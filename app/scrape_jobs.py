import pandas as pd
from jobspy import scrape_jobs
from app.models import JobSearchParams, Job, JobSearchResponse, ScrapingError
from app.proxy_manager import proxy_manager
from app.config import settings
from typing import List
import logging

logger = logging.getLogger(__name__)


def get_jobs(params: JobSearchParams) -> JobSearchResponse:
    try:
        logger.info(
            f"Scraping jobs for: {params.search_term} in {params.location}")

        # Get proxy list automatically if enabled
        proxies = None
        if settings.USE_PROXIES:
            try:
                proxies = proxy_manager.get_proxy_list()
                if proxies:
                    logger.info(f"Using {len(proxies)} proxies for scraping")
                else:
                    logger.warning("No working proxies available")
                    if not settings.PROXY_FALLBACK_ENABLED:
                        logger.error(
                            "PROXY_FALLBACK_ENABLED is false and no proxies are available. "
                            "Aborting scrape to prevent rate limiting.")
                        return JobSearchResponse(
                            success=False,
                            jobs=[],
                            error=ScrapingError(
                                error_type="proxy_unavailable",
                                message="No working proxies available and fallback is disabled",
                                details={
                                    "proxy_system_enabled": settings.USE_PROXIES,
                                    "fallback_enabled": settings.PROXY_FALLBACK_ENABLED,
                                    "working_proxies": 0
                                },
                                suggested_actions=[
                                    "Try refreshing the proxy list: POST /admin/refresh-proxies",
                                    "Enable fallback scraping: set PROXY_FALLBACK_ENABLED=true (may cause rate limiting)",
                                    "Check proxy system health: GET /health/proxies",
                                    "Wait a few minutes and try again as new proxies may become available"
                                ]
                            )
                        )
                    else:
                        logger.info(
                            "Continuing without proxies (fallback enabled)")
            except Exception as e:
                logger.warning(f"Failed to get proxies: {e}")
                if not settings.PROXY_FALLBACK_ENABLED:
                    logger.error(
                        "PROXY_FALLBACK_ENABLED is false and failed to get proxies. "
                        "Aborting scrape to prevent rate limiting.")
                    return JobSearchResponse(
                        success=False,
                        jobs=[],
                        error=ScrapingError(
                            error_type="proxy_fetch_failed",
                            message=f"Failed to fetch proxies and fallback is disabled: {str(e)}",
                            details={
                                "proxy_system_enabled": settings.USE_PROXIES,
                                "fallback_enabled": settings.PROXY_FALLBACK_ENABLED,
                                "error_details": str(e)
                            },
                            suggested_actions=[
                                "Check network connectivity",
                                "Try refreshing the proxy list: POST /admin/refresh-proxies",
                                "Enable fallback scraping: set PROXY_FALLBACK_ENABLED=true (may cause rate limiting)",
                                "Check proxy system health: GET /health/proxies"
                            ]
                        )
                    )
                else:
                    logger.info(
                        "Continuing without proxies (fallback enabled)")

        # Build kwargs dict, only excluding job_type if None
        scrape_kwargs = {
            "site_name": "linkedin",
            "search_term": params.search_term,
            "location": params.location,
            "distance": params.distance,
            "results_wanted": params.results_wanted,
            "hours_old": params.hours_old,
            "offset": params.offset,
            "is_remote": params.is_remote,
            "description_format": "markdown",
            "linkedin_fetch_description": True,
            "proxies": proxies  # Add proxy support
        }

        # Only add job_type if it's specified
        if params.job_type is not None:
            scrape_kwargs["job_type"] = params.job_type

        # Scrape jobs from LinkedIn with proxy support
        jobs_df = scrape_jobs(**scrape_kwargs)

        # Normalize null values to None for Pydantic compatibility
        jobs_df = jobs_df.astype(object).where(pd.notnull(jobs_df), None)

        # Convert to list of dictionaries
        jobs_list = jobs_df.to_dict(orient="records")

        # Convert to Pydantic models for validation
        validated_jobs = [Job(**job_data) for job_data in jobs_list]

        logger.info(f"Successfully scraped {len(validated_jobs)} jobs")
        return JobSearchResponse(
            success=True,
            jobs=validated_jobs,
            metadata={
                "total_results": len(validated_jobs),
                "used_proxies": len(proxies) if proxies else 0,
                "proxy_enabled": settings.USE_PROXIES,
                "search_params": {
                    "search_term": params.search_term,
                    "location": params.location,
                    "results_wanted": params.results_wanted
                }
            }
        )

    except Exception as e:
        # If scraping fails with proxies, retry without them
        if proxies and settings.PROXY_FALLBACK_ENABLED and "proxy" in str(e).lower():
            logger.warning(f"Proxy scraping failed: {e}")
            logger.info("Retrying without proxies...")

            try:
                # Remove proxies from kwargs and retry
                scrape_kwargs["proxies"] = None
                jobs_df = scrape_jobs(**scrape_kwargs)

                # Normalize null values to None for Pydantic compatibility
                jobs_df = jobs_df.astype(object).where(
                    pd.notnull(jobs_df), None)

                # Convert to list of dictionaries
                jobs_list = jobs_df.to_dict(orient="records")

                # Convert to Pydantic models for validation
                validated_jobs = [Job(**job_data) for job_data in jobs_list]

                logger.info(
                    f"Successfully scraped {len(validated_jobs)} jobs without proxies")
                return JobSearchResponse(
                    success=True,
                    jobs=validated_jobs,
                    metadata={
                        "total_results": len(validated_jobs),
                        "used_proxies": 0,
                        "proxy_enabled": settings.USE_PROXIES,
                        "fallback_used": True,
                        "original_error": str(e),
                        "search_params": {
                            "search_term": params.search_term,
                            "location": params.location,
                            "results_wanted": params.results_wanted
                        }
                    }
                )
            except Exception as fallback_error:
                logger.error(
                    f"Fallback scraping also failed: {str(fallback_error)}")
                return JobSearchResponse(
                    success=False,
                    jobs=[],
                    error=ScrapingError(
                        error_type="scraping_failed",
                        message="Both proxy and fallback scraping failed",
                        details={
                            "original_error": str(e),
                            "fallback_error": str(fallback_error),
                            "proxy_enabled": settings.USE_PROXIES,
                            "fallback_enabled": settings.PROXY_FALLBACK_ENABLED
                        },
                        suggested_actions=[
                            "Check network connectivity",
                            "Verify search parameters are valid",
                            "Try again in a few minutes",
                            "Check service status: GET /health/proxies"
                        ]
                    )
                )
        else:
            # Determine error type based on context
            if settings.PROXY_FALLBACK_ENABLED:
                error_type = "scraping_failed"
                message = f"Scraping failed: {str(e)}"
                suggested_actions = [
                    "Check network connectivity",
                    "Verify search parameters are valid",
                    "Try again in a few minutes",
                    "Check if LinkedIn is accessible"
                ]
            else:
                error_type = "scraping_failed"
                message = f"Scraping failed and fallback is disabled: {str(e)}"
                suggested_actions = [
                    "Enable fallback scraping: set PROXY_FALLBACK_ENABLED=true",
                    "Check proxy system: GET /health/proxies",
                    "Try refreshing proxies: POST /admin/refresh-proxies",
                    "Verify search parameters are valid"
                ]

            logger.error(f"Error scraping jobs: {str(e)}")
            return JobSearchResponse(
                success=False,
                jobs=[],
                error=ScrapingError(
                    error_type=error_type,
                    message=message,
                    details={
                        "error": str(e),
                        "proxy_enabled": settings.USE_PROXIES,
                        "fallback_enabled": settings.PROXY_FALLBACK_ENABLED,
                        "had_proxies": proxies is not None and len(proxies) > 0
                    },
                    suggested_actions=suggested_actions
                )
            )
