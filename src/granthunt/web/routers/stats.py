"""Analytics dashboard endpoints."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from granthunt.db import list_grants
from granthunt.models import GrantStatus
from ..dependencies import get_db, get_templates

router = APIRouter(prefix="/stats", tags=["stats"])

DBDep = Annotated[sqlite3.Connection, Depends(get_db)]


@router.get("", response_class=HTMLResponse)
async def stats_dashboard(request: Request, conn: DBDep) -> HTMLResponse:
    """Render the analytics dashboard."""
    templates = get_templates(request)
    grants = list_grants(conn)

    # Count by status
    status_counts: dict[str, int] = {}
    for status in GrantStatus:
        status_counts[status.value] = len([g for g in grants if g.status == status])

    # Active grants (not rejected/withdrawn)
    active_statuses = {
        GrantStatus.DISCOVERED,
        GrantStatus.EVALUATING,
        GrantStatus.PREPARING,
        GrantStatus.SUBMITTED,
        GrantStatus.UNDER_REVIEW,
        GrantStatus.APPROVED,
    }
    active_grants = [g for g in grants if g.status in active_statuses]

    # Average score
    scores = [g.score for g in active_grants if g.score is not None]
    avg_score = sum(scores) / len(scores) if scores else 0

    # Score distribution
    score_dist = {"90-100": 0, "80-89": 0, "70-79": 0, "60-69": 0, "<60": 0}
    for s in scores:
        if s >= 90:
            score_dist["90-100"] += 1
        elif s >= 80:
            score_dist["80-89"] += 1
        elif s >= 70:
            score_dist["70-79"] += 1
        elif s >= 60:
            score_dist["60-69"] += 1
        else:
            score_dist["<60"] += 1

    # Stale grants (submitted > 30 days ago with no update)
    stale_threshold = datetime.now() - timedelta(days=30)
    stale_grants = [
        g
        for g in grants
        if g.status == GrantStatus.SUBMITTED and g.date_updated < stale_threshold
    ]

    # Response rate (grants that reached a terminal or advanced state)
    total_submitted = (
        status_counts.get("SUBMITTED", 0)
        + status_counts.get("UNDER_REVIEW", 0)
        + status_counts.get("APPROVED", 0)
        + status_counts.get("REJECTED", 0)
    )
    responses = (
        status_counts.get("UNDER_REVIEW", 0)
        + status_counts.get("APPROVED", 0)
        + status_counts.get("REJECTED", 0)
    )
    response_rate = (responses / total_submitted * 100) if total_submitted > 0 else 0

    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "status_counts": status_counts,
            "total_active": len(active_grants),
            "avg_score": round(avg_score, 1),
            "score_dist": score_dist,
            "stale_grants": stale_grants,
            "response_rate": round(response_rate),
            "now": datetime.now(),
        },
    )
