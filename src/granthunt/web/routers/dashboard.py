"""Dashboard routes — pipeline and kanban views."""

from __future__ import annotations

import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from granthunt.db import list_grants
from granthunt.models import Grant, GrantStatus
from ..dependencies import get_db, get_templates

router = APIRouter()

DBDep = Annotated[sqlite3.Connection, Depends(get_db)]
TemplatesDep = Annotated[Jinja2Templates, Depends(get_templates)]


def _group_grants_by_status(grants: list[Grant]) -> dict[GrantStatus, list[Grant]]:
    """Group a flat list of grants into a dict keyed by GrantStatus."""
    grouped: dict[GrantStatus, list[Grant]] = {status: [] for status in GrantStatus}
    for grant in grants:
        grouped[grant.status].append(grant)
    return grouped


@router.get("/", response_class=HTMLResponse)
async def pipeline_view(
    request: Request,
    conn: DBDep,
) -> HTMLResponse:
    """Render the main pipeline dashboard."""
    templates = get_templates(request)
    grants = list_grants(conn)
    grants_by_status = _group_grants_by_status(grants)
    status_counts = {status: len(grants_by_status[status]) for status in GrantStatus}

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "grants_by_status": grants_by_status,
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
    grants = list_grants(conn)
    grants_by_status = _group_grants_by_status(grants)

    return templates.TemplateResponse(
        request,
        "kanban.html",
        {
            "grants_by_status": grants_by_status,
        },
    )
