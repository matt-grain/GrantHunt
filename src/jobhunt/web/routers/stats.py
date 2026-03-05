"""Analytics dashboard endpoints."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from jobhunt.db import list_jobs
from jobhunt.models import JobStatus
from ..dependencies import get_db, get_templates

router = APIRouter(prefix="/stats", tags=["stats"])

DBDep = Annotated[sqlite3.Connection, Depends(get_db)]


@router.get("", response_class=HTMLResponse)
async def stats_dashboard(request: Request, conn: DBDep) -> HTMLResponse:
    """Render the analytics dashboard."""
    templates = get_templates(request)
    jobs = list_jobs(conn)

    # Count by status
    status_counts: dict[str, int] = {}
    for status in JobStatus:
        status_counts[status.value] = len([j for j in jobs if j.status == status])

    # Active jobs (not rejected/withdrawn)
    active_statuses = {
        JobStatus.NEW,
        JobStatus.INTERESTED,
        JobStatus.APPLIED,
        JobStatus.INTERVIEWING,
        JobStatus.OFFER,
    }
    active_jobs = [j for j in jobs if j.status in active_statuses]

    # Average score
    scores = [j.score for j in active_jobs if j.score is not None]
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

    # Stale jobs (applied > 7 days ago)
    stale_threshold = datetime.now() - timedelta(days=7)
    stale_jobs = [
        j
        for j in jobs
        if j.status == JobStatus.APPLIED and j.date_updated < stale_threshold
    ]

    # Response rate
    total_applied = (
        status_counts.get("APPLIED", 0)
        + status_counts.get("INTERVIEWING", 0)
        + status_counts.get("OFFER", 0)
        + status_counts.get("REJECTED", 0)
    )
    responses = (
        status_counts.get("INTERVIEWING", 0)
        + status_counts.get("OFFER", 0)
        + status_counts.get("REJECTED", 0)
    )
    response_rate = (responses / total_applied * 100) if total_applied > 0 else 0

    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "status_counts": status_counts,
            "total_active": len(active_jobs),
            "avg_score": round(avg_score, 1),
            "score_dist": score_dist,
            "stale_jobs": stale_jobs,
            "response_rate": round(response_rate),
            "now": datetime.now(),
        },
    )
