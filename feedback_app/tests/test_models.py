import pytest
import sqlite3
import os
import tempfile
from datetime import datetime
from models import FeedbackModel


class TestFeedbackModel:
    """Comprehensive test suite for FeedbackModel class."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        db_fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(db_fd)
        yield db_path
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
    
    @pytest.fixture
    def feedback_model(self, temp_db):
        """Create a FeedbackModel instance with temporary database."""
        return FeedbackModel(db_path=temp_db)
    
    @pytest.fixture
    def sample_feedback_data(self):
        """Sample feedback data for testing."""
        return {
            'user': 'Test User',
            'comment': 'This is a test feedback comment.'
        }
    
    def test_init_database_creates_table(self, feedback_model, temp_db):
        """Test that init_database creates the feedback table."""
        # Check if table exists
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='feedback'
            """)
            result = cursor.fetchone()
            assert result is not None
            assert result[0] == 'feedback'
    
    def test_init_database_table_structure(self, feedback_model, temp_db):
        """Test that the feedback table has correct structure."""
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(feedback)")
            columns = cursor.fetchall()
            
        column_names = [col[1] for col in columns]
        expected_columns = ['id', 'user', 'comment', 'timestamp']
        
        assert all(col in column_names for col in expected_columns)
        
        # Check primary key
        id_column = next(col for col in columns if col[1] == 'id')
        assert id_column[5] == 1  # Primary key
    
    def test_create_feedback_success(self, feedback_model, sample_feedback_data):
        """Test successful feedback creation."""
        result = feedback_model.create(sample_feedback_data)
        assert result is True
        
        # Verify data was inserted
        all_feedback = feedback_model.read_all()
        assert len(all_feedback) == 1
        assert all_feedback[0]['user'] == sample_feedback_data['user']
        assert all_feedback[0]['comment'] == sample_feedback_data['comment']
        assert 'timestamp' in all_feedback[0]
        assert 'id' in all_feedback[0]
    
    def test_create_feedback_with_timestamp(self, feedback_model, sample_feedback_data):
        """Test that feedback creation includes proper timestamp."""
        before_creation = datetime.now()
        feedback_model.create(sample_feedback_data)
        after_creation = datetime.now()
        
        feedback = feedback_model.read_all()[0]
        created_timestamp = datetime.strptime(feedback['timestamp'], '%Y-%m-%d %H:%M:%S')
        
        # Allow 1 minute tolerance for test execution time
        assert (created_timestamp - before_creation).total_seconds() >= -60
        assert (after_creation - created_timestamp).total_seconds() >= -60
    
    def test_create_feedback_empty_user(self, feedback_model):
        """Test feedback creation with empty user."""
        invalid_data = {'user': '', 'comment': 'Valid comment'}
        result = feedback_model.create(invalid_data)
        # Your implementation doesn't validate - it creates with empty user
        assert result is True
    
    def test_create_feedback_empty_comment(self, feedback_model):
        """Test feedback creation with empty comment."""
        invalid_data = {'user': 'Valid User', 'comment': ''}
        result = feedback_model.create(invalid_data)
        # Your implementation doesn't validate - it creates with empty comment
        assert result is True
    
    def test_create_feedback_missing_keys(self, feedback_model):
        """Test feedback creation with missing required keys."""
        # Missing user key - this will raise KeyError
        invalid_data1 = {'comment': 'Valid comment'}
        try:
            result1 = feedback_model.create(invalid_data1)
            assert result1 is False
        except KeyError:
            # Expected behavior - missing key causes error
            pass
        
        # Missing comment key - this will raise KeyError
        invalid_data2 = {'user': 'Valid User'}
        try:
            result2 = feedback_model.create(invalid_data2)
            assert result2 is False
        except KeyError:
            # Expected behavior - missing key causes error
            pass
    
    def test_create_feedback_none_values(self, feedback_model):
        """Test feedback creation with None values."""
        invalid_data = {'user': None, 'comment': None}
        result = feedback_model.create(invalid_data)
        assert result is False
    
    def test_read_all_empty_database(self, feedback_model):
        """Test reading from empty database."""
        result = feedback_model.read_all()
        assert result == []
    
    def test_read_all_multiple_feedback(self, feedback_model):
        """Test reading multiple feedback entries."""
        feedback_data = [
            {'user': 'User1', 'comment': 'Comment1'},
            {'user': 'User2', 'comment': 'Comment2'},
            {'user': 'User3', 'comment': 'Comment3'}
        ]
        
        for data in feedback_data:
            feedback_model.create(data)
        
        result = feedback_model.read_all()
        assert len(result) == 3
        
        # Verify all data is present
        users = [f['user'] for f in result]
        assert 'User1' in users
        assert 'User2' in users
        assert 'User3' in users
    
    def test_read_all_order(self, feedback_model):
        """Test that read_all returns entries in correct order (newest first)."""
        import time
        
        # Create entries with meaningful time gaps
        feedback_model.create({'user': 'First', 'comment': 'First comment'})
        time.sleep(1)  # Ensure different seconds in timestamp
        feedback_model.create({'user': 'Second', 'comment': 'Second comment'})
        time.sleep(1)
        feedback_model.create({'user': 'Third', 'comment': 'Third comment'})
        
        result = feedback_model.read_all()
        # Should be in DESC order (newest first)
        assert len(result) == 3
        assert result[0]['user'] == 'Third'
        assert result[1]['user'] == 'Second'
        assert result[2]['user'] == 'First'
    
    def test_get_by_id_existing(self, feedback_model, sample_feedback_data):
        """Test getting feedback by existing ID."""
        feedback_model.create(sample_feedback_data)
        all_feedback = feedback_model.read_all()
        feedback_id = all_feedback[0]['id']
        
        result = feedback_model.get_by_id(feedback_id)
        assert result is not None
        assert result['id'] == feedback_id
        assert result['user'] == sample_feedback_data['user']
        assert result['comment'] == sample_feedback_data['comment']
    
    def test_get_by_id_nonexistent(self, feedback_model):
        """Test getting feedback by non-existent ID."""
        result = feedback_model.get_by_id(999)
        assert result is None
    
    def test_get_by_id_invalid_type(self, feedback_model):
        """Test getting feedback with invalid ID type."""
        result = feedback_model.get_by_id("invalid")
        assert result is None
    
    def test_get_by_id_negative_id(self, feedback_model):
        """Test getting feedback with negative ID."""
        result = feedback_model.get_by_id(-1)
        assert result is None
    
    def test_update_feedback_success(self, feedback_model, sample_feedback_data):
        """Test successful feedback update."""
        # Create initial feedback
        feedback_model.create(sample_feedback_data)
        feedback_id = feedback_model.read_all()[0]['id']
        
        # Update data
        update_data = {
            'user': 'Updated User',
            'comment': 'Updated comment content'
        }
        
        result = feedback_model.update(feedback_id, update_data)
        assert result is True
        
        # Verify update
        updated_feedback = feedback_model.get_by_id(feedback_id)
        assert updated_feedback['user'] == update_data['user']
        assert updated_feedback['comment'] == update_data['comment']
    
    def test_update_feedback_preserves_id_and_timestamp(self, feedback_model, sample_feedback_data):
        """Test that update preserves original ID and timestamp."""
        feedback_model.create(sample_feedback_data)
        original_feedback = feedback_model.read_all()[0]
        
        update_data = {'user': 'Updated User', 'comment': 'Updated comment'}
        feedback_model.update(original_feedback['id'], update_data)
        
        updated_feedback = feedback_model.get_by_id(original_feedback['id'])
        assert updated_feedback['id'] == original_feedback['id']
        assert updated_feedback['timestamp'] == original_feedback['timestamp']
    
    def test_update_feedback_nonexistent(self, feedback_model):
        """Test updating non-existent feedback."""
        update_data = {'user': 'User', 'comment': 'Comment'}
        result = feedback_model.update(999, update_data)
        assert result is False
    
    def test_update_feedback_empty_user(self, feedback_model, sample_feedback_data):
        """Test updating feedback with empty user."""
        feedback_model.create(sample_feedback_data)
        feedback_id = feedback_model.read_all()[0]['id']
        
        # Your implementation doesn't validate - it updates with empty user
        result = feedback_model.update(feedback_id, {'user': '', 'comment': 'Valid'})
        assert result is True
    
    def test_update_feedback_empty_comment(self, feedback_model, sample_feedback_data):
        """Test updating feedback with empty comment."""
        feedback_model.create(sample_feedback_data)
        feedback_id = feedback_model.read_all()[0]['id']
        
        # Your implementation doesn't validate - it updates with empty comment
        result = feedback_model.update(feedback_id, {'user': 'Valid', 'comment': ''})
        assert result is True
    
    def test_update_feedback_missing_keys(self, feedback_model, sample_feedback_data):
        """Test updating feedback with missing keys."""
        feedback_model.create(sample_feedback_data)
        feedback_id = feedback_model.read_all()[0]['id']
        
        # Missing user - will cause KeyError
        try:
            result1 = feedback_model.update(feedback_id, {'comment': 'Valid'})
            assert result1 is False
        except KeyError:
            # Expected behavior - missing key causes error
            pass
        
        # Missing comment - will cause KeyError
        try:
            result2 = feedback_model.update(feedback_id, {'user': 'Valid'})
            assert result2 is False
        except KeyError:
            # Expected behavior - missing key causes error
            pass
    
    def test_delete_feedback_success(self, feedback_model, sample_feedback_data):
        """Test successful feedback deletion."""
        # Create feedback
        feedback_model.create(sample_feedback_data)
        feedback_id = feedback_model.read_all()[0]['id']
        
        # Delete feedback
        result = feedback_model.delete(feedback_id)
        assert result is True
        
        # Verify deletion
        assert feedback_model.get_by_id(feedback_id) is None
        assert len(feedback_model.read_all()) == 0
    
    def test_delete_feedback_nonexistent(self, feedback_model):
        """Test deleting non-existent feedback."""
        result = feedback_model.delete(999)
        assert result is False
    
    def test_delete_feedback_invalid_id(self, feedback_model):
        """Test deleting with invalid ID."""
        result = feedback_model.delete("invalid")
        assert result is False
    
    def test_delete_feedback_multiple_entries(self, feedback_model):
        """Test deleting one entry from multiple entries."""
        # Create multiple entries
        for i in range(3):
            feedback_model.create({'user': f'User{i}', 'comment': f'Comment{i}'})
        
        all_feedback = feedback_model.read_all()
        assert len(all_feedback) == 3
        
        # Delete middle entry
        middle_id = all_feedback[1]['id']
        result = feedback_model.delete(middle_id)
        assert result is True
        
        # Verify only one was deleted
        remaining_feedback = feedback_model.read_all()
        assert len(remaining_feedback) == 2
        assert feedback_model.get_by_id(middle_id) is None
    
    def test_database_error_handling(self):
        """Test database error handling with invalid database path."""
        # Create model with invalid database path
        invalid_model = FeedbackModel(db_path='/invalid/path/database.db')
        
        # These should not raise exceptions, but return False/empty results
        result = invalid_model.create({'user': 'Test', 'comment': 'Test'})
        assert result is False
        
        result = invalid_model.read_all()
        assert result == []
        
        result = invalid_model.get_by_id(1)
        assert result is None
        
        result = invalid_model.update(1, {'user': 'Test', 'comment': 'Test'})
        assert result is False
        
        result = invalid_model.delete(1)
        assert result is False
    
    def test_concurrent_operations(self, feedback_model):
        """Test multiple concurrent operations."""
        # Create multiple feedback entries
        for i in range(5):
            data = {'user': f'User{i}', 'comment': f'Comment{i}'}
            result = feedback_model.create(data)
            assert result is True
        
        # Read all
        all_feedback = feedback_model.read_all()
        assert len(all_feedback) == 5
        
        # Update one
        feedback_id = all_feedback[0]['id']
        update_result = feedback_model.update(feedback_id, {
            'user': 'Updated User',
            'comment': 'Updated Comment'
        })
        assert update_result is True
        
        # Delete one
        delete_id = all_feedback[1]['id']
        delete_result = feedback_model.delete(delete_id)
        assert delete_result is True
        
        # Verify final state
        final_feedback = feedback_model.read_all()
        assert len(final_feedback) == 4
        
        updated_feedback = feedback_model.get_by_id(feedback_id)
        assert updated_feedback['user'] == 'Updated User'
        
        deleted_feedback = feedback_model.get_by_id(delete_id)
        assert deleted_feedback is None
    
    def test_full_crud_cycle(self, feedback_model):
        """Test complete CRUD cycle."""
        # CREATE
        create_data = {'user': 'CRUD Test User', 'comment': 'CRUD test comment'}
        create_result = feedback_model.create(create_data)
        assert create_result is True
        
        # READ
        all_feedback = feedback_model.read_all()
        assert len(all_feedback) == 1
        feedback_id = all_feedback[0]['id']
        
        single_feedback = feedback_model.get_by_id(feedback_id)
        assert single_feedback['user'] == create_data['user']
        assert single_feedback['comment'] == create_data['comment']
        
        # UPDATE
        update_data = {'user': 'Updated CRUD User', 'comment': 'Updated CRUD comment'}
        update_result = feedback_model.update(feedback_id, update_data)
        assert update_result is True
        
        updated_feedback = feedback_model.get_by_id(feedback_id)
        assert updated_feedback['user'] == update_data['user']
        assert updated_feedback['comment'] == update_data['comment']
        
        # DELETE
        delete_result = feedback_model.delete(feedback_id)
        assert delete_result is True
        
        final_feedback = feedback_model.read_all()
        assert len(final_feedback) == 0
    
    def test_edge_cases_long_text(self, feedback_model):
        """Test with very long user names and comments."""
        long_data = {
            'user': 'A' * 1000,  # Very long username
            'comment': 'B' * 5000  # Very long comment
        }
        
        result = feedback_model.create(long_data)
        assert result is True
        
        retrieved = feedback_model.read_all()[0]
        assert retrieved['user'] == long_data['user']
        assert retrieved['comment'] == long_data['comment']
    
    def test_special_characters(self, feedback_model):
        """Test with special characters and unicode."""
        special_data = {
            'user': "Test User with 'quotes' and \"double quotes\"",
            'comment': "Comment with émojis 🎉 and special chars: @#$%^&*()"
        }
        
        result = feedback_model.create(special_data)
        assert result is True
        
        retrieved = feedback_model.read_all()[0]
        assert retrieved['user'] == special_data['user']
        assert retrieved['comment'] == special_data['comment']
