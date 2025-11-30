# HindSight

## DevOps Assignment 2 Short Report

**Ilinca Corbu**

---

## Abstract

During the second assignment I improved the feedback application by removing code smells, improving type safety, creating a CI/CD pipeline and deploying a containerized version. This document describes the improvements and new implementations concisely. A more detailed description of the new features would be found in the documentation.

---

## Code Improvements

Key changes made to improve maintainability, testability and quality:

- Centralized configuration in [`feedback_app/config.py`](feedback_app/config.py) and removed hardcoded values (secret key, host, port, timestamp format).
- Replaced duplicated validation logic with [`feedback_app/validators.py`](feedback_app/validators.py) and the function [`validate_feedback_data`](feedback_app/validators.py).
- Added structured logging via [`feedback_app/logging_config.py`](feedback_app/logging_config.py).
- Improved separation of concerns (validation in `validators.py`, business logic in [`feedback_app/models.py`](feedback_app/models.py) as class [`FeedbackModel`](feedback_app/models.py)).
- Added type hints, consistent docstrings and PEP8-style formatting.
- Created `.env.example` to document runtime environment variables.

Files changed/created (high level):
- Modified: [`feedback_app/app.py`](feedback_app/app.py), [`feedback_app/models.py`](feedback_app/models.py)  
- Created: [`feedback_app/config.py`](feedback_app/config.py), [`feedback_app/validators.py`](feedback_app/validators.py), [`feedback_app/logging_config.py`](feedback_app/logging_config.py), `.env.example`

See the refactoring summary: [`feedback_app/REFACTORING_SUMMARY.md`](feedback_app/REFACTORING_SUMMARY.md).

---

## Pipeline

CI and CD are implemented with GitHub Actions.

CI
- Workflow: [.github/workflows/ci.yml](.github/workflows/ci.yml)
- Steps:
  - Checkout repository
  - Setup Python 3.12
  - Install runtime and test dependencies (see [`feedback_app/requirements.txt`](feedback_app/requirements.txt) and [`feedback_app/requirements-test.txt`](feedback_app/requirements-test.txt))
  - Run tests with coverage (pytest + pytest-cov). Tests are configured in [`feedback_app/pytest.ini`](feedback_app/pytest.ini) and test files live under [`feedback_app/tests/`](feedback_app/tests/)
  - Build Docker image using [`Dockerfile`](Dockerfile)
  - Authenticate to Azure and push images to Azure Container Registry (ACR)

CD
- Workflow: [.github/workflows/cd.yml](.github/workflows/cd.yml)
- Trigger: runs when CI completes successfully on branch `main` (workflow_run with conclusion == success and head_branch == `main`)
- Steps:
  - Checkout code
  - Login to Azure using `AZURE_CREDENTIALS` (GitHub Secret)
  - Login to ACR and deploy to Azure Container Apps (create or update) using `az containerapp` commands
  - Deployment parameters (resource group, environment, app name, ACR repo, region) are passed via repository secrets:
    - `AZURE_CREDENTIALS`, `ACR_NAME`, `ACR_REPOSITORY`, `AZURE_RESOURCE_GROUP`, `ACA_ENVIRONMENT`, `ACA_APP_NAME`, `AZURE_REGION`, `ACR_USERNAME`, `ACR_PASSWORD`

See CI/CD configs: [.github/workflows/ci.yml](.github/workflows/ci.yml), [.github/workflows/cd.yml](.github/workflows/cd.yml).

---

## Containerization

- Dockerfile summary: base image `python:3.12-slim`, working dir `/app`, installs `sqlite3` and Python dependencies from [`feedback_app/requirements.txt`](feedback_app/requirements.txt), copies application source, creates `/app/data` and `/app/logs`, switches to non-root `USER 1000`, declares `EXPOSE 5001`, sets `VOLUME` for persistent data/logs, and final `CMD` runs database setup script and starts the Flask app. See [`Dockerfile`](Dockerfile).
- How Flask runs inside the container: the container `CMD` runs `python feedback_app/setup.py` to ensure sample data, then `python feedback_app/app.py` which creates the Flask `app` object (see [`feedback_app/app.py`](feedback_app/app.py)). `app.run()` uses configuration values from [`feedback_app/config.py`](feedback_app/config.py) (`HOST`, `PORT`, `DEBUG`) so Flask listens on the declared port.
- EXPOSE and environment variables:
  - `EXPOSE 5001` documents the service port in the image (`Dockerfile`).
  - Runtime configuration is driven by environment variables documented in `.env.example` and read via [`feedback_app/config.py`](feedback_app/config.py) (SECRET_KEY, DEBUG, HOST, PORT, DATABASE_PATH, LOG_LEVEL, LOG_FILE).
  - Volumes (`VOLUME ["/app/data","/app/logs"]` and docker-compose `feedback_data`) persist the SQLite DB and logs across container restarts.
