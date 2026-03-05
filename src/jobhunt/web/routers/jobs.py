"""Job CRUD endpoints — detail, status update, and add form."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from jobhunt.db import add_job, get_job, update_job
from jobhunt.models import JobCreate, JobStatus, JobUpdate
from ..dependencies import get_db, get_templates

router = APIRouter()

DBDep = Annotated[sqlite3.Connection, Depends(get_db)]
TemplatesDep = Annotated[Jinja2Templates, Depends(get_templates)]

_APPLICATIONS_DIR = Path("applications")


def _find_application_file(job_id: int, pattern: str) -> Path | None:
    """Return the first match for a glob pattern under applications/<job_id>-*/."""
    matches = list(_APPLICATIONS_DIR.glob(f"{job_id}-*/{pattern}"))
    return matches[0] if matches else None


@router.get("/add", response_class=HTMLResponse)
async def add_job_modal(request: Request) -> HTMLResponse:
    """Render the add-job form (HTMX modal)."""
    templates = get_templates(request)
    return templates.TemplateResponse("add_job.html", {"request": request})


@router.post("/add", response_class=HTMLResponse)
async def create_job(
    request: Request,
    conn: DBDep,
    url: Annotated[str, Form()],
    title: Annotated[str, Form()],
    company: Annotated[str, Form()],
    location: Annotated[str | None, Form()] = None,
    notes: Annotated[str | None, Form()] = None,
) -> RedirectResponse:
    """Create a new job from the add form and redirect to the pipeline."""
    add_job(
        conn,
        JobCreate(
            url=url,
            title=title,
            company=company,
            location=location,
            notes=notes,
        ),
    )
    return RedirectResponse("/", status_code=302)


@router.get("/{job_id}", response_class=HTMLResponse)
async def job_detail(
    request: Request,
    job_id: int,
    conn: DBDep,
) -> HTMLResponse | RedirectResponse:
    """Render the job detail page."""
    templates = get_templates(request)
    job = get_job(conn, job_id)

    if job is None:
        return RedirectResponse("/", status_code=302)

    research_path = _find_application_file(job_id, "research.md")
    research = research_path.read_text(encoding="utf-8") if research_path else None

    cover_path = _find_application_file(job_id, "cover_letter.md")
    has_cover_letter = cover_path is not None

    return templates.TemplateResponse(
        "job_detail.html",
        {
            "request": request,
            "job": job,
            "statuses": list(JobStatus),
            "research": research,
            "has_cover_letter": has_cover_letter,
        },
    )


@router.post("/{job_id}/status", response_class=HTMLResponse)
async def update_status(
    request: Request,
    job_id: int,
    conn: DBDep,
    status: Annotated[JobStatus, Form()],
) -> HTMLResponse | RedirectResponse:
    """Update a job's status and return the refreshed card partial (HTMX)."""
    templates = get_templates(request)
    update_job(conn, job_id, JobUpdate(status=status))
    job = get_job(conn, job_id)

    if job is None:
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse(
        "partials/job_card.html",
        {"request": request, "job": job},
    )
