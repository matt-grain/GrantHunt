from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class JobStatus(StrEnum):
    NEW = "NEW"
    INTERESTED = "INTERESTED"
    APPLIED = "APPLIED"
    INTERVIEWING = "INTERVIEWING"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


class ProspectStatus(StrEnum):
    PENDING = "PENDING"
    DISMISSED = "DISMISSED"
    TRACKED = "TRACKED"


class Job(BaseModel):
    id: int
    url: str
    title: str
    company: str
    location: str | None = None
    status: JobStatus = JobStatus.NEW
    score: float | None = None
    notes: str | None = None
    date_added: datetime
    date_updated: datetime
    raw_description: str | None = None


class JobCreate(BaseModel):
    url: str
    title: str
    company: str
    location: str | None = None
    notes: str | None = None


class JobUpdate(BaseModel):
    status: JobStatus | None = None
    score: float | None = None
    notes: str | None = None


class JobProspect(BaseModel):
    id: int
    url: str
    title: str
    company: str
    location: str | None = None
    summary: str | None = None
    salary: str | None = None
    quick_score: float | None = None
    source: str = "linkedin"
    external_id: str | None = None
    status: ProspectStatus = ProspectStatus.PENDING
    job_id: int | None = None
    discovered_at: datetime


class ScrapeHistory(BaseModel):
    id: int
    source: str
    query: str | None = None
    scraped_at: datetime
    jobs_found: int = 0
    new_jobs: int = 0


class ProspectCreate(BaseModel):
    url: str
    title: str
    company: str
    location: str | None = None
    summary: str | None = None
    salary: str | None = None
    quick_score: float | None = None
    source: str = "linkedin"
    external_id: str | None = None


class ProspectUpdate(BaseModel):
    status: ProspectStatus | None = None
    job_id: int | None = None
