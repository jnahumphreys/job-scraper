# Job Scraper API

A FastAPI application for scraping job listings from LinkedIn.

![Tests](https://github.com/jnahumphreys/job-scraper/actions/workflows/test.yml/badge.svg)

## Features

- **FastAPI Framework**: High-performance, modern web framework
- **Job Scraping**: Scrapes job listings from LinkedIn using JobSpy
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

### Continuous Integration

The project uses GitHub Actions for continuous integration:

- **Automated Testing**: Tests run on every pull request to main branch
- **Multi-Python Support**: Tests against Python 3.10, 3.11, and 3.12
- **Coverage Reporting**: Coverage reports are uploaded to Codecov
- **PR Comments**: Coverage reports are automatically commented on pull requests
- **Artifacts**: HTML coverage reports are saved as downloadable artifacts

#### Setting up Codecov (Optional)

To enable coverage reporting to Codecov:

1. Sign up at [codecov.io](https://codecov.io) and connect your repository
2. Add your Codecov token as a GitHub secret named `CODECOV_TOKEN`
3. Coverage reports will be automatically uploaded on every test run

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

## Docker Deployment

### Using Pre-built Image

Pull and run the latest image from GitHub Container Registry:

```bash
docker run -p 8000:8000 ghcr.io/jnahumphreys/job-scraper:latest
```

### Using Docker Compose

Requires pulling the repository:

```bash
git clone https://github.com/jnahumphreys/job-scraper.git
cd job-scraper
docker compose up -d
```

### Available Image Tags

- `latest`: Latest released version
- `v*`: Specific version releases (e.g., `v1.0.0`, `v1.2.3`)
- Version variations: `v1.2.3`, `v1.2`, `v1` (created automatically from releases)

## Development

### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Acknowledgments

We would like to express our gratitude to the maintainers and contributors of [JobSpy](https://github.com/cullenwatson/JobSpy), the powerful job scraping library that makes this project possible. JobSpy provides robust scraping capabilities for major job platforms including Indeed, LinkedIn, ZipRecruiter, Glassdoor, and Google Jobs.

Special thanks to:
- The JobSpy development team for creating and maintaining this excellent tool
- All contributors who help improve the library
- The open-source community that supports job search automation

Their work enables developers to build job search and analysis tools more efficiently.