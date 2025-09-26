from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Annotated
from app.scrape_jobs import get_jobs
from app.models import Job, JobSearchParams, JobSearchResponse
from app.proxy_manager import proxy_manager

app = FastAPI(
    title="JobSpy API",
    description="A FastAPI application for scraping job listings from LinkedIn using JobSpy with automatic proxy support",
    version="0.2.0-beta.1",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get(
    "/jobs",
    response_model=JobSearchResponse,
)
async def search_jobs(
    params: Annotated[JobSearchParams, Query()]
) -> JobSearchResponse:
    return get_jobs(params)


@app.get("/health/proxies")
async def proxy_health():
    """Check proxy system health"""
    try:
        proxies = proxy_manager.get_proxy_list()

        return {
            "proxy_system_enabled": True,
            "working_proxies": len(proxies) if proxies else 0,
            "last_update": proxy_manager.last_update,
            "status": "healthy" if proxies else "no_proxies_available"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "proxy_system_enabled": True,
                "working_proxies": 0,
                "error": str(e),
                "status": "error"
            }
        )


@app.get("/health/scraping")
async def scraping_health():
    """Check if scraping is currently available"""
    from app.config import settings

    try:
        scraping_available = True
        reason = "Scraping is available"

        if settings.USE_PROXIES and not settings.PROXY_FALLBACK_ENABLED:
            proxies = proxy_manager.get_proxy_list()
            if not proxies:
                scraping_available = False
                reason = "Scraping unavailable: No working proxies and fallback disabled"

        return {
            "scraping_available": scraping_available,
            "use_proxies": settings.USE_PROXIES,
            "fallback_enabled": settings.PROXY_FALLBACK_ENABLED,
            "working_proxies": len(proxy_manager.get_proxy_list() or []),
            "reason": reason
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "scraping_available": False,
                "error": str(e),
                "reason": "Error checking scraping availability"
            }
        )


@app.post("/admin/refresh-proxies")
async def refresh_proxies():
    """Manually refresh proxy list (admin endpoint)"""
    try:
        proxies = proxy_manager.get_proxy_list(force_refresh=True)
        return {
            "message": "Proxy list refreshed",
            "working_proxies": len(proxies) if proxies else 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to refresh proxies: {str(e)}")
