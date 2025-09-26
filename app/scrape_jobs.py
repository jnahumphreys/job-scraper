import pandas as pd
from jobspy import scrape_jobs
from app.models import JobSearchParams, Job
from app.proxy_manager import proxy_manager
from app.config import settings
from typing import List
import logging

logger = logging.getLogger(__name__)


def get_jobs(params: JobSearchParams) -> List[Job]:
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
                        return []
                    else:
                        logger.info(
                            "Continuing without proxies (fallback enabled)")
            except Exception as e:
                logger.warning(f"Failed to get proxies: {e}")
                if not settings.PROXY_FALLBACK_ENABLED:
                    logger.error(
                        "PROXY_FALLBACK_ENABLED is false and failed to get proxies. "
                        "Aborting scrape to prevent rate limiting.")
                    return []
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
        return validated_jobs

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
                return validated_jobs
            except Exception as fallback_error:
                logger.error(
                    f"Fallback scraping also failed: {str(fallback_error)}")
                return []
        else:
            logger.error(f"Error scraping jobs: {str(e)}")
            # Return empty list instead of raising exception to prevent API errors
            return []
