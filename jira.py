#!/usr/bin/env python3
"""
Protonion MCP Jira Agent - Standalone Version
Simple, robust, and portable
"""
import os
from pathlib import Path
from dotenv import load_dotenv, set_key
from mcp.server.fastmcp import FastMCP
import requests
from typing import Dict, List

# Load environment
load_dotenv()

# Configuration
JIRA_URL = os.getenv("JIRA_URL", "https://ukambas-team.atlassian.net")
JIRA_USER = os.getenv("JIRA_USER", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "CRM")

# Initialize FastMCP
mcp = FastMCP(
    "protonion",
    instructions="""
# 🚀 Protonion Jira Agent
**Professional Jira Integration for Antigravity**

This agent provides a complete suite of tools to manage your Jira workflow without leaving your editor.

### 🌟 Key Capabilities
*   **Task Management**: Create, list, search, and inspect issues.
*   **Workflow Automation**: Transitions tasks safely with validation.
*   **Team Collaboration**: Find teammates and assign tasks.
*   **Configuration**: Zero-config setup with UI-based credential management.

### 🛠️ Setup
Use the `update_config` tool to set your Jira URL, Email, and API Token.
    """
)

@mcp.resource("protonion://readme")
def get_readme() -> str:
    """📄 About Protonion Jira"""
    return """
# 🚀 Protonion Jira Agent

Professional Jira integration for high-performance teams.

### Features
- 📋 **Task Management**: List, create, and inspect tasks
- 🔄 **Workflow**: Move tasks securely between statuses
- 👥 **Team**: Find colleagues instantly
- ⚙️ **Configurable**: Manage credentials directly from the UI

*Powered by Antigravity & Protonion Framework*
"""


class JiraClient:
    """Simple Jira API client"""
    
    def __init__(self):
        self.base_url = JIRA_URL.rstrip('/')
        self.session = requests.Session()
        self.session.auth = (JIRA_USER, JIRA_API_TOKEN)
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make API request"""
        url = f"{self.base_url}/rest/api/3/{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except Exception as e:
            raise Exception(f"Jira API Error: {str(e)}")
    
    def get_board_issues(self, board_id: int, jql: str = None) -> List[Dict]:
        """Get issues from board"""
        url = f"{self.base_url}/rest/agile/1.0/board/{board_id}/issue"
        params = {"jql": jql} if jql else {}
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json().get("issues", [])
        except:
            return []
    
    def get_issue(self, issue_key: str) -> Dict:
        """Get issue details"""
        return self._request("GET", f"issue/{issue_key}")
    
    def search_issues(self, jql: str, max_results: int = 50) -> List[Dict]:
        """Search issues"""
        params = {
            "jql": jql,
            "maxResults": max_results,
            "fields": "summary,status,assignee,priority,created"
        }
        result = self._request("GET", "search", params=params)
        return result.get("issues", [])
    
    def get_transitions(self, issue_key: str) -> List[Dict]:
        """Get available transitions"""
        result = self._request("GET", f"issue/{issue_key}/transitions")
        return result.get("transitions", [])
    
    def transition_issue(self, issue_key: str, transition_id: str) -> None:
        """Transition issue"""
        data = {"transition": {"id": transition_id}}
        self._request("POST", f"issue/{issue_key}/transitions", json=data)
    
    def create_issue(self, summary: str, description: str, issue_type: str = "Task") -> Dict:
        """Create new issue"""
        data = {
            "fields": {
                "project": {"key": JIRA_PROJECT_KEY},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}]
                    }]
                },
                "issuetype": {"name": issue_type}
            }
        }
        return self._request("POST", "issue", json=data)
    
    def add_comment(self, issue_key: str, comment: str) -> Dict:
        """Add comment to issue"""
        data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": comment}]
                }]
            }
        }
        return self._request("POST", f"issue/{issue_key}/comment", json=data)
    
    def search_users(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search users"""
        params = {"query": query, "maxResults": max_results}
        return self._request("GET", "user/search", params=params)


# Global client instance
client = JiraClient()


