"""Configuration settings for the feedback application."""

import os
from typing import Final

# Application Configuration
SECRET_KEY: Final[str] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
DEBUG: Final[bool] = os.environ.get('DEBUG', 'True').lower() == 'true'
HOST: Final[str] = os.environ.get('HOST', '0.0.0.0')
PORT: Final[int] = int(os.environ.get('PORT', '5001'))

# Database Configuration  
DATABASE_PATH: Final[str] = os.environ.get('DATABASE_PATH', 'feedback.db')

# Date/Time Configuration
TIMESTAMP_FORMAT: Final[str] = '%Y-%m-%d %H:%M:%S'

# Flash Message Constants
class Messages:
    """Flash message constants."""
    FEEDBACK_CREATED: Final[str] = 'Feedback created successfully!'
    FEEDBACK_UPDATED: Final[str] = 'Feedback updated successfully!'
    FEEDBACK_DELETED: Final[str] = 'Feedback deleted successfully!'
    FEEDBACK_NOT_FOUND: Final[str] = 'Feedback not found!'
    FIELDS_REQUIRED: Final[str] = 'Both user and comment fields are needed!'
    CREATE_ERROR: Final[str] = 'Error creating feedback. Please try again.'
    UPDATE_ERROR: Final[str] = 'Error updating feedback. Please try again.'
    DELETE_ERROR: Final[str] = 'Error deleting feedback. Please try again.'

# Flash Message Categories
class MessageCategories:
    """Flash message category constants."""
    SUCCESS: Final[str] = 'success'
    ERROR: Final[str] = 'error'
