from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import pytest
from app.main import app
from app.models import Job, JobSearchParams

client = TestClient(app)


def test_api_docs_available():
    """Test that API documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_jobs_endpoint_requires_parameters():
    """Test that the /jobs endpoint requires search_term and location"""
    response = client.get("/jobs")
    assert response.status_code == 422  # Validation error for missing required fields


def test_jobs_endpoint_validates_parameters():
    """Test parameter validation"""
    response = client.get("/jobs", params={
        "search_term": "python developer",
        "location": "New York",
        "results_wanted": 150  # Over the limit of 100
    })
    assert response.status_code == 422  # Validation error


@patch('app.scrape_jobs.scrape_jobs')
def test_jobs_endpoint_success(mock_scrape_jobs):
    """Test successful job retrieval with mocked data"""
    # Mock the pandas DataFrame that scrape_jobs returns
    mock_df = Mock()
    mock_df.astype.return_value.where.return_value = mock_df
    mock_df.to_dict.return_value = [
        {
            "id": "123",
            "title": "Python Developer",
            "company": "Tech Corp",
            "location": "New York, NY",
            "job_url": "https://example.com/job/123",
            "job_url_direct": "https://example.com/apply/123",
            "job_type": "fulltime",
            "description": "Great Python job"
        }
    ]
    mock_scrape_jobs.return_value = mock_df

    response = client.get("/jobs", params={
        "search_term": "python developer",
        "location": "New York"
    })

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Python Developer"
    assert data[0]["company"] == "Tech Corp"
    assert data[0]["location"] == "New York, NY"


@patch('app.scrape_jobs.scrape_jobs')
def test_jobs_endpoint_handles_scraping_failure(mock_scrape_jobs):
    """Test that API handles scraping failures gracefully"""
    # Mock scrape_jobs to raise an exception
    mock_scrape_jobs.side_effect = Exception("LinkedIn is down")

    response = client.get("/jobs", params={
        "search_term": "python developer",
        "location": "New York"
    })

    # Your get_jobs function returns empty list on error
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("params,expected_status", [
    ({"search_term": "developer", "location": "NYC"}, 200),
    ({"search_term": "developer", "location": "NYC", "job_type": "fulltime"}, 200),
    ({"search_term": "developer", "location": "NYC", "is_remote": True}, 200),
    ({"search_term": "developer", "location": "NYC", "distance": 25}, 200),
    ({"search_term": "developer", "location": "NYC", "results_wanted": 50}, 200),
    # Empty search term is allowed by current model
    ({"search_term": "", "location": "NYC"}, 200),
    # Empty location is allowed by current model
    ({"search_term": "developer", "location": ""}, 200),
    ({"search_term": "developer", "location": "NYC",
     "results_wanted": 0}, 422),  # Invalid results_wanted
])
@patch('app.scrape_jobs.scrape_jobs')
def test_parameter_combinations(mock_scrape_jobs, params, expected_status):
    """Test various parameter combinations"""
    if expected_status == 200:
        mock_df = Mock()
        mock_df.astype.return_value.where.return_value = mock_df
        mock_df.to_dict.return_value = []
        mock_scrape_jobs.return_value = mock_df

    response = client.get("/jobs", params=params)
    assert response.status_code == expected_status


def test_job_model_validation():
    """Test Job model accepts valid data"""
    job_data = {
        "id": "123",
        "title": "Python Developer",
        "company": "Tech Corp",
        "location": "New York, NY",
        "job_url": "https://example.com/job/123",
        "job_type": "fulltime",
        "description": "Great Python job"
    }
    job = Job(**job_data)
    assert job.title == "Python Developer"
    assert job.company == "Tech Corp"
    assert job.location == "New York, NY"


def test_job_model_accepts_none_values():
    """Test Job model accepts None for optional fields"""
    job_data = {
        "id": None,
        "title": None,
        "company": None,
        "location": None,
        "job_url": None,
        "job_url_direct": None,
        "job_type": None,
        "description": None
    }
    job = Job(**job_data)
    assert job.title is None
    assert job.company is None


def test_job_search_params_defaults():
    """Test JobSearchParams has correct defaults"""
    params = JobSearchParams(search_term="developer", location="NYC")
    assert params.distance == 0
    assert params.results_wanted == 10
    assert params.hours_old == 24
    assert params.is_remote is False
    assert params.job_type is None
    assert params.offset == 0


def test_job_search_params_validation():
    """Test JobSearchParams validation rules"""
    # Test valid parameters
    params = JobSearchParams(
        search_term="python developer",
        location="New York",
        distance=25,
        job_type="fulltime",
        is_remote=True,
        results_wanted=50,
        hours_old=48
    )
    assert params.search_term == "python developer"
    assert params.location == "New York"
    assert params.distance == 25
    assert params.job_type == "fulltime"
    assert params.is_remote is True
    assert params.results_wanted == 50
    assert params.hours_old == 48


def test_job_search_params_validation_errors():
    """Test JobSearchParams validation catches invalid values"""
    with pytest.raises(ValueError):
        # Invalid job_type
        JobSearchParams(
            search_term="developer",
            location="NYC",
            job_type="invalid_type"
        )

    with pytest.raises(ValueError):
        # Invalid results_wanted (too high)
        JobSearchParams(
            search_term="developer",
            location="NYC",
            results_wanted=150
        )

    with pytest.raises(ValueError):
        # Invalid distance (negative)
        JobSearchParams(
            search_term="developer",
            location="NYC",
            distance=-5
        )


@patch('app.scrape_jobs.scrape_jobs')
def test_jobs_endpoint_with_all_parameters(mock_scrape_jobs):
    """Test jobs endpoint with all optional parameters"""
    mock_df = Mock()
    mock_df.astype.return_value.where.return_value = mock_df
    mock_df.to_dict.return_value = []
    mock_scrape_jobs.return_value = mock_df

    response = client.get("/jobs", params={
        "search_term": "senior python developer",
        "location": "San Francisco",
        "distance": 50,
        "job_type": "fulltime",
        "is_remote": True,
        "offset": 20,
        "results_wanted": 25,
        "hours_old": 72
    })

    assert response.status_code == 200
    assert response.json() == []

    # Verify the mock was called with correct parameters
    mock_scrape_jobs.assert_called_once()
    call_kwargs = mock_scrape_jobs.call_args[1]
    assert call_kwargs["search_term"] == "senior python developer"
    assert call_kwargs["location"] == "San Francisco"
    assert call_kwargs["distance"] == 50
    assert call_kwargs["job_type"] == "fulltime"
    assert call_kwargs["is_remote"] is True
    assert call_kwargs["offset"] == 20
    assert call_kwargs["results_wanted"] == 25
    assert call_kwargs["hours_old"] == 72


@patch('app.scrape_jobs.scrape_jobs')
def test_jobs_endpoint_without_job_type(mock_scrape_jobs):
    """Test that job_type parameter is not passed when None"""
    mock_df = Mock()
    mock_df.astype.return_value.where.return_value = mock_df
    mock_df.to_dict.return_value = []
    mock_scrape_jobs.return_value = mock_df

    response = client.get("/jobs", params={
        "search_term": "developer",
        "location": "Austin"
    })

    assert response.status_code == 200

    # Verify job_type was not included in the call
    call_kwargs = mock_scrape_jobs.call_args[1]
    assert "job_type" not in call_kwargs or call_kwargs.get("job_type") is None
