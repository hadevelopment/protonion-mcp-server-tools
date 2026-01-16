"""Tests for Jira agent MCP server"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.jira_tools.validators import (
    validate_issue_key,
    validate_status,
    validate_board_id,
    validate_limit,
    ValidationError
)


class TestValidators:
    """Test input validation"""
    
    def test_validate_issue_key_valid(self):
        """Test valid issue keys"""
        assert validate_issue_key("CRM-123") == "CRM-123"
        assert validate_issue_key("PROJECT-1") == "PROJECT-1"
        assert validate_issue_key(" CRM-456 ") == "CRM-456"  # Trimmed
    
    def test_validate_issue_key_invalid(self):
        """Test invalid issue keys"""
        with pytest.raises(ValidationError, match="must be a non-empty string"):
            validate_issue_key("")
        
        with pytest.raises(ValidationError, match="Invalid issue key format"):
            validate_issue_key("CRM")  # No number
        
        with pytest.raises(ValidationError, match="Invalid issue key format"):
            validate_issue_key("123")  # No project
        
        with pytest.raises(ValidationError, match="Invalid issue key format"):
            validate_issue_key("crm-123")  # Lowercase
    
    def test_validate_status_valid(self):
        """Test valid statuses"""
        assert validate_status("In Progress") == "In Progress"
        assert validate_status("Done") == "Done"
        assert validate_status(" To Do ") == "To Do"  # Trimmed
    
    def test_validate_status_invalid(self):
        """Test invalid statuses"""
        with pytest.raises(ValidationError, match="must be a non-empty string"):
            validate_status("")
        
        with pytest.raises(ValidationError, match="Invalid status format"):
            validate_status("Done!")  # Special char
        
        with pytest.raises(ValidationError, match="too long"):
            validate_status("A" * 51)  # Too long
    
    def test_validate_board_id_valid(self):
        """Test valid board IDs"""
        assert validate_board_id(67) == 67
        assert validate_board_id(1) == 1
        assert validate_board_id(9999) == 9999
    
    def test_validate_board_id_invalid(self):
        """Test invalid board IDs"""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_board_id("67")
        
        with pytest.raises(ValidationError, match="must be positive"):
            validate_board_id(0)
        
        with pytest.raises(ValidationError, match="must be positive"):
            validate_board_id(-1)
    
    def test_validate_limit_valid(self):
        """Test valid limits"""
        assert validate_limit(10) == 10
        assert validate_limit(1) == 1
        assert validate_limit(100) == 100
    
    def test_validate_limit_invalid(self):
        """Test invalid limits"""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_limit("10")
        
        with pytest.raises(ValidationError, match="must be at least 1"):
            validate_limit(0)
        
        with pytest.raises(ValidationError, match="cannot exceed"):
            validate_limit(101)


class TestCaching:
    """Test caching functionality"""
    
    def test_ttl_cache(self):
        """Test TTL cache"""
        from src.jira_tools.cache import TTLCache
        
        cache = TTLCache(ttl_seconds=1)
        
        # Set and get
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Not expired
        assert "key1" in cache
        
        # Clear
        cache.clear()
        assert cache.get("key1") is None
    
    def test_ttl_cache_expiration(self):
        """Test TTL cache expiration"""
        import time
        from src.jira_tools.cache import TTLCache
        
        cache = TTLCache(ttl_seconds=0.1)  # 100ms TTL
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Should be expired
        assert cache.get("key1") is None


class TestHealthCheck:
    """Test health check functionality"""
    
    def test_health_status_healthy(self):
        """Test healthy status"""
        from src.jira_tools.healthcheck import HealthStatus
        
        status = HealthStatus(
            config=True,
            api_connectivity=True,
            authentication=True,
            permissions=True
        )
        
        assert status.is_healthy is True
        assert status.status_emoji == "✅"
    
    def test_health_status_unhealthy(self):
        """Test unhealthy status"""
        from src.jira_tools.healthcheck import HealthStatus
        
        status = HealthStatus(
            config=False,
            api_connectivity=False,
            authentication=False
        )
        
        assert status.is_healthy is False
        assert status.status_emoji == "⛔"
    
    def test_format_health_report(self):
        """Test health report formatting"""
        from src.jira_tools.healthcheck import HealthStatus, format_health_report
        
        status = HealthStatus(
            config=True,
            api_connectivity=True,
            authentication=True
        )
        
        report = format_health_report(status)
        
        assert "HEALTHY" in report
        assert "✅" in report


# FastMCP Integration Tests (require FastMCP to be installed)
# TODO: Update these tests with correct FastMCP test API once available
# @pytest.mark.asyncio
# @pytest.mark.skipif("SKIP_INTEGRATION" in os.environ, reason="Integration tests skipped")
# class TestMCPServer:
#     """Test MCP server tools"""
#     
#     async def test_ping(self):
#         """Test ping/healthcheck tool"""
#         pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
