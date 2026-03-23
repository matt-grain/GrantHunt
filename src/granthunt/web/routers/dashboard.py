"""Dashboard routes — pipeline and kanban views."""

from __future__ import annotations

import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from granthunt.db import list_jobs
from granthunt.models import Job, JobStatus
from ..dependencies import get_db, get_templates

router = APIRouter()

DBDep = Annotated[sqlite3.Connection, Depends(get_db)]
TemplatesDep = Annotated[Jinja2Templates, Depends(get_templates)]


def _group_jobs_by_status(jobs: list[Job]) -> dict[JobStatus, list[Job]]:
    """Group a flat list of jobs into a dict keyed by JobStatus."""
    grouped: dict[JobStatus, list[Job]] = {status: [] for status in JobStatus}
    for job in jobs:
        grouped[job.status].append(job)
    return grouped


@router.get("/", response_class=HTMLResponse)
async def pipeline_view(
    request: Request,
    conn: DBDep,
) -> HTMLResponse:
    """Render the main pipeline dashboard."""
    templates = get_templates(request)
    jobs = list_jobs(conn)
    jobs_by_status = _group_jobs_by_status(jobs)
    status_counts = {status: len(jobs_by_status[status]) for status in JobStatus}

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "jobs_by_status": jobs_by_status,
            "status_counts": status_counts,
        },
    )


@router.get("/kanban", response_class=HTMLResponse)
async def kanban_view(
    request: Request,
    conn: DBDep,
) -> HTMLResponse:
    """Render the kanban board view."""
    templates = get_templates(request)
    jobs = list_jobs(conn)
    jobs_by_status = _group_jobs_by_status(jobs)

    return templates.TemplateResponse(
        "kanban.html",
        {
            "request": request,
            "jobs_by_status": jobs_by_status,
        },
    )
