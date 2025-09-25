import pandas as pd
from typing import Literal
from jobspy import scrape_jobs


def get_jobs(
    search_term: str,
    location: str = None,
    distance: int = None,
    job_type: Literal["fulltime",
                      "parttime", "internship", "contract"] = None,
    results_wanted: int = None,
    hours_old: int = None
):
    jobs = scrape_jobs(
        site_name="linkedin",
        search_term=search_term,
        location=location,
        distance=distance,
        job_type=job_type,
        results_wanted=results_wanted,
        hours_old=hours_old,
        description_format="markdown",
        linkedin_fetch_description=True
    )
    jobs = jobs.astype(object).where(pd.notnull(jobs), None)  # ← normalize nulls
    return jobs.to_dict(orient="records")