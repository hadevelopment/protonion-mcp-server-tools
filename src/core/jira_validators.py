
import re
from .validators import ValidationError

def validate_issue_key(issue_key: str) -> str:
    """Valida formato CRM-123"""
    if not issue_key or not isinstance(issue_key, str):
        raise ValidationError("Issue key must be a non-empty string")
    
    issue_key = issue_key.strip().upper()
    pattern = r'^[A-Z]{2,10}-\d{1,10}$'
    
    if not re.match(pattern, issue_key):
        raise ValidationError(f"Invalid issue key format: '{issue_key}'. Expected PROJECT-NUMBER (e.g. CRM-123)")
    return issue_key

def validate_status(status: str) -> str:
    """Sanitiza nombre de status"""
    if not status or not isinstance(status, str):
        raise ValidationError("Status must be a string")
    return status.strip()

def validate_board_id(board_id: Any) -> int:
    """Valida ID de tablero"""
    try:
        val = int(board_id)
        if val <= 0: raise ValueError()
        return val
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid Board ID: {board_id}. Must be a positive integer.")
