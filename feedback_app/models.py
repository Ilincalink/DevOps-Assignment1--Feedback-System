
import sqlite3
from datetime import datetime
import logging
from typing import Optional, List, Dict, Any

from config import DATABASE_PATH, TIMESTAMP_FORMAT

# Configure logging
logger = logging.getLogger(__name__)


class FeedbackModel:
    """Model class for handling feedback database operations."""
    
    def __init__(self, db_path: str = DATABASE_PATH) -> None:
        """Initialize feedback model with database path.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize the database and create feedback table if not exists."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user TEXT NOT NULL,
                        comment TEXT NOT NULL,
                        timestamp TEXT NOT NULL
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            # Do not re-raise - allow the model to be constructed even if the
            # database cannot be opened. Individual operations handle errors
            # and will return False/empty results as expected by tests.
            return
    
    def create(self, data: Dict[str, str]) -> bool:
        """Create new feedback entry.
        
        Args:
            data: Dictionary with 'user' and 'comment' keys
            
        Returns:
            True if successful, False otherwise
        """
        try:
            timestamp = self._get_current_timestamp()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO feedback (user, comment, timestamp)
                    VALUES (?, ?, ?)
                ''', (data['user'], data['comment'], timestamp))
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error creating feedback: {e}")
            return False
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp as formatted string.
        
        Returns:
            Formatted timestamp string
        """
        return datetime.now().strftime(TIMESTAMP_FORMAT)
    
    def read_all(self) -> List[Dict[str, Any]]:
        """Read all feedback entries from the database.
        
        Returns:
            List of dictionaries containing feedback data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Access columns by name
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, user, comment, timestamp
                    FROM feedback
                    ORDER BY timestamp DESC
                ''')
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                return [dict(row) for row in rows]
                
        except sqlite3.Error as e:
            logger.error(f"Error reading feedback: {e}")
            return []
    
    def get_by_id(self, feedback_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific feedback entry by ID.
        
        Args:
            feedback_id: The ID of the feedback entry
            
        Returns:
            Dictionary containing feedback data or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, user, comment, timestamp
                    FROM feedback
                    WHERE id = ?
                ''', (feedback_id,))
                row = cursor.fetchone()
                
                return dict(row) if row else None
                
        except sqlite3.Error as e:
            logger.error(f"Error getting feedback by ID: {e}")
            return None
    
    def update(self, feedback_id: int, data: Dict[str, str]) -> bool:
        """Update an existing feedback entry.
        
        Args:
            feedback_id: The ID of the feedback to update
            data: Dictionary with 'user' and 'comment' keys
            
        Returns:
            True if successful, False otherwise
        """
        try:
            timestamp = self._get_current_timestamp()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE feedback
                    SET user = ?, comment = ?, timestamp = ?
                    WHERE id = ?
                ''', (data['user'], data['comment'], timestamp, feedback_id))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    return True
                return False
                
        except sqlite3.Error as e:
            logger.error(f"Error updating feedback: {e}")
            return False
    
    def delete(self, feedback_id: int) -> bool:
        """Delete a feedback entry.
        
        Args:
            feedback_id: The ID of the feedback to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM feedback WHERE id = ?', (feedback_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    return True
                return False
                
        except sqlite3.Error as e:
            logger.error(f"Error deleting feedback: {e}")
            return False
