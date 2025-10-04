# Feedback System - DevOps Assignment 1

A simple CRUD (Create, Read, Update, Delete) feedback application built with Flask, SQLite, and HTML templates. This app allows users to write in feedback, view all feedback entries, update existing feedback, and delete feedback entries.

## Features

- **Create Feedback**: Submit new feedback with user name and comments
- **Read Feedback**: View all feedback entries in a clean, organized layout
- **Update Feedback**: Edit existing feedback entries
- **Delete Feedback**: Remove feedback entries with confirmation
- **Input Validation**: Ensures required fields are not empty
- **Responsive Design**: Works on desktop and mobile devices
- **Flash Messages**: User-friendly success and error notifications

## Architecture

- **Backend**: Flask 
- **Database**: SQLite 
- **Frontend**: HTML templates with Jinja2 templating
- **Styling**: Custom CSS with responsive design
- **Model**: `FeedbackModel` class handles all database operations

## Database Scheme

```sql
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT NOT NULL,
    comment TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
```

## Project structure

```
feedback_app/
├── app.py                  # Flask application entry point
├── models.py               # FeedbackModel class with SQLite CRUD operations
├── templates/
│   ├── base.html           # Base template with common layout
│   ├── create.html         # Create feedback form
│   ├── read.html           # Display all feedback
│   └── update.html         # Update feedback form
├── static/
│   └── style.css           # Custom CSS styling
├── feedback.db             # SQLite database (created automatically)
└── README.md               # This file
```

## Setup instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd DevOps-Assignment1--Feedback-System
   ```

2. **Navigate to the feedback_app directory**:
   ```bash
   cd feedback_app
   ```

3. **Create a venv** (recommended):
   ```bash
   python -m venv venv
   ```

4. **Activate the virtual environment**:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

5. **Install Flask**:
   ```bash
   pip install flask
   ```

6. **Run the application**:
   ```bash
   flask run
   ```
   Or:
   ```bash
   python app.py
   ```

7. **Access the application**:
   Open web browser and go to `http://localhost:5001`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Redirects to feedback list |
| GET/POST | `/create_feedback` | Create new feedback |
| GET | `/read_feedback` | View all feedback entries |
| GET/POST | `/update_feedback/<id>` | Update specific feedback |
| GET | `/delete_feedback/<id>` | Delete specific feedback |

## Usage

1. **View Feedback**: Navigate to the home page to see all existing feedback
2. **Add Feedback**: Click "Add New Feedback" to submit new feedback
3. **Edit Feedback**: Click "Edit" on any feedback card to modify it
4. **Delete Feedback**: Click "Delete" on any feedback card to remove it (with confirmation)

## Testing

The application includes input validation and error handling:
- Empty user names and comments are rejected
- Flash messages provide user feedback
- Database errors are handled gracefully
- Confirmation dialogs prevent accidental deletions

## Development Notes

### Code Quality
- Follows PEP 8 style guidelines
- Comprehensive comments and docstrings
- Error handling for database operations
- Input validation and sanitization

### Security Considerations
- Input validation prevents empty submissions
- SQLite parameterized queries prevent SQL injection
- Flash messages provide user feedback without exposing system details

### Future Enhancements
- User authentication and authorization
- Pagination for large feedback lists
- Search and filtering capabilities
- Email notifications for new feedback
- API endpoints for external integrations



