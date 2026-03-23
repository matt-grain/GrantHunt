"""Grant CRUD endpoints — detail, status update, and add form."""

from __future__ import annotations

import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from granthunt.db import add_grant, delete_grant, get_grant, update_grant
from granthunt.models import GrantCreate, GrantStatus, GrantUpdate
from ..dependencies import get_db, get_templates

router = APIRouter()

DBDep = Annotated[sqlite3.Connection, Depends(get_db)]
TemplatesDep = Annotated[Jinja2Templates, Depends(get_templates)]


@router.get("/add", response_class=HTMLResponse)
async def add_grant_modal(request: Request) -> HTMLResponse:
    """Render the add-grant form (HTMX modal)."""
    templates = get_templates(request)
    return templates.TemplateResponse("add_grant.html", {"request": request})


@router.post("/add", response_class=HTMLResponse)
async def create_grant(
    request: Request,
    conn: DBDep,
    url: Annotated[str, Form()],
    title: Annotated[str, Form()],
    organization: Annotated[str, Form()],
    program: Annotated[str | None, Form()] = None,
    location: Annotated[str | None, Form()] = None,
    deadline: Annotated[str | None, Form()] = None,
    amount_min: Annotated[float | None, Form()] = None,
    amount_max: Annotated[float | None, Form()] = None,
    grant_type: Annotated[str | None, Form()] = None,
    notes: Annotated[str | None, Form()] = None,
) -> RedirectResponse:
    """Create a new grant from the add form and redirect to the pipeline."""
    add_grant(
        conn,
        GrantCreate(
            url=url,
            title=title,
            organization=organization,
            program=program,
            location=location,
            deadline=deadline,
            amount_min=amount_min,
            amount_max=amount_max,
            grant_type=grant_type,
            notes=notes,
        ),
    )
    return RedirectResponse("/", status_code=302)


@router.get("/{grant_id}", response_class=HTMLResponse, response_model=None)
async def grant_detail(
    request: Request,
    grant_id: int,
    conn: DBDep,
) -> HTMLResponse | RedirectResponse:
    """Render the grant detail page."""
    templates = get_templates(request)
    grant = get_grant(conn, grant_id)

    if grant is None:
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse(
        "grant_detail.html",
        {
            "request": request,
            "grant": grant,
            "statuses": list(GrantStatus),
        },
    )


@router.post("/{grant_id}/notes", response_class=HTMLResponse, response_model=None)
async def add_note(
    request: Request,
    grant_id: int,
    conn: DBDep,
    note: Annotated[str, Form()],
) -> HTMLResponse | RedirectResponse:
    """Append a timestamped note to a grant's existing notes."""
    grant = get_grant(conn, grant_id)
    if grant is None:
        return RedirectResponse("/", status_code=302)

    existing = grant.notes or ""
    timestamp = __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M")
    separator = "\n\n" if existing else ""
    updated_notes = f"{existing}{separator}[{timestamp}] {note}"

    update_grant(conn, grant_id, GrantUpdate(notes=updated_notes))
    return RedirectResponse(f"/grants/{grant_id}", status_code=302)


@router.post("/{grant_id}/delete", response_model=None)
async def delete_grant_route(
    grant_id: int,
    conn: DBDep,
) -> RedirectResponse:
    """Delete a grant from the tracker."""
    delete_grant(conn, grant_id)
    return RedirectResponse("/", status_code=302)


@router.post("/{grant_id}/status", response_class=HTMLResponse, response_model=None)
async def update_status(
    request: Request,
    grant_id: int,
    conn: DBDep,
    status: Annotated[GrantStatus, Form()],
) -> HTMLResponse | RedirectResponse:
    """Update a grant's status and return the refreshed card partial (HTMX)."""
    templates = get_templates(request)
    update_grant(conn, grant_id, GrantUpdate(status=status))
    grant = get_grant(conn, grant_id)

    if grant is None:
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse(
        "partials/grant_card.html",
        {"request": request, "grant": grant},
    )
