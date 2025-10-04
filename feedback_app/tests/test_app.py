import pytest
import tempfile
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import FeedbackModel


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    # Configure app for testing
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Replace the feedback_model with one using temp database
    app.feedback_model = FeedbackModel(db_path=db_path)
    
    with app.test_client() as client:
        with app.app_context():
            yield client
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def sample_feedback():
    """Sample feedback data for testing."""
    return {
        'user': 'Test User',
        'comment': 'This is a test feedback comment for Flask testing.'
    }


class TestFlaskRoutes:
    """Test suite for Flask application routes."""
    
    def test_index_redirect(self, client):
        """Test that index route redirects to read_feedback."""
        response = client.get('/')
        assert response.status_code == 302
        assert '/read_feedback' in response.location
    
    def test_create_feedback_get(self, client):
        """Test GET request to create_feedback route."""
        response = client.get('/create_feedback')
        assert response.status_code == 200
        assert b'form' in response.data
    
    def test_create_feedback_post_success(self, client, sample_feedback):
        """Test successful POST to create_feedback route."""
        response = client.post('/create_feedback', data=sample_feedback, follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to read_feedback and show the data
        assert sample_feedback['user'].encode() in response.data
    
    def test_create_feedback_post_empty_user(self, client):
        """Test POST with empty user field - should fail validation."""
        invalid_data = {'user': '', 'comment': 'Valid comment'}
        response = client.post('/create_feedback', data=invalid_data)
        assert response.status_code == 200
        # Should return to form page due to validation
        assert b'form' in response.data
    
    def test_create_feedback_post_empty_comment(self, client):
        """Test POST with empty comment field - should fail validation."""
        invalid_data = {'user': 'Valid User', 'comment': ''}
        response = client.post('/create_feedback', data=invalid_data)
        assert response.status_code == 200
        # Should return to form page due to validation
        assert b'form' in response.data
    
    def test_read_feedback_empty(self, client):
        """Test read_feedback route with empty database."""
        response = client.get('/read_feedback')
        assert response.status_code == 200
        # Should load the page successfully even if empty
    
    def test_read_feedback_with_data(self, client, sample_feedback):
        """Test read_feedback route with existing feedback."""
        # First create some feedback
        client.post('/create_feedback', data=sample_feedback, follow_redirects=True)
        
        # Then read it
        response = client.get('/read_feedback')
        assert response.status_code == 200
        assert sample_feedback['user'].encode() in response.data
        assert sample_feedback['comment'].encode() in response.data
    
    def test_update_feedback_workflow(self, client, sample_feedback):
        """Test complete update workflow."""
        # Create feedback first
        response = client.post('/create_feedback', data=sample_feedback, follow_redirects=True)
        assert response.status_code == 200
        
        # Get the created feedback ID
        feedback_list = app.feedback_model.read_all()
        if len(feedback_list) > 0:
            feedback_id = feedback_list[0]['id']
            
            # Test GET update form
            response = client.get(f'/update_feedback/{feedback_id}')
            assert response.status_code == 200
            
            # Test POST update
            updated_data = {'user': 'Updated User', 'comment': 'Updated comment'}
            response = client.post(f'/update_feedback/{feedback_id}', 
                                 data=updated_data, follow_redirects=True)
            assert response.status_code == 200
            assert b'Updated User' in response.data
    
    def test_delete_feedback_workflow(self, client, sample_feedback):
        """Test complete delete workflow."""
        # Create feedback first
        client.post('/create_feedback', data=sample_feedback, follow_redirects=True)
        
        # Get the created feedback ID
        feedback_list = app.feedback_model.read_all()
        if len(feedback_list) > 0:
            feedback_id = feedback_list[0]['id']
            
            # Delete the feedback
            response = client.get(f'/delete_feedback/{feedback_id}', follow_redirects=True)
            assert response.status_code == 200
            
            # Verify deletion
            feedback_list_after = app.feedback_model.read_all()
            assert len(feedback_list_after) == 0
    
    def test_delete_feedback_nonexistent(self, client):
        """Test deleting non-existent feedback."""
        response = client.get('/delete_feedback/999', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect gracefully without error
    
    def test_update_feedback_nonexistent(self, client):
        """Test updating non-existent feedback."""
        response = client.get('/update_feedback/999', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect gracefully without error


class TestFlaskIntegration:
    """Integration tests for Flask application workflows."""
    
    def test_navigation_flow(self, client, sample_feedback):
        """Test navigation between different pages."""
        # Start at index
        response = client.get('/')
        assert response.status_code == 302
        
        # Go to create page
        response = client.get('/create_feedback')
        assert response.status_code == 200
        
        # Create feedback and verify redirect
        response = client.post('/create_feedback', data=sample_feedback, follow_redirects=True)
        assert response.status_code == 200
        assert sample_feedback['user'].encode() in response.data
    
    def test_form_validation_persistence(self, client):
        """Test that invalid form data is handled properly."""
        # Test with whitespace-only input
        invalid_data = {'user': '   ', 'comment': '   '}
        response = client.post('/create_feedback', data=invalid_data)
        assert response.status_code == 200
        # Should return to form due to validation (strip() makes them empty)
        assert b'form' in response.data
    
    def test_multiple_feedback_handling(self, client):
        """Test handling multiple feedback entries."""
        feedback_entries = [
            {'user': 'User1', 'comment': 'Comment1'},
            {'user': 'User2', 'comment': 'Comment2'},
            {'user': 'User3', 'comment': 'Comment3'}
        ]
        
        # Create multiple entries
        for feedback in feedback_entries:
            response = client.post('/create_feedback', data=feedback, follow_redirects=True)
            assert response.status_code == 200
        
        # Verify all entries appear on read page
        response = client.get('/read_feedback')
        assert response.status_code == 200
        for feedback in feedback_entries:
            assert feedback['user'].encode() in response.data
            assert feedback['comment'].encode() in response.data
