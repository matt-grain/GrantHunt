from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class GrantStatus(StrEnum):
    DISCOVERED = "DISCOVERED"
    EVALUATING = "EVALUATING"
    PREPARING = "PREPARING"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


class ProspectStatus(StrEnum):
    PENDING = "PENDING"
    DISMISSED = "DISMISSED"
    TRACKED = "TRACKED"


class Grant(BaseModel):
    id: int
    url: str
    title: str
    organization: str
    program: str | None = None
    location: str | None = None
    status: GrantStatus = GrantStatus.DISCOVERED
    score: float | None = None
    notes: str | None = None
    raw_description: str | None = None
    deadline: datetime | None = None
    amount_min: float | None = None
    amount_max: float | None = None
    grant_type: str | None = None
    date_added: datetime
    date_updated: datetime


class GrantCreate(BaseModel):
    url: str
    title: str
    organization: str
    program: str | None = None
    location: str | None = None
    notes: str | None = None
    deadline: datetime | None = None
    amount_min: float | None = None
    amount_max: float | None = None
    grant_type: str | None = None


class GrantUpdate(BaseModel):
    status: GrantStatus | None = None
    score: float | None = None
    notes: str | None = None
    deadline: datetime | None = None


class GrantProspect(BaseModel):
    id: int
    url: str
    title: str
    organization: str
    program: str | None = None
    location: str | None = None
    summary: str | None = None
    amount_range: str | None = None
    deadline: str | None = None
    quick_score: float | None = None
    source: str = "innovation_canada"
    external_id: str | None = None
    status: ProspectStatus = ProspectStatus.PENDING
    grant_id: int | None = None
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
    organization: str
    program: str | None = None
    location: str | None = None
    summary: str | None = None
    amount_range: str | None = None
    deadline: str | None = None
    quick_score: float | None = None
    source: str = "innovation_canada"
    external_id: str | None = None


class ProspectUpdate(BaseModel):
    status: ProspectStatus | None = None
    grant_id: int | None = None
