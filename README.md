# Job Scraper API

A FastAPI application for scraping job listings from various job boards.

## Features

- **FastAPI Framework**: High-performance, modern web framework
- **Job Scraping**: Scrapes job listings from LinkedIn using jobspy
- **Pydantic Models**: Strong data validation and serialization
- **Comprehensive Testing**: Full test suite with mocking for external dependencies

## API Endpoints

### GET /jobs

Search for job listings with the following parameters:

- `search_term` (required): The job title or keywords to search for
- `location` (required): The location to search for jobs
- `distance` (optional): Search radius in miles from the specified location (default: 0)
- `job_type` (optional): Type of employment - "fulltime", "parttime", "internship", or "contract"
- `is_remote` (optional): Whether to include remote job opportunities (default: false)
- `offset` (optional): Number of results to skip for pagination (default: 0)
- `results_wanted` (optional): Maximum number of job results to return, 1-100 (default: 10)
- `hours_old` (optional): Only return jobs posted within this many hours (default: 24)

## Installation

### Using VS Code Dev Container (Recommended)

If you're using VS Code with the dev container setup, all dependencies are automatically installed and configured for you. Simply:

1. Open the project in VS Code
2. When prompted, click "Reopen in Container" or use the Command Palette (`Ctrl+Shift+P`) and select "Dev Containers: Reopen in Container"
3. The container will build and install all dependencies automatically

### Manual Installation

If you're not using the dev container:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

2. Run the development server:
```bash
fastapi dev app/main.py
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## Testing

The project includes a comprehensive test suite that covers:

- API endpoint validation
- Parameter validation
- Error handling
- Model validation
- External dependency mocking

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app

# Run tests with detailed coverage report
pytest --cov=app --cov-report=term-missing

# Run tests in verbose mode
pytest -v

# Run specific test file
pytest app/test_main.py
```

### Test Structure

- `app/test_main.py`: Main test file containing all API and model tests
- Tests use `FastAPI TestClient` for endpoint testing
- External dependencies (jobspy) are mocked using `unittest.mock`
- Parameterized tests cover various input combinations
- Model validation tests ensure Pydantic models work correctly

### Test Coverage

The test suite achieves 100% code coverage, testing:

- All API endpoints and their responses
- Parameter validation and error handling
- Model creation and validation
- External service failure scenarios
- Different parameter combinations

## Project Structure

```
job-scraper/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── models.py        # Pydantic models
│   ├── scrape_jobs.py   # Job scraping logic
│   └── test_main.py     # Test suite
├── requirements.txt     # Python dependencies
├── pyproject.toml      # Pytest configuration
└── README.md           # This file
```

## Development

The application is containerized with Docker. See `Dockerfile` and `compose.yml` for container setup.

### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`