"""Health check utilities for Jira agent"""
import json
from typing import Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class HealthStatus:
    """Health check status"""
    config: bool = False
    api_connectivity: bool = False
    authentication: bool = False
    permissions: bool = False
    
    @property
    def is_healthy(self) -> bool:
        """Check if all components are healthy"""
        return all([self.config, self.api_connectivity, self.authentication])
    
    @property
    def status_emoji(self) -> str:
        """Get emoji representation of health"""
        return "✅" if self.is_healthy else "⛔"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)


def perform_health_check() -> HealthStatus:
    """
    Perform comprehensive health check.
    
    Returns:
        HealthStatus object with results
    """
    from .config import JiraConfig
    from .client import JiraClient
    
    status = HealthStatus()
    
    # 1. Check Configuration
    try:
        status.config = JiraConfig.is_configured()
    except Exception:
        status.config = False
    
    # If config fails, no point checking the rest
    if not status.config:
        return status
    
    # 2. Check API Connectivity
    try:
        client = JiraClient()
        # Try to get server info
        info = client.jira.server_info()
        status.api_connectivity = bool(info)
    except Exception:
        status.api_connectivity = False
        return status  # Can't continue without connectivity
    
    # 3. Check Authentication
    try:
        # Try to get current user
        user = client.jira.current_user()
        status.authentication = bool(user)
    except Exception:
        status.authentication = False
        return status
    
    # 4. Check Permissions (optional, won't fail health check)
    try:
        # Try to search for issues (basic permission)
        client.jira.search_issues('PROJECT is not EMPTY', maxResults=1)
        status.permissions = True
    except Exception:
        status.permissions = False
    
    return status


def format_health_report(status: HealthStatus) -> str:
    """
    Format health check results for display.
    
    Args:
        status: HealthStatus object
    
    Returns:
        Formatted health report string
    """
    report = [
        f"{status.status_emoji} **Protonion Jira Agent Health Check**",
        "",
        f"Overall Status: {'HEALTHY' if status.is_healthy else 'UNHEALTHY'}",
        "",
        "Component Status:",
        f"  {'✅' if status.config else '❌'} Configuration",
        f"  {'✅' if status.api_connectivity else '❌'} API Connectivity",
        f"  {'✅' if status.authentication else '❌'} Authentication",
        f"  {'✅' if status.permissions else '⚠️'} Permissions (optional)",
    ]
    
    # Add troubleshooting tips if unhealthy
    if not status.is_healthy:
        report.extend([
            "",
            "💡 Troubleshooting:",
        ])
        
        if not status.config:
            report.append("  - Check that JIRA_URL, JIRA_USER, and JIRA_API_TOKEN are set")
        
        if not status.api_connectivity:
            report.append("  - Verify network connection to Jira server")
            report.append("  - Check that JIRA_URL is correct")
        
        if not status.authentication:
            report.append("  - Verify JIRA_USER and JIRA_API_TOKEN are correct")
            report.append("  - Check that the token hasn't expired")
    
    return "\n".join(report)