- Container testing:
  - Build and run locally:
    - `docker build -t feedback-app:local .`
    - `docker run --rm -p 5001:5001 --env-file .env.example -v feedback_data:/app/data feedback-app:local`
    - Check endpoints: `curl http://localhost:5001/health`, `curl http://localhost:5001/metrics`
  - Or use `docker-compose up --build` to run the app alongside Prometheus and Grafana using [`docker-compose.yml`](docker-compose.yml).
  - CI builds and pushes immutable image tags to ACR; CD deploys those images.

---

## Monitoring and Testing

Monitoring
- Prometheus scraping config: [`prometheus/prometheus.yml`](prometheus/prometheus.yml) (scrapes `/metrics` on the app)
- Grafana data source provisioning: [`grafana/provisioning/datasources/datasources.yml`](grafana/provisioning/datasources/datasources.yml)
- Instrumentation: implemented in [`feedback_app/app.py`](feedback_app/app.py) using `prometheus_client`:
  - `REQUEST_COUNT` Counter, `REQUEST_LATENCY` Histogram, `REQUEST_EXCEPTIONS` Counter
  - `/metrics` endpoint returns Prometheus metrics via `generate_latest`
  - `/health` endpoint returns JSON status with uptime and DB path

Testing
- Tests live under [`feedback_app/tests/`](feedback_app/tests/) and are configured by [`feedback_app/pytest.ini`](feedback_app/pytest.ini).
  - Unit tests: [`feedback_app/tests/test_models.py`](feedback_app/tests/test_models.py), model-focused tests for [`FeedbackModel`](feedback_app/models.py).
  - Integration tests: [`feedback_app/tests/test_app.py`](feedback_app/tests/test_app.py), using Flask test client and temporary SQLite DBs.
  - Setup tests: [`feedback_app/tests/test_setup.py`](feedback_app/tests/test_setup.py)
- Test tooling: `pytest`, `pytest-cov`, `pytest-flask` (see [`feedback_app/requirements-test.txt`](feedback_app/requirements-test.txt)).
- CI enforces coverage and runs tests before image push (see [.github/workflows/ci.yml](.github/workflows/ci.yml)).

Recommended test architecture:
- Fast unit test suite for developers (models, validators, helpers).
- Integration suite for CI (Flask routes + DB).
- Optional E2E or smoke tests against a deployed environment.
- Use CI-produced immutable image tags for reproducible E2E runs.

Testing docs: [`feedback_app/TESTING.md`](feedback_app/TESTING.md).

---


## Quick Links

- CI workflow: [.github/workflows/ci.yml](.github/workflows/ci.yml)  
- CD workflow: [.github/workflows/cd.yml](.github/workflows/cd.yml)  
- Dockerfile: [Dockerfile](Dockerfile)  
- Docker compose: [docker-compose.yml](docker-compose.yml)  
- App entry: [`app`](feedback_app/app.py) ([feedback_app/app.py](feedback_app/app.py))  
- Model: [`FeedbackModel`](feedback_app/models.py) ([feedback_app/models.py](feedback_app/models.py))  
- Validators: [`validate_feedback_data`](feedback_app/validators.py) ([feedback_app/validators.py](feedback_app/validators.py))  
- Setup script: [`setup_database`](feedback_app/setup.py) ([feedback_app/setup.py](feedback_app/setup.py))  
- Config: [feedback_app/config.py](feedback_app/config.py)  
- Logging config: [feedback_app/logging_config.py](feedback_app/logging_config.py)  
- Tests: [feedback_app/tests/](feedback_app/tests/)  
- Test config: [feedback_app/pytest.ini](feedback_app/pytest.ini), [feedback_app/TESTING.md](feedback_app/TESTING.md)  
- Monitoring: [prometheus/prometheus.yml](prometheus/prometheus.yml), [grafana/provisioning/datasources/datasources.yml](grafana/provisioning/datasources/datasources.yml)