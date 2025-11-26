
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g

from models import FeedbackModel
from config import SECRET_KEY, DEBUG, HOST, PORT, Messages, MessageCategories
from validators import validate_feedback_data, sanitize_input
from logging_config import setup_logging

# Setup logging
setup_logging()

import logging
logger = logging.getLogger(__name__)

# Instrumentation
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Start time for uptime metric
APP_START_TIME = time.time()

# Prometheeus metrics
REQUEST_COUNT = Counter(
    'app_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)
REQUEST_EXCEPTIONS = Counter(
    'app_exceptions_total',
    'Total exceptions raised by the application',
    ['endpoint']
)

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


# Metrics hooks
@app.before_request
def _before_request_metrics():
    g._req_start_time = time.time()


@app.after_request
def _after_request_metrics(response):
    try:
        start = getattr(g, '_req_start_time', None)
        if start is not None:
            latency = time.time() - start
            endpoint = (request.endpoint or 'unknown')
            REQUEST_LATENCY.labels(request.method, endpoint).observe(latency)
            REQUEST_COUNT.labels(request.method, endpoint, str(response.status_code)).inc()
    except Exception:
        logger.exception('Metrics collection failed')
    return response


@app.errorhandler(Exception)
def _handle_exception_metrics(e):
    endpoint = (request.endpoint or 'unknown')
    REQUEST_EXCEPTIONS.labels(endpoint).inc()
    raise e


@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint."""
    data = generate_latest()
    return data, 200, {'Content-Type': CONTENT_TYPE_LATEST}


@app.route('/health')
def health():
    """Basic health endpoint."""
    uptime_seconds = int(time.time() - APP_START_TIME)
    status = {
        'status': 'ok',
        'uptime_seconds': uptime_seconds,
        'db_path': getattr(feedback_model, 'db_path', 'unknown')
    }
    return jsonify(status), 200


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
