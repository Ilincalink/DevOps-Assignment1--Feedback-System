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
   # HindSight — Feedback System

   A simple CRUD feedback application built with Flask and SQLite, packaged for containerized deployment with monitoring and CI/CD.

   ## Features

   - Create, read, update, delete feedback entries (user + comment)
   - Input validation in the web layer and centralized validators
   - Prometheus metrics (`/metrics`) and a basic `/health` endpoint
   - Dockerized image and docker-compose stack with Prometheus + Grafana
   - GitHub Actions CI (tests, coverage, build) and CD (push to ACR + deploy to Container Apps)

   ## Quick links

   - App entry: `feedback_app/app.py`
   - Model: `feedback_app/models.py` (`FeedbackModel`)
   - Validation: `feedback_app/validators.py` (`validate_feedback_data`)
   - Tests: `feedback_app/tests/`
   - Dockerfile: `Dockerfile`
   - Compose: `docker-compose.yml`
   - CI/CD: `.github/workflows/ci.yml`, `.github/workflows/cd.yml`

   ## Requirements

   - Python 3.12 (recommended)
   - Docker (for container runs)
   - Docker Compose (optional, for monitoring stack)

   ## Local development (recommended)

   1. Clone and open repo:
      ```bash
      git clone <repo-url>
      cd DevOps-Assignment1--Feedback-System
      ```

   2. Create and activate a virtual environment:
      ```bash
      python -m venv .venv
      source .venv/bin/activate    # macOS/Linux
      .\.venv\Scripts\activate   # Windows (PowerShell)
      ```

   3. Install runtime dependencies:
      ```bash
      pip install -r feedback_app/requirements.txt
      ```

   4. Run the app:
      ```bash
      # ensure environment variables (see .env.example)
      python feedback_app/app.py
      ```
      Open http://localhost:5001

   ## Docker / Compose

   - Build and run container locally:
     ```bash
     docker build -t feedback-app:local .
     docker run --rm -p 5001:5001 --env-file .env.example -v feedback_data:/app/data feedback-app:local
     ```
   - Run full stack (Prometheus + Grafana):
     ```bash
     docker-compose up --build
     ```
   - Container exposes port `5001` (Dockerfile `EXPOSE 5001`) and persists DB/logs via `/app/data` and `/app/logs`.

   ## Testing

   1. Install test deps:
      ```bash
      cd feedback_app
      pip install -r requirements-test.txt
      ```
   2. Run tests:
      ```bash
      python -m pytest tests/ -v
      ```
   3. Run with coverage:
      ```bash
      python -m pytest --cov=. --cov-report=html --cov-report=term-missing tests/ -v
      # open htmlcov/index.html
      ```

   Notes:
   - Unit tests target the model and helpers; integration tests exercise Flask routes with a temporary SQLite DB.
   - CI enforces a coverage threshold before image push (see `.github/workflows/ci.yml`).

   ## CI/CD

   - CI workflow runs tests, measures coverage and builds/pushes Docker images to Azure Container Registry (ACR). See `.github/workflows/ci.yml`.
   - CD workflow (`.github/workflows/cd.yml`) triggers on successful CI runs for `main`, logs into Azure and updates the Container App using images in ACR.
   - Secrets required for GitHub Actions: `AZURE_CREDENTIALS` / service principal fields, `ACR_NAME`, `ACR_REPOSITORY`, `AZURE_RESOURCE_GROUP`, `ACA_ENVIRONMENT`, `ACA_APP_NAME`, `AZURE_REGION`.

   ## Validation vs Persistence

   - Input validation and sanitization are performed in the web layer using `feedback_app/validators.py` (`validate_feedback_data`).
   - The persistence layer `FeedbackModel` (`feedback_app/models.py`) performs CRUD operations but does not perform additional input validation — controllers must validate before calling the model.

   ## Monitoring

   - Prometheus config: `prometheus/prometheus.yml` (scrapes `/metrics`).
   - Grafana datasource: `grafana/provisioning/datasources/datasources.yml`.
   - The app exposes `/metrics` and `/health` and records request counts, latencies and exceptions.

   ## Environment
   See `.env.example` for recommended environment variables (SECRET_KEY, DEBUG, HOST, PORT, DATABASE_PATH, LOG_LEVEL, LOG_FILE).

   ## Contributing / Notes
   - Follow `feedback_app/REFACTORING_SUMMARY.md` for refactor rationale.
   - Ensure `python-version` in CI and local environment matches (3.12) to avoid subtle incompatibilities.

   ```



