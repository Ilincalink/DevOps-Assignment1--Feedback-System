
from flask import Flask, render_template, request, redirect, url_for, flash

from models import FeedbackModel
from config import SECRET_KEY, DEBUG, HOST, PORT, Messages, MessageCategories
from validators import validate_feedback_data, sanitize_input
from logging_config import setup_logging

# Setup logging
setup_logging()

import logging
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = SECRET_KEY

def _process_feedback_form() -> tuple[str, str]:
    """Process and sanitize feedback form data.
    
    Returns:
        Tuple of (user, comment)
    """
    user = sanitize_input(request.form.get('user', ''))
    comment = sanitize_input(request.form.get('comment', ''))
    return user, comment


def _create_feedback_data(user: str, comment: str) -> dict[str, str]:
    """Create feedback data dictionary.
    
    Args:
        user: Users name
        comment: User comment
        
    Returns:
        Dictionary containing feedback data
    """
    return {
        'user': user,
        'comment': comment
    }


feedback_model = FeedbackModel()


@app.route('/')
def index():
    """Homepage redirects to read feedback."""
    return redirect(url_for('read_feedback'))


@app.route('/create_feedback', methods=['GET', 'POST'])
def create_feedback():
    """Create a new feedbacck entry."""
    if request.method == 'POST':
        user, comment = _process_feedback_form()
        
        # Validate input
        is_valid, errors = validate_feedback_data(user, comment)
        if not is_valid:
            flash(Messages.FIELDS_REQUIRED, MessageCategories.ERROR)
            return render_template('create.html')
        
        # Create feedback
        feedback_data = _create_feedback_data(user, comment)
        
        if feedback_model.create(feedback_data):
            flash(Messages.FEEDBACK_CREATED, MessageCategories.SUCCESS)
            return redirect(url_for('read_feedback'))
        else:
            flash(Messages.CREATE_ERROR, MessageCategories.ERROR)
    
    return render_template('create.html')


@app.route('/read_feedback')
def read_feedback():
    """Display entire list of feedback entries."""
    feedback_list = feedback_model.read_all()
    return render_template('read.html', feedback_list=feedback_list)


@app.route('/update_feedback/<int:feedback_id>', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    """Update an existing feedback entry."""
    if request.method == 'POST':
        user, comment = _process_feedback_form()
        
        # Validate input
        is_valid, errors = validate_feedback_data(user, comment)
        if not is_valid:
            flash(Messages.FIELDS_REQUIRED, MessageCategories.ERROR)
            return redirect(url_for('update_feedback', feedback_id=feedback_id))
        
        # Update feedback
        feedback_data = _create_feedback_data(user, comment)
        
        if feedback_model.update(feedback_id, feedback_data):
            flash(Messages.FEEDBACK_UPDATED, MessageCategories.SUCCESS)
            return redirect(url_for('read_feedback'))
        else:
            flash(Messages.UPDATE_ERROR, MessageCategories.ERROR)
    
    # Get current feedback data for the form
    current_feedback = feedback_model.get_by_id(feedback_id)
    if not current_feedback:
        flash(Messages.FEEDBACK_NOT_FOUND, MessageCategories.ERROR)
        return redirect(url_for('read_feedback'))
    
    return render_template('update.html', feedback=current_feedback)


@app.route('/delete_feedback/<int:feedback_id>')
def delete_feedback(feedback_id):
    """Delete feedback entry."""
    if feedback_model.delete(feedback_id):
        flash(Messages.FEEDBACK_DELETED, MessageCategories.SUCCESS)
    else:
        flash(Messages.DELETE_ERROR, MessageCategories.ERROR)
    
    return redirect(url_for('read_feedback'))


if __name__ == '__main__':
    logger.info(f"Starting Flask application on {HOST}:{PORT}")
    app.run(debug=DEBUG, host=HOST, port=PORT)
