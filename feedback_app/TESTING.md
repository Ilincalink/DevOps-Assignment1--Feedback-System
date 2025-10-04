# 🧪 Backend Testing Guide

## Quick Test Commands (Copy-Paste Ready)

### Install Test Dependencies
```bash
cd feedback_app
pip install -r requirements-test.txt
```

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Tests with Coverage Report
```bash
python -m pytest --cov=. --cov-report=html --cov-report=term-missing tests/ -v
```

### Run Specific Test Files
```bash
# Models tests only
python -m pytest tests/test_models.py -v

# Flask app tests only  
python -m pytest tests/test_app.py -v

# Setup script tests only
python -m pytest tests/test_setup.py -v
```

### Coverage Only (without running tests again)
```bash
coverage html
```

## Test Coverage Targets
- **Models**: 95%+ coverage of FeedbackModel class
- **Flask Routes**: 90%+ coverage of all endpoints  
- **Setup Script**: 85%+ coverage of setup functionality
- **Overall**: 90%+ total backend coverage

## Expected Test Results
- **Models**: ~35 tests covering CRUD operations, validation, edge cases
- **Flask App**: ~15 tests covering routes, forms, navigation
- **Setup**: ~10 tests covering database initialization

Total: **~60 comprehensive backend tests**

## View Coverage Report
After running tests with coverage, open:
```bash
open htmlcov/index.html
```

Or check the terminal output for coverage percentages.
