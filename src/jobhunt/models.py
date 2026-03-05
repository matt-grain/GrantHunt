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
