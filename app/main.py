from fastapi import FastAPI, Depends, Query
from typing import Annotated
from app.scrape_jobs import get_jobs
from app.models import Job, JobSearchParams

app = FastAPI(
    title="Job Scraper API",
    description="A FastAPI application for scraping job listings from various job boards",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get(
    "/jobs",
    response_model=list[Job],
)
async def search_jobs(
    params: Annotated[JobSearchParams, Query()]
) -> list[Job]:
    return get_jobs(params)
