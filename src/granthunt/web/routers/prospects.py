"""Prospect review endpoints."""

from __future__ import annotations

import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from granthunt.db import (
    count_prospects_by_status,
    dismiss_prospect,
    list_prospects,
    track_prospect,
)
from granthunt.models import ProspectStatus
from ..dependencies import get_db, get_templates

router = APIRouter(prefix="/prospects", tags=["prospects"])

DBDep = Annotated[sqlite3.Connection, Depends(get_db)]


@router.get("", response_class=HTMLResponse)
async def prospect_review(
    request: Request,
    conn: DBDep,
    sort: str = "quick_score",
    dir: str = "desc",
) -> HTMLResponse:
    """Render the prospect review page with pending prospects."""
    templates = get_templates(request)
    prospects = list_prospects(conn, ProspectStatus.PENDING, sort_by=sort, sort_dir=dir)
    counts = count_prospects_by_status(conn)

    return templates.TemplateResponse(
        "prospects.html",
        {
            "request": request,
            "prospects": prospects,
            "pending_count": counts.get("PENDING", 0),
            "tracked_count": counts.get("TRACKED", 0),
            "dismissed_count": counts.get("DISMISSED", 0),
            "sort_by": sort,
            "sort_dir": dir,
        },
    )


@router.post("/{prospect_id}/track", response_class=HTMLResponse)
async def track(prospect_id: int, conn: DBDep) -> str:
    """Track a prospect (add to job pipeline). Returns empty for HTMX delete."""
    track_prospect(conn, prospect_id)
    return ""  # Row will be removed via hx-swap="delete"


@router.post("/{prospect_id}/dismiss", response_class=HTMLResponse)
async def dismiss(prospect_id: int, conn: DBDep) -> str:
    """Dismiss a prospect. Returns empty for HTMX delete."""
    dismiss_prospect(conn, prospect_id)
    return ""  # Row will be removed via hx-swap="delete"
