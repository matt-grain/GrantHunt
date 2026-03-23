"""Job CRUD endpoints — detail, status update, and add form."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from granthunt.db import add_job, delete_job, get_job, update_job
from granthunt.models import JobCreate, JobStatus, JobUpdate
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


@router.get("/{job_id}", response_class=HTMLResponse, response_model=None)
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
    research = None
    if research_path:
        import markdown
        research = markdown.markdown(
            research_path.read_text(encoding="utf-8"),
            extensions=["tables", "fenced_code", "nl2br"],
        )

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


@router.get("/{job_id}/cover-letter", response_class=HTMLResponse, response_model=None)
async def cover_letter(
    request: Request,
    job_id: int,
    conn: DBDep,
) -> HTMLResponse | RedirectResponse:
    """Render the cover letter page."""
    import markdown

    templates = get_templates(request)
    job = get_job(conn, job_id)

    if job is None:
        return RedirectResponse("/", status_code=302)

    cover_path = _find_application_file(job_id, "cover_letter.md")
    if cover_path is None:
        return RedirectResponse(f"/jobs/{job_id}", status_code=302)

    cover_letter_html = markdown.markdown(
        cover_path.read_text(encoding="utf-8"),
        extensions=["tables", "fenced_code", "nl2br"],
    )

    return templates.TemplateResponse(
        "cover_letter.html",
        {
            "request": request,
            "job": job,
            "cover_letter": cover_letter_html,
        },
    )


@router.post("/{job_id}/notes", response_class=HTMLResponse, response_model=None)
async def add_note(
    request: Request,
    job_id: int,
    conn: DBDep,
    note: Annotated[str, Form()],
) -> HTMLResponse | RedirectResponse:
    """Append a note to a job's existing notes."""
    job = get_job(conn, job_id)
    if job is None:
        return RedirectResponse("/", status_code=302)

    existing = job.notes or ""
    timestamp = __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M")
    separator = "\n\n" if existing else ""
    updated_notes = f"{existing}{separator}[{timestamp}] {note}"

    update_job(conn, job_id, JobUpdate(notes=updated_notes))
    return RedirectResponse(f"/jobs/{job_id}", status_code=302)


@router.post("/{job_id}/delete", response_model=None)
async def delete_job_route(
    job_id: int,
    conn: DBDep,
) -> RedirectResponse:
    """Delete a job from the tracker."""
    delete_job(conn, job_id)
    return RedirectResponse("/", status_code=302)


@router.post("/{job_id}/status", response_class=HTMLResponse, response_model=None)
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
