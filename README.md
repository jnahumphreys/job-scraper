# JobSpy API

A FastAPI application for scraping job listings from LinkedIn using the JobSpy package with **automatic proxy support**.

![Tests](https://github.com/jnahumphreys/job-scraper/actions/workflows/test.yml/badge.svg)
[![codecov](https://codecov.io/github/jnahumphreys/job-scraper/graph/badge.svg?token=LCI4JMRK6O)](https://codecov.io/github/jnahumphreys/job-scraper)

## Features

- **Job Scraping**: Scrapes job listings from LinkedIn using the powerful JobSpy library
- **Automatic Proxy Support**: Built-in free proxy rotation to avoid rate limiting and IP blocks
- **Zero Configuration**: Works out of the box with sensible defaults
- **Rate Limit Protection**: Defaults to not scraping without proxies to protect users from rate limiting
- **REST API**: Clean, documented API endpoints for easy integration
- **Docker Ready**: Pre-built Docker images available for instant deployment

## Supporting the Project

If this project has been helpful in your workflow and you'd like to support my open-source work, please consider making a small donation. Thank you! 🙏

[![Buy me a coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=jnahumphreys&button_colour=FFDD00&font_colour=000000&font_family=Lato&outline_colour=000000&coffee_colour=ffffff)](https://www.buymeacoffee.com/jnahumphreys)

## Roadmap

- [x] LinkedIn job scraping with proxy support
- [ ] Support for Indeed job scraping
- [ ] Support for Google Jobs scraping

## Quick Start

### Pre-built Docker image

Pull and run the latest Docker image from GitHub Container Registry:

```bash
# Run with default settings (proxy support enabled)
docker run -p 8000:8000 ghcr.io/jnahumphreys/job-scraper:latest
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
services:
  job-scraper:
    image: ghcr.io/jnahumphreys/job-scraper:latest
    container_name: job-scraper
    ports:
      - "8000:8000"
    restart: unless-stopped
```

Run with:
```bash
docker compose up -d
```

## Configuration

**Proxy support is enabled by default** - no configuration required! The system automatically fetches free proxies and falls back to direct scraping if needed.

### Environment Variables

You can customize the behavior with these optional environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_PROXIES` | `true` | Enable/disable proxy support |
| `PROXY_UPDATE_INTERVAL` | `300` | Proxy refresh interval (seconds) |
| `MAX_PROXY_WORKERS` | `20` | Concurrent proxy validation workers |
| `MAX_WORKING_PROXIES` | `10` | Maximum working proxies to maintain |
| `PROXY_FALLBACK_ENABLED` | `false` | Enable fallback to direct scraping (disabled by default to prevent rate limiting) |

### Configuration Examples

**Disable proxy support:**
```bash
docker run -p 8000:8000 -e USE_PROXIES=false ghcr.io/jnahumphreys/job-scraper:latest
```

**Custom proxy settings:**
```bash
docker run -p 8000:8000 \
  -e PROXY_UPDATE_INTERVAL=600 \
  -e MAX_WORKING_PROXIES=5 \
  ghcr.io/jnahumphreys/job-scraper:latest
```

**Enable fallback to direct scraping (not recommended - may cause rate limiting):**
```bash
docker run -p 8000:8000 -e PROXY_FALLBACK_ENABLED=true ghcr.io/jnahumphreys/job-scraper:latest
```

**Using .env file with Docker Compose:**

Create `.env` file:
```bash
USE_PROXIES=true
PROXY_UPDATE_INTERVAL=300
MAX_WORKING_PROXIES=10
PROXY_FALLBACK_ENABLED=false  # Default: false (recommended for rate limit protection)
```

Update `docker-compose.yml`:
```yaml
services:
  job-scraper:
    image: ghcr.io/jnahumphreys/job-scraper:latest
    container_name: job-scraper
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
```

## API Reference

### Job Search Endpoint

**`GET /jobs`**

Search for job listings with the following parameters:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `search_term` | string | Yes | - | Job title or keywords to search for |
| `location` | string | Yes | - | Location to search for jobs |
| `distance` | integer | No | `0` | Search radius in miles from location |
| `job_type` | string | No | - | Employment type (`fulltime`, `parttime`, `internship`, `contract`) |
| `is_remote` | boolean | No | `false` | Include remote job opportunities |
| `offset` | integer | No | `0` | Number of results to skip for pagination |
| `results_wanted` | integer | No | `10` | Maximum results to return (1-100) |
| `hours_old` | integer | No | `24` | Only return jobs posted within this many hours |

**Example Request:**
```bash
curl "http://localhost:8000/jobs?search_term=python%20developer&location=New%20York&results_wanted=5"
```

**Example Response:**
```json
[
  {
    "id": "123456789",
    "title": "Senior Python Developer",
    "company": "Tech Corp",
    "location": "New York, NY",
    "job_url": "https://linkedin.com/jobs/view/123456789",
    "job_url_direct": "https://tech-corp.com/jobs/123456789",
    "job_type": "fulltime",
    "description": "We are looking for a Senior Python Developer...",
    "is_remote": false,
  }
]
```

Note: the `description` will be returned as Markdown

### Proxy Health Endpoint

**`GET /health/proxies`**

Check the status of the proxy system:

```bash
curl http://localhost:8000/health/proxies
```

**Response:**
```json
{
  "proxy_system_enabled": true,
  "working_proxies": 3,
  "last_update": 1695123456,
  "status": "healthy"
}
```

### Proxy Refresh Endpoint

**`POST /admin/refresh-proxies`**

Manually refresh the proxy list:

```bash
curl -X POST http://localhost:8000/admin/refresh-proxies
```

**Response:**
```json
{
  "message": "Proxy list refreshed",
  "working_proxies": 5
}
```

### Interactive Documentation

Once running, visit these URLs for interactive API documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## FAQ

### General Questions

**Q: What job sites are supported?** \
A: Currently, the API supports LinkedIn job scraping. Support for Indeed and Google Jobs is planned.

**Q: How many jobs can I scrape at once?** \
A: You can request up to 100 jobs per API call using the `results_wanted` parameter.

**Q: Are there rate limits?** \
A: The built-in proxy system helps avoid rate limits. By default, the application will not scrape if no proxies are available (`PROXY_FALLBACK_ENABLED=false`) to protect users from rate limiting. You can enable fallback by setting `PROXY_FALLBACK_ENABLED=true`.

### Proxy Questions

**Q: Do I need to configure proxies?** \
A: No! Proxy support is enabled by default and works automatically with free proxy lists.

**Q: My scraping is slow or failing frequently** \
A: Check proxy health with `GET /health/proxies`. If no working proxies are found, the system automatically falls back to direct scraping.

**Q: How do I disable proxy support?** \
A: Set the environment variable `USE_PROXIES=false` when running the container.

**Q: Can I use my own proxy servers?** \
A: Currently, the system uses free proxy lists from Proxifly. Custom proxy support would require code modifications.

**Q: The proxy system isn't finding any working proxies** \
A: This is normal for free proxy lists. By default, the application will return an empty result set when no proxies are available to protect you from rate limiting. You can enable fallback to direct scraping by setting `PROXY_FALLBACK_ENABLED=true`. You can manually refresh proxies using `POST /admin/refresh-proxies`.

**Q: My scraping returns empty results when proxies fail** \
A: This is the default behavior to protect users from rate limiting. When `PROXY_FALLBACK_ENABLED=false` (default), the application won't scrape without proxies. Set `PROXY_FALLBACK_ENABLED=true` to enable fallback to direct scraping at your own risk.

### Docker Questions

**Q: What Docker tags are available?** \
A: Available tags include `latest` (most recent), and specific versions like `v1.0.0`, `v1.2.3`.

**Q: How do I update to the latest version?** \
A: Pull the latest image: `docker pull ghcr.io/jnahumphreys/job-scraper:latest` and restart your container.

**Q: Can I run this without Docker?**\ 
A: Yes, but Docker is recommended for easier deployment. You would need to manually install Python dependencies and run the FastAPI application.

## Acknowledgments

I would like to express my gratitude to the maintainers and contributors of [JobSpy](https://github.com/cullenwatson/JobSpy), the powerful job scraping library that makes this project possible. JobSpy provides robust scraping capabilities for major job platforms including Indeed, LinkedIn, ZipRecruiter, Glassdoor, and Google Jobs.

Special thanks to:
- The JobSpy development team for creating and maintaining this excellent tool
- All contributors who help improve the library
- The open-source community that supports job search automation
- [Proxifly](https://github.com/proxifly/free-proxy-list) for maintaining free proxy lists

Their work enables developers to build job search and analysis tools more efficiently.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.