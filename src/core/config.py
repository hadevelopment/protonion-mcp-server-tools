"""
Jira Integration Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

class JiraConfig:
    """Configuration for Jira integration"""
    BASE_URL = os.getenv("JIRA_BASE_URL", "https://ukambas-team.atlassian.net").strip()
    EMAIL = os.getenv("JIRA_EMAIL", "").strip()
    API_TOKEN = os.getenv("JIRA_API_TOKEN", "").strip()
    PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "CRM").strip()
    
    # API endpoints
    API_VERSION = "3"
    API_BASE = f"{BASE_URL}/rest/api/{API_VERSION}"
    AGILE_API_BASE = f"{BASE_URL}/rest/agile/1.0"
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if Jira is properly configured"""
        return bool(cls.EMAIL and cls.API_TOKEN)
    
    @classmethod
    def get_auth(cls) -> tuple:
        """Return authentication tuple for requests"""
        return (cls.EMAIL, cls.API_TOKEN)
