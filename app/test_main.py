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
            "description": "Great Python job",
            "is_remote": False
        }
    ]
    mock_scrape_jobs.return_value = mock_df

    response = client.get("/jobs", params={
        "search_term": "python developer",
        "location": "New York"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["jobs"]) == 1
    assert data["jobs"][0]["title"] == "Python Developer"
    assert data["jobs"][0]["company"] == "Tech Corp"
    assert data["jobs"][0]["location"] == "New York, NY"
    assert data["jobs"][0]["is_remote"] is False


@patch('app.scrape_jobs.scrape_jobs')
def test_jobs_endpoint_returns_remote_jobs(mock_scrape_jobs):
    """Test that API returns is_remote field correctly for remote jobs"""
    # Mock the pandas DataFrame with remote job data
    mock_df = Mock()
    mock_df.astype.return_value.where.return_value = mock_df
    mock_df.to_dict.return_value = [
        {
            "id": "456",
            "title": "Remote Python Developer",
            "company": "Remote Corp",
            "location": "Remote",
            "job_url": "https://example.com/job/456",
            "job_url_direct": "https://example.com/apply/456",
            "job_type": "fulltime",
            "description": "Remote Python job",
            "is_remote": True
        }
    ]
    mock_scrape_jobs.return_value = mock_df

    response = client.get("/jobs", params={
        "search_term": "python developer",
        "location": "Remote",
        "is_remote": True
    })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["jobs"]) == 1
    assert data["jobs"][0]["title"] == "Remote Python Developer"
    assert data["jobs"][0]["company"] == "Remote Corp"
    assert data["jobs"][0]["location"] == "Remote"
    assert data["jobs"][0]["is_remote"] is True


@patch('app.scrape_jobs.scrape_jobs')
def test_jobs_endpoint_handles_scraping_failure(mock_scrape_jobs):
    """Test that API handles scraping failures gracefully"""
    # Mock scrape_jobs to raise an exception
    mock_scrape_jobs.side_effect = Exception("LinkedIn is down")

    response = client.get("/jobs", params={
        "search_term": "python developer",
        "location": "New York"
    })

    # The API should return a structured error response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["jobs"] == []
    assert data["error"] is not None
    assert data["error"]["error_type"] == "scraping_failed"
    assert "LinkedIn is down" in data["error"]["message"]


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
    # Test that is_remote defaults to None when not provided
    assert job.is_remote is None


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
        "is_remote": None,
        "description": None
    }
    job = Job(**job_data)
    assert job.title is None
    assert job.company is None
    assert job.is_remote is None


def test_job_model_with_is_remote():
    """Test Job model with is_remote field explicitly set"""
    job_data_remote = {
        "id": "123",
        "title": "Remote Python Developer",
        "company": "Remote Corp",
        "location": "Remote",
        "job_url": "https://example.com/job/123",
        "job_type": "fulltime",
        "description": "Remote Python job",
        "is_remote": True
    }
    job_remote = Job(**job_data_remote)
    assert job_remote.is_remote is True

    job_data_not_remote = {
        "id": "124",
        "title": "Onsite Python Developer",
        "company": "Local Corp",
        "location": "New York, NY",
        "job_url": "https://example.com/job/124",
        "job_type": "fulltime",
        "description": "Onsite Python job",
        "is_remote": False
    }
    job_not_remote = Job(**job_data_not_remote)
    assert job_not_remote.is_remote is False


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
    data = response.json()
    assert data["success"] is True
    assert data["jobs"] == []

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


# Proxy-related tests
@patch('app.main.proxy_manager')
def test_proxy_health_endpoint_success(mock_proxy_manager):
    """Test proxy health endpoint with working proxies"""
    mock_proxy_manager.get_proxy_list.return_value = [
        "http://proxy1:8080", "http://proxy2:8080"]
    mock_proxy_manager.last_update = 1234567890

    response = client.get("/health/proxies")

    assert response.status_code == 200
    data = response.json()
    assert data["proxy_system_enabled"] is True
    assert data["working_proxies"] == 2
    assert data["last_update"] == 1234567890
    assert data["status"] == "healthy"


@patch('app.main.proxy_manager')
def test_proxy_health_endpoint_no_proxies(mock_proxy_manager):
    """Test proxy health endpoint with no working proxies"""
    mock_proxy_manager.get_proxy_list.return_value = None
    mock_proxy_manager.last_update = 1234567890

    response = client.get("/health/proxies")

    assert response.status_code == 200
    data = response.json()
    assert data["proxy_system_enabled"] is True
    assert data["working_proxies"] == 0
    assert data["last_update"] == 1234567890
    assert data["status"] == "no_proxies_available"


@patch('app.main.proxy_manager')
def test_proxy_health_endpoint_error(mock_proxy_manager):
    """Test proxy health endpoint when proxy manager fails"""
    mock_proxy_manager.get_proxy_list.side_effect = Exception(
        "Proxy service error")

    response = client.get("/health/proxies")

    assert response.status_code == 500
    data = response.json()
    assert data["proxy_system_enabled"] is True
    assert data["working_proxies"] == 0
    assert "error" in data
    assert data["status"] == "error"


