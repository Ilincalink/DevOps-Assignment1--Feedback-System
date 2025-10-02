
from flask import Flask, render_template, request, redirect, url_for, flash
from models import FeedbackModel 

app = Flask(__name__)
app.secret_key = 'your-secret-key-here' # added to avoid the runtime error about the secret key. Learned that the hard way. 


feedback_model = FeedbackModel()

@app.route('/')
def index():
    """Homepage redirects to read feedback."""
    return redirect(url_for('read_feedback'))


@app.route('/create_feedback', methods=['GET', 'POST'])
def create_feedback():
    """Create a new feedback entry."""
    if request.method == 'POST':
        user = request.form.get('user', '').strip()
        comment = request.form.get('comment', '').strip()
        
        # Input validation
        if not user or not comment:
            flash('Both user and comment fields needed!', 'error')
            return render_template('create.html')
        
        # Create feedback
        feedback_data = {
            'user': user,
            'comment': comment
        }
        
        if feedback_model.create(feedback_data):
            flash('Feedback created successfully!', 'success')
            return redirect(url_for('read_feedback'))
        else:
            flash('Error creating feedback. try again.', 'error')
    
    return render_template('create.html')


@app.route('/read_feedback')
def read_feedback():
    """Display entire list of the feedback entries."""
    feedback_list = feedback_model.read_all()
    return render_template('read.html', feedback_list=feedback_list)


@app.route('/update_feedback/<int:feedback_id>', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    """Update an existing feedback entry."""
    if request.method == 'POST':
        user = request.form.get('user', '').strip()
        comment = request.form.get('comment', '').strip()
        
        # Input valid
        if not user or not comment:
            flash('Both user and comment fields are needed!', 'error')
            return redirect(url_for('update_feedback', feedback_id=feedback_id))
        
        # update feedback
        feedback_data = {
            'user': user,
            'comment': comment
        }
        
        if feedback_model.update(feedback_id, feedback_data):
            flash('Feedback updated successfully!', 'success')
            return redirect(url_for('read_feedback'))
        else:
            flash('Error updating feedback. try again.', 'error')
    
    # Get current feedback data for the form
    current_feedback = feedback_model.get_by_id(feedback_id)
    if not current_feedback:
        flash('Feedback not found!', 'error')
        return redirect(url_for('read_feedback'))
    
    return render_template('update.html', feedback=current_feedback)


@app.route('/delete_feedback/<int:feedback_id>')
def delete_feedback(feedback_id):
    """Delete feedback entry."""
    if feedback_model.delete(feedback_id):
        flash('Feedback deleted successfully!', 'success')
    else:
        flash('Error deleting feedback. Please try again.', 'error')
    
    return redirect(url_for('read_feedback'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
