import pandas as pd
from jobspy import scrape_jobs
from app.models import JobSearchParams, Job
from typing import List
import logging

logger = logging.getLogger(__name__)


def get_jobs(params: JobSearchParams) -> List[Job]:
    try:
        logger.info(
            f"Scraping jobs for: {params.search_term} in {params.location}")

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
            "linkedin_fetch_description": True
        }

        # Only add job_type if it's specified
        if params.job_type is not None:
            scrape_kwargs["job_type"] = params.job_type

        # Scrape jobs from LinkedIn
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
        logger.error(f"Error scraping jobs: {str(e)}")
        # Return empty list instead of raising exception to prevent API errors
        return []
