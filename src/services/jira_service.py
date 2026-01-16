"""
Jira API Client with Clean Architecture Principles
"""
import requests
from typing import Dict, List, Optional, Any
from src.core.config import JiraConfig
# from src.core.models import IssueDigest, IssueTransition # Comentamos modelos si no existen aun

class JiraClient:
    """Client for interacting with Jira API"""
    
    def __init__(self):
        self.config = JiraConfig
        self.session = requests.Session()
        self.session.auth = self.config.get_auth()
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """Make a request to Jira API"""
        url = f"{self.config.API_BASE}/{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params
            )
            # Jira specific error handling
            if response.status_code == 400:
                print(f"Jira Validation Error: {response.text}")
            elif response.status_code == 404:
                print(f"Jira Resource Not Found: {url}")
                
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            print(f"Jira API Error: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise
    
    # --- Clean Architecture / Robust Methods ---

    def get_issue_digest(self, issue_key: str) -> Dict:
        """Get a curated, token-efficient summary of an issue"""
        issue = self.get_issue(issue_key)
        fields = issue.get("fields", {})
        
        # Extract text from Atlassian Doc format if possible user helper
        description = "No description"
        desc_raw = fields.get("description")
        if desc_raw and isinstance(desc_raw, dict):
            # Very naive extraction of text from ADF
            content = desc_raw.get("content", [])
            if content and len(content) > 0:
                text_parts = []
                for p in content:
                     if p.get("type") == "paragraph":
                         for node in p.get("content", []):
                             if node.get("type") == "text":
                                 text_parts.append(node.get("text", ""))
                description = " ".join(text_parts)[:300] + "..." if text_parts else "Complex content"
        elif isinstance(desc_raw, str):
            description = desc_raw[:300]

        comments_data = fields.get("comment", {}).get("comments", [])
        last_comment = None
        if comments_data:
            last_body = comments_data[-1].get("body", {})
            # Naive extraction again
            try:
                # Try to get text from ADF
                last_comment = "Rich Text Comment" # Placeholder implementation for complex ADF
                if isinstance(last_body, dict) and "content" in last_body:
                     content = last_body["content"][0]["content"][0]["text"]
                     last_comment = content
                elif isinstance(last_body, str):
                    last_comment = last_body
            except:
                last_comment = "Rich text comment (could not parse)"

        return {
            "key": issue.get("key"),
            "summary": fields.get("summary"),
            "status": fields.get("status", {}).get("name"),
            "priority": fields.get("priority", {}).get("name"),
            "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else "Unassigned",
            "description_snippet": description,
            "comments_count": fields.get("comment", {}).get("total", 0),
            "last_comment": last_comment
        }

    def safe_transition(self, issue_key: str, target_status: str) -> Dict:
        """
        Robust transition that validates workflow first.
        Returns detailed success or failure context.
        """
        # 1. Introspection: Get legal transitions
        try:
            transitions_resp = self._make_request("GET", f"issue/{issue_key}/transitions")
        except Exception:
            return {"success": False, "error": "Issue Not Found or No Permission"}

        available_transitions = transitions_resp.get("transitions", [])
        
        # 2. Validation
        target_normalized = target_status.lower().strip()
        matching_trans = None
        
        valid_names = []
        for t in available_transitions:
            t_name = t["to"]["name"]
            valid_names.append(t_name)
            if t_name.lower() == target_normalized:
                matching_trans = t
                break
        
        if not matching_trans:
            return {
                "success": False,
                "error": "Invalid Transition",
                "message": f"Cannot move '{issue_key}' to '{target_status}'. Legal transitions are: {', '.join(valid_names)}",
                "valid_transitions": valid_names
            }
            
        # 3. Execution (Atomic)
        data = {"transition": {"id": matching_trans["id"]}}
        try:
            self._make_request("POST", f"issue/{issue_key}/transitions", data=data)
            return {
                "success": True,
                "message": f"Successfully moved '{issue_key}' to '{matching_trans['to']['name']}'",
                "new_status": matching_trans['to']['name']
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Execution Error",
                "message": str(e)
            }

    def fuzzy_user_search(self, name_query: str) ->  Optional[Dict]:
        """Resolve a name (e.g. 'Hector') to a Jira Account ID"""
        users = self.search_users(name_query)
        if not users:
            return None
        
        # Best match logic
        for user in users:
            if user.get("accountType") == "atlassian" and user.get("active"):
                return {
                    "accountId": user.get("accountId"),
                    "displayName": user.get("displayName"),
                    "email": user.get("emailAddress", "Hidden")
                }
        return None

    # --- Standard Methods ---
    
    def get_project(self, project_key: Optional[str] = None) -> Dict:
        """Get project information"""
        key = project_key or self.config.PROJECT_KEY
        return self._make_request("GET", f"project/{key}")
    
    def get_board_issues(self, board_id: int, jql: Optional[str] = None) -> List[Dict]:
        """Get issues from a specific board using Agile API"""
        url = f"{self.config.AGILE_API_BASE}/board/{board_id}/issue"
        params = {}
        if jql:
            params["jql"] = jql
            
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json().get("issues", [])
        except requests.exceptions.RequestException as e:
            print(f"Jira Agile API Error: {e}")
            return []

    def get_issues(self, project_key: Optional[str] = None, jql: Optional[str] = None, max_results: int = 50) -> List[Dict]:
        key = project_key or self.config.PROJECT_KEY
        if not jql:
            jql = f"project = {key} ORDER BY created DESC"
        
        # Update for new Jira API constraints: Use POST to search/jql
        payload = {
            "jql": jql,
            "maxResults": max_results,
            "fields": ["summary", "status", "assignee", "priority", "created", "updated", "description", "issuetype", "comment"]
        }
        
        # Ensure we use search/jql endpoint which is replacing standard search in some tenants
        result = self._make_request("POST", "search/jql", data=payload)
        return result.get("issues", [])
    
    def get_issue(self, issue_key: str) -> Dict:
        return self._make_request("GET", f"issue/{issue_key}")
    
    def create_issue(self, summary: str, description: str, issue_type: str = "Task", project_key: Optional[str] = None, priority: Optional[str] = None, assignee: Optional[str] = None) -> Dict:
        key = project_key or self.config.PROJECT_KEY
        
        fields = {
            "project": {"key": key},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]
            },
            "issuetype": {"name": issue_type}
        }
        
        if priority:
            fields["priority"] = {"name": priority}
        if assignee:
            fields["assignee"] = {"accountId": assignee}
            
        data = {"fields": fields}
        return self._make_request("POST", "issue", data=data)
        
    def add_comment(self, issue_key: str, comment: str) -> Dict:
        data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}]
            }
        }
        return self._make_request("POST", f"issue/{issue_key}/comment", data=data)
    
    def transition_issue(self, issue_key: str, status_name: str) -> Dict:
        # Legacy method kept for backward compatibility, usage of safe_transition is preferred
        return self.safe_transition(issue_key, status_name)

    def search_users(self, query: str, max_results: int = 10) -> List[Dict]:
        params = {"query": query, "maxResults": max_results}
        return self._make_request("GET", "user/search", params=params)
