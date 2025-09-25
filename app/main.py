from fastapi import FastAPI
from typing import Literal
from app.scrape_jobs import get_jobs
from pydantic import BaseModel

app = FastAPI()


class Job(BaseModel):
    id: str | None
    job_url: str | None
    job_url_direct: str | None
    location: str | None
    title: str | None
    company: str | None
    job_type: str | None
    description: str | None


@app.get("/jobs")
async def jobs(search_term: str, location: str = "london", distance: int = 5, job_type: Literal["fulltime", "parttime", "internship", "contract"] = None, results_wanted: int = 10, hours_old: int = 24) -> list[Job]:
    return get_jobs(search_term, location, distance, job_type, results_wanted, hours_old)
