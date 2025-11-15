"""Validation utilities for the feedback application."""

from typing import Tuple, List


def validate_feedback_data(user: str, comment: str) -> Tuple[bool, List[str]]:
    """Validate feedback data.
    
    Args:
        user: User name input
        comment: Comment input
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if not user or not user.strip():
        errors.append("User field is required")
    
    if not comment or not comment.strip():
        errors.append("Comment field is required")
    
    return len(errors) == 0, errors


def sanitize_input(text: str) -> str:
    """Sanitize input text by getting rid of whitespace.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text
    """
    return text.strip() if text else ""