@mcp.tool()
def list_my_tasks(board_id: int = 67, limit: int = 10) -> str:
    """📋 My Tasks - Show all pending tasks assigned to you"""
    try:
        jql = "assignee = currentUser() AND statusCategory != Done"
        issues = client.get_board_issues(board_id=board_id, jql=jql)
        
        if not issues:
            return "No pending tasks found."
        
        result = [f"📋 PENDING TASKS (Board {board_id}):"]
        for issue in issues[:limit]:
            key = issue.get("key")
            summary = issue.get("fields", {}).get("summary")
            status = issue.get("fields", {}).get("status", {}).get("name")
            result.append(f"- [{key}] {summary} ({status})")
        
        return "\n".join(result)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def inspect_task(issue_key: str) -> str:
    """🔍 View Task Details - Get comprehensive task information"""
    try:
        issue = client.get_issue(issue_key)
        fields = issue.get("fields", {})
        
        status = fields.get("status", {}).get("name", "Unknown")
        priority = fields.get("priority", {}).get("name", "None")
        assignee = fields.get("assignee", {}).get("displayName", "Unassigned")
        summary = fields.get("summary", "No summary")
        
        # Get description
        desc_raw = fields.get("description", {})
        description = "No description"
        if isinstance(desc_raw, dict) and "content" in desc_raw:
            try:
                text_parts = []
                for block in desc_raw.get("content", []):
                    if block.get("type") == "paragraph":
                        for node in block.get("content", []):
                            if node.get("type") == "text":
                                text_parts.append(node.get("text", ""))
                if text_parts:
                    description = " ".join(text_parts)[:200]
            except:
                description = "Rich text content"
        
        return (
            f"🆔 {issue_key} | {status} | {priority}\n"
            f"👤 Assigned: {assignee}\n"
            f"📝 Summary: {summary}\n"
            f"📄 Description: {description}"
        )
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def safe_move_task(issue_key: str, target_status: str, comment: str = None) -> str:
    """🔄 Move Task - Transition task with workflow validation"""
    try:
        # Get available transitions
        transitions = client.get_transitions(issue_key)
        
        # Find matching transition
        target_normalized = target_status.lower().strip()
        matching_trans = None
        valid_names = []
        
        for trans in transitions:
            t_name = trans["to"]["name"]
            valid_names.append(t_name)
            if t_name.lower() == target_normalized:
                matching_trans = trans
                break
        
        if not matching_trans:
            return (
                f"⛔ Cannot move '{issue_key}' to '{target_status}'.\n"
                f"💡 Valid transitions: {', '.join(valid_names)}"
            )
        
        # Add comment if provided
        if comment:
            client.add_comment(issue_key, f"🤖 [Agent]: {comment}")
        
        # Perform transition
        client.transition_issue(issue_key, matching_trans["id"])
        
        return f"✅ Successfully moved '{issue_key}' to '{matching_trans['to']['name']}'"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def create_task(summary: str, description: str, issue_type: str = "Task") -> str:
    """✨ Create New Task - Add a task to your Jira board"""
    try:
        response = client.create_issue(summary, description, issue_type)
        key = response.get("key", "Unknown")
        return f"✅ Created task {key}: {summary}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def search_colleague(name: str) -> str:
    """👥 Find Team Member - Search for colleagues by name"""
    try:
        users = client.search_users(name)
        if not users:
            return f"No active user found matching '{name}'"
        
        # Return first active user
        for user in users:
            if user.get("accountType") == "atlassian" and user.get("active"):
                return f"Found: {user['displayName']} (ID: {user['accountId']})"
        
        return f"No active user found matching '{name}'"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def show_config() -> str:
    """⚙️ Show Configuration - Display current Jira settings (tokens masked)"""
    def mask_token(value: str) -> str:
        if not value or len(value) < 8:
            return "***"
        return f"{value[:4]}...{value[-4:]}"
    
    return (
        f"🔧 **Jira Configuration:**\n"
        f"- JIRA_URL: {JIRA_URL}\n"
        f"- JIRA_USER: {JIRA_USER or '(not set)'}\n"
        f"- JIRA_API_TOKEN: {mask_token(JIRA_API_TOKEN) if JIRA_API_TOKEN else '(not set)'}\n"
        f"- JIRA_PROJECT_KEY: {JIRA_PROJECT_KEY}\n\n"
        f"💡 Use `update_config` to change these values"
    )


@mcp.tool()
def update_config(jira_url: str = None, jira_user: str = None, jira_api_token: str = None, jira_project_key: str = None) -> str:
    """🔐 Update Configuration - Set Jira credentials and settings"""
    try:
        # Find .env file
        env_path = Path(__file__).parent / ".env"
        
        # Create .env if it doesn't exist
        if not env_path.exists():
            env_path.write_text("# Jira Configuration\n")
        
        updated = []
        
        if jira_url:
            set_key(env_path, "JIRA_URL", jira_url)
            updated.append("JIRA_URL")
        
        if jira_user:
            set_key(env_path, "JIRA_USER", jira_user)
            updated.append("JIRA_USER")
        
        if jira_api_token:
            set_key(env_path, "JIRA_API_TOKEN", jira_api_token)
            updated.append("JIRA_API_TOKEN")
        
        if jira_project_key:
            set_key(env_path, "JIRA_PROJECT_KEY", jira_project_key)
            updated.append("JIRA_PROJECT_KEY")
        
        if not updated:
            return "⚠️ No values provided to update. Specify at least one parameter."
        
        return (
            f"✅ Configuration updated: {', '.join(updated)}\n\n"
            f"⚠️ **Important:** You must restart Antigravity for changes to take effect."
        )
    except Exception as e:
        return f"Error updating config: {str(e)}"


if __name__ == "__main__":
    mcp.run()

