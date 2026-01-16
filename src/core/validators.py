"""Input validation utilities for Jira agent"""
import re
from typing import Optional


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_issue_key(issue_key: str) -> str:
    """
    Validate and sanitize Jira issue key.
    
    Args:
        issue_key: The issue key to validate (e.g., 'CRM-123')
    
    Returns:
        Sanitized issue key
    
    Raises:
        ValidationError: If the issue key format is invalid
    """
    if not issue_key or not isinstance(issue_key, str):
        raise ValidationError("Issue key must be a non-empty string")
    
    # Remove whitespace
    issue_key = issue_key.strip()
    
    # Validate format: PROJECT-NUMBER
    # Project: 1-10 uppercase letters
    # Number: 1-10 digits
    pattern = r'^[A-Z]{1,10}-\d{1,10}$'
    
    if not re.match(pattern, issue_key):
        raise ValidationError(
            f"Invalid issue key format: '{issue_key}'. "
            f"Expected format: PROJECT-NUMBER (e.g., 'CRM-123')"
        )
    
    return issue_key


def validate_status(status: str) -> str:
    """
    Validate and sanitize status name.
    
    Args:
        status: The status to validate
    
    Returns:
        Sanitized status
    
    Raises:
        ValidationError: If the status is invalid
    """
    if not status or not isinstance(status, str):
        raise ValidationError("Status must be a non-empty string")
    
    status = status.strip()
    
    # Status should be alphanumeric + spaces, max 50 chars
    if len(status) > 50:
        raise ValidationError(f"Status name too long (max 50 chars): '{status}'")
    
    if not re.match(r'^[a-zA-Z0-9\s]+$', status):
        raise ValidationError(
            f"Invalid status format: '{status}'. "
            f"Only alphanumeric characters and spaces allowed"
        )
    
    return status


def validate_board_id(board_id: int) -> int:
    """
    Validate board ID.
    
    Args:
        board_id: The board ID to validate
    
    Returns:
        Validated board ID
    
    Raises:
        ValidationError: If the board ID is invalid
    """
    if not isinstance(board_id, int):
        raise ValidationError(f"Board ID must be an integer, got {type(board_id)}")
    
    if board_id < 1:
        raise ValidationError(f"Board ID must be positive, got {board_id}")
    
    return board_id


def validate_limit(limit: int, max_limit: int = 100) -> int:
    """
    Validate pagination limit.
    
    Args:
        limit: The limit to validate
        max_limit: Maximum allowed limit
    
    Returns:
        Validated limit
    
    Raises:
        ValidationError: If the limit is invalid
    """
    if not isinstance(limit, int):
        raise ValidationError(f"Limit must be an integer, got {type(limit)}")
    
    if limit < 1:
        raise ValidationError(f"Limit must be at least 1, got {limit}")
    
    if limit > max_limit:
        raise ValidationError(f"Limit cannot exceed {max_limit}, got {limit}")
    
    return limit
