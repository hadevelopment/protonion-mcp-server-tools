
from mcp.server.fastmcp import FastMCP
from typing import Optional
import os
from dotenv import load_dotenv

# 1. Cargar entorno (buscando en raíz)
load_dotenv()

# 2. Importar Lógica Modular
from src.services.jira_service import JiraClient
from src.core.config import JiraConfig
from src.core.jira_validators import (
    validate_issue_key,
    validate_status,
    validate_board_id
)
from src.core.validators import (
    validate_limit,
    ValidationError
)
from src.core.cache import get_singleton_client

# 3. Inicializar Servidor MCP "Protonion MCP Jira"
mcp = FastMCP("Protonion MCP Jira")

def get_client():
    """Helper para obtener cliente singleton"""
    if not JiraConfig.is_configured():
        raise ValueError("Jira credentials not configured")
    # Nota: get_singleton_client usa JiraClient internamente
    return get_singleton_client()

# --- HERRAMIENTAS DE JIRA ---

@mcp.tool()
def list_my_tasks(board_id: int = 67, limit: int = 10) -> str:
    """📋 My Tasks - Show all pending tasks assigned to you on the current board"""
    try:
        board_id = validate_board_id(board_id)
        limit = validate_limit(limit, max_limit=100)
        
        client = get_client()
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
    except ValidationError as e:
        return f"⛔ Validation Error: {str(e)}"
    except Exception as e:
        return f"System Error: {str(e)}"

@mcp.tool()
def inspect_task(issue_key: str) -> str:
    """🔍 View Task Details - Get a comprehensive summary including status, assignee, and comments"""
    try:
        issue_key = validate_issue_key(issue_key)
        client = get_client()
        digest = client.get_issue_digest(issue_key)
        
        return (
            f"🆔 {digest['key']} | {digest['status']} | {digest['priority']}\n"
            f"👤 Assigned: {digest['assignee']}\n"
            f"📝 Summary: {digest['summary']}\n"
            f"📄 Desc Snippet: {digest['description_snippet']}\n"
            f"💬 Last Comment: {digest['last_comment']}"
        )
    except ValidationError as e:
        return f"⛔ Validation Error: {str(e)}"
    except Exception as e:
        return f"System Error: {str(e)}"

@mcp.tool()
def safe_move_task(issue_key: str, target_status: str, comment: Optional[str] = None) -> str:
    """🔄 Move Task - Transition a task with workflow validation and optional comment"""
    try:
        issue_key = validate_issue_key(issue_key)
        target_status = validate_status(target_status)
        
        client = get_client()
        if comment:
            client.add_comment(issue_key, f"🤖 [Agent]: {comment}")
            
        result = client.safe_transition(issue_key, target_status)
        
        if result["success"]:
            return f"✅ {result['message']}"
        else:
            return (
                f"⛔ BLOCKER: {result['message']}\n"
                f"💡 Valid transitions: {result.get('valid_transitions', [])}"
            )
    except ValidationError as e:
        return f"⛔ Validation Error: {str(e)}"
    except Exception as e:
        return f"System Error: {str(e)}"

@mcp.tool()
def create_task(summary: str, description: str, issue_type: str = "Task") -> str:
    """✨ Create New Task - Add a new task to your Jira board"""
    try:
        client = get_client()
        resp = client.create_issue(summary, description, issue_type=issue_type)
        return f"✅ Created task {resp.get('key')}: {summary}"
    except Exception as e:
        return f"Error creating task: {str(e)}"

@mcp.tool()
def search_colleague(name: str) -> str:
    """👥 Find Team Member - Search for colleagues by name to get their ID"""
    try:
        client = get_client()
        user = client.fuzzy_user_search(name)
        if user:
            return f"Found: {user['displayName']} (ID: {user['accountId']})"
        return f"No active user found matching '{name}'"
    except Exception as e:
        return f"Search Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