@patch('app.main.proxy_manager')
def test_refresh_proxies_endpoint_success(mock_proxy_manager):
    """Test proxy refresh endpoint success"""
    mock_proxy_manager.get_proxy_list.return_value = [
        "http://proxy1:8080", "http://proxy2:8080"]

    response = client.post("/admin/refresh-proxies")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Proxy list refreshed"
    assert data["working_proxies"] == 2
    mock_proxy_manager.get_proxy_list.assert_called_once_with(
        force_refresh=True)


@patch('app.main.proxy_manager')
def test_refresh_proxies_endpoint_error(mock_proxy_manager):
    """Test proxy refresh endpoint error handling"""
    mock_proxy_manager.get_proxy_list.side_effect = Exception("Refresh failed")

    response = client.post("/admin/refresh-proxies")

    assert response.status_code == 500
    data = response.json()
    assert "Failed to refresh proxies" in data["detail"]


@patch('app.scrape_jobs.scrape_jobs')
@patch('app.scrape_jobs.proxy_manager')
@patch('app.scrape_jobs.settings')
def test_jobs_endpoint_with_proxy_support(mock_settings, mock_proxy_manager, mock_scrape_jobs):
    """Test that jobs endpoint uses proxies when available"""
    mock_settings.USE_PROXIES = True
    mock_proxy_manager.get_proxy_list.return_value = [
        "http://proxy1:8080", "http://proxy2:8080"]

    mock_df = Mock()
    mock_df.astype.return_value.where.return_value = mock_df
    mock_df.to_dict.return_value = []
    mock_scrape_jobs.return_value = mock_df

    response = client.get("/jobs", params={
        "search_term": "python developer",
        "location": "New York"
    })

    assert response.status_code == 200

    # Verify proxies were passed to scrape_jobs
    call_kwargs = mock_scrape_jobs.call_args[1]
    assert call_kwargs["proxies"] == [
        "http://proxy1:8080", "http://proxy2:8080"]


@patch('app.scrape_jobs.scrape_jobs')
@patch('app.scrape_jobs.proxy_manager')
@patch('app.scrape_jobs.settings')
def test_jobs_endpoint_proxy_disabled(mock_settings, mock_proxy_manager, mock_scrape_jobs):
    """Test that jobs endpoint works without proxies when disabled"""
    mock_settings.USE_PROXIES = False

    mock_df = Mock()
    mock_df.astype.return_value.where.return_value = mock_df
    mock_df.to_dict.return_value = []
    mock_scrape_jobs.return_value = mock_df

    response = client.get("/jobs", params={
        "search_term": "python developer",
        "location": "New York"
    })

    assert response.status_code == 200

    # Verify proxies were not requested
    mock_proxy_manager.get_proxy_list.assert_not_called()

    # Verify proxies were not passed to scrape_jobs
    call_kwargs = mock_scrape_jobs.call_args[1]
    assert call_kwargs["proxies"] is None


@patch('app.scrape_jobs.proxy_manager')
@patch('app.scrape_jobs.settings')
def test_jobs_endpoint_no_proxies_fallback_disabled(mock_settings, mock_proxy_manager):
    """Test that jobs endpoint returns structured error when no proxies available and fallback disabled"""
    mock_settings.USE_PROXIES = True
    mock_settings.PROXY_FALLBACK_ENABLED = False
    mock_proxy_manager.get_proxy_list.return_value = None  # No proxies available

    response = client.get("/jobs", params={
        "search_term": "python developer",
        "location": "New York"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["jobs"] == []
    assert data["error"] is not None
    assert data["error"]["error_type"] == "proxy_unavailable"
    assert "No working proxies available" in data["error"]["message"]
    assert "POST /admin/refresh-proxies" in data["error"]["suggested_actions"][0]


@patch('app.scrape_jobs.scrape_jobs')
@patch('app.scrape_jobs.proxy_manager')
@patch('app.scrape_jobs.settings')
def test_jobs_endpoint_no_proxies_fallback_enabled(mock_settings, mock_proxy_manager, mock_scrape_jobs):
    """Test that jobs endpoint continues without proxies when fallback enabled"""
    mock_settings.USE_PROXIES = True
    mock_settings.PROXY_FALLBACK_ENABLED = True
    mock_proxy_manager.get_proxy_list.return_value = None  # No proxies available

    mock_df = Mock()
    mock_df.astype.return_value.where.return_value = mock_df
    mock_df.to_dict.return_value = []
    mock_scrape_jobs.return_value = mock_df

    response = client.get("/jobs", params={
        "search_term": "python developer",
        "location": "New York"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["jobs"] == []

    # Verify scrape_jobs was called without proxies
    call_kwargs = mock_scrape_jobs.call_args[1]
    assert call_kwargs["proxies"] is None


@patch('app.scrape_jobs.proxy_manager')
@patch('app.scrape_jobs.settings')
def test_jobs_endpoint_proxy_fetch_fails_fallback_disabled(mock_settings, mock_proxy_manager):
    """Test that jobs endpoint returns empty list when proxy fetch fails and fallback disabled"""
    mock_settings.USE_PROXIES = True
    mock_settings.PROXY_FALLBACK_ENABLED = False
    mock_proxy_manager.get_proxy_list.side_effect = Exception(
        "Proxy service unavailable")

    response = client.get("/jobs", params={
        "search_term": "python developer",
        "location": "New York"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["jobs"] == []
    assert data["error"] is not None
    assert data["error"]["error_type"] == "proxy_fetch_failed"
    assert "Failed to fetch proxies" in data["error"]["message"]
    assert "Proxy service unavailable" in data["error"]["message"]
