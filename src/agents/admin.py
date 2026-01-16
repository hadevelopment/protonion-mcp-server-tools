
from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
from src.jira_tools.healthcheck import perform_health_check, format_health_report
from src.jira_tools.config import JiraConfig

load_dotenv()

# Servidor MCP para Administración de Sistemas
mcp = FastMCP("Protonion Admin")

@mcp.tool()
def health_check() -> str:
    """🩺 System Status - Check connectivity and health of all Protonion services"""
    status = perform_health_check()
    return format_health_report(status)

@mcp.tool()
def show_environment() -> str:
    """⚙️ Environment - Show status of environment variables (masked)"""
    def mask(v): return f"{v[:4]}***" if v else "Not set"
    
    report = [
        "🌍 **Current Environment Status:**",
        f"- JIRA_URL: {os.getenv('JIRA_URL', 'Not set')}",
        f"- JIRA_USER: {os.getenv('JIRA_USER', 'Not set')}",
        f"- JIRA_TOKEN: {mask(os.getenv('JIRA_API_TOKEN'))}",
        f"- ENV: {os.getenv('ENV', 'dev')}"
    ]
    return "\n".join(report)

if __name__ == "__main__":
    mcp.run()
