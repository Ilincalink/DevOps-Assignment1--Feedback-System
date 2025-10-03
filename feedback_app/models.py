
import sqlite3
from datetime import datetime
import os
#tried using Docstrings for methods and classes for the first time. hopefully they are readable and useful

class FeedbackModel:
    """Model class- handling feedback database operations."""
    
    def __init__(self, db_path='feedback.db'):
        """Init feedback model with database path."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initiallise the database and create feedback table if not already there."""
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
            print(f"Database initialisation error: {e}")
    
    def create(self, data):
        """
        Create new feedback entry.
        
        Args:data (dict): Dictionary with 'user' and 'comment' keys
            
        Returns:bool: True if successful, False otherwise
        """
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO feedback (user, comment, timestamp)
                    VALUES (?, ?, ?)
                ''', (data['user'], data['comment'], timestamp))
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            print(f"Error creating feedback: {e}")
            return False
    
    def read_all(self):
        """
        Read all feedback entries from the dbse.
        
        Returns a list of dictionaries containing feedback data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  #access cols by name
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, user, comment, timestamp
                    FROM feedback
                    ORDER BY timestamp DESC
                ''')
                rows = cursor.fetchall()
                
                # convert to list of dictionaries
                return [dict(row) for row in rows]
                
        except sqlite3.Error as e:
            print(f"Error reading feedback: {e}")
            return []
    
    def get_by_id(self, feedback_id):
        """
        Get a specific feedback by the ID.
        
        Args:feedback_id (int)
            
        Returns:dict
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
            print(f"Error getting feedback by ID: {e}")
            return None
    
    def update(self, feedback_id, data):
        """
        Update an already done feedback entry.
        
        Args:feedback_id (int), data (dict)
            
        Returns:bool
        """
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
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
            print(f"Error updating feedback: {e}")
            return False
    
    def delete(self, feedback_id):
        """
        Delete an entry.
        
        Args:feedback_id (int)
            
        Returns:bool: 
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
            print(f"Error deleting the feedback: {e}")
            return False
