from pydantic import BaseModel, Field
from typing import Literal


class JobSearchParams(BaseModel):
    # Required fields
    search_term: str = Field(
        description="The job title or keywords to search for",
    )
    location: str = Field(
        description="The location to search for jobs",
    )

    # Optional fields with sensible defaults
    distance: int = Field(
        default=0,
        ge=0,
        description="Search radius in miles from the specified location",
    )
    job_type: Literal["fulltime", "parttime", "internship", "contract"] | None = Field(
        default=None,
        description="Type of employment to filter by (optional)"
    )
    is_remote: bool = Field(
        default=False,
        description="Whether to include remote job opportunities"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of results to skip (for pagination)"
    )
    results_wanted: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of job results to return (1-100)",
    )
    hours_old: int = Field(
        default=24,
        ge=1,
        description="Only return jobs posted within this many hours",
    )


class Job(BaseModel):
    id: str | None = Field(
        default=None,
        description="Unique job identifier"
    )
    job_url: str | None = Field(
        default=None,
        description="URL to the job posting"
    )
    job_url_direct: str | None = Field(
        default=None,
        description="Direct URL to apply for the job"
    )
    location: str | None = Field(
        default=None,
        description="Job location (city, state/country, or 'Remote')",
    )
    title: str | None = Field(
        default=None,
        description="Job title",
    )
    company: str | None = Field(
        default=None,
        description="Company name",
    )
    job_type: str | None = Field(
        default=None,
        description="Employment type",
    )
    is_remote: bool | None = Field(
        default=None,
        description="Whether the job is remote/work-from-home"
    )
    description: str | None = Field(
        default=None,
        description="Job description in markdown format"
    )
