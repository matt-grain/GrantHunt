# Phase 4.3: Prospect Review + Stats

**Status:** ✅ Complete
**Completed:** 2026-03-05
**Dependencies:** Phase 4.1 (routers), Phase 4.2 (base.html, partials)
**Agent:** python-fastapi

---

## Files to Create

### `src/jobhunt/web/routers/prospects.py`

**Purpose:** Prospect review endpoints
**Dependencies:** `get_db`, `get_templates`, prospect db functions
**Endpoints:**

1. `GET /prospects` — Prospect review page
   - List pending prospects sorted by score descending
   - Count by status
   - Render `prospects.html`

2. `POST /prospects/{id}/track` — Track prospect (HTMX)
   - Call `track_prospect()` from db.py
   - Return updated row or remove from list

3. `POST /prospects/{id}/dismiss` — Dismiss prospect (HTMX)
   - Call `dismiss_prospect()` from db.py
   - Return empty (row disappears) with hx-swap="delete"

4. `POST /prospects/bulk` — Bulk action (HTMX)
   - Accept action (track/dismiss) and list of IDs
   - Process all, return updated prospect list

**Code pattern:**
```python
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
import sqlite3
from typing import Annotated

from jobhunt.db import (
    list_prospects,
    track_prospect,
    dismiss_prospect,
    count_prospects_by_status,
)
from jobhunt.models import ProspectStatus
from ..dependencies import get_db, get_templates

router = APIRouter(prefix="/prospects", tags=["prospects"])

@router.get("", response_class=HTMLResponse)
async def prospect_review(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
):
    templates = get_templates(request)
    prospects = list_prospects(conn, ProspectStatus.PENDING)
    counts = count_prospects_by_status(conn)

    return templates.TemplateResponse(
        "prospects.html",
        {
            "request": request,
            "prospects": prospects,
            "pending_count": counts.get("PENDING", 0),
            "tracked_count": counts.get("TRACKED", 0),
            "dismissed_count": counts.get("DISMISSED", 0),
        }
    )

@router.post("/{prospect_id}/track", response_class=HTMLResponse)
async def track(
    request: Request,
    prospect_id: int,
    conn: sqlite3.Connection = Depends(get_db),
):
    track_prospect(conn, prospect_id)
    # Return empty with OOB swap to update counts
    templates = get_templates(request)
    counts = count_prospects_by_status(conn)
    return templates.TemplateResponse(
        "partials/prospect_row.html",
        {"request": request, "prospect": None, "tracked": True, "counts": counts}
    )

@router.post("/{prospect_id}/dismiss", response_class=HTMLResponse)
async def dismiss(
    prospect_id: int,
    conn: sqlite3.Connection = Depends(get_db),
):
    dismiss_prospect(conn, prospect_id)
    # Return empty string - HTMX will remove the row
    return ""
```

**Constraints:**
- Sort prospects by `quick_score DESC`
- Return empty string for dismiss (HTMX removes element)
- Track returns confirmation or redirects to pipeline

---

### `src/jobhunt/web/routers/stats.py`

**Purpose:** Analytics dashboard endpoints
**Dependencies:** `get_db`, `get_templates`, db functions
**Endpoints:**

1. `GET /stats` — Stats dashboard
   - Calculate: jobs by status, avg score, response rate
   - Find stale jobs (applied > 7 days, no update)
   - Render `stats.html`

**Code pattern:**
```python
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
import sqlite3

from jobhunt.db import list_jobs
from jobhunt.models import JobStatus
from ..dependencies import get_db, get_templates

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("", response_class=HTMLResponse)
async def stats_dashboard(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
):
    templates = get_templates(request)
    jobs = list_jobs(conn)

    # Count by status
    status_counts = {}
    for status in JobStatus:
        status_counts[status.value] = len([j for j in jobs if j.status == status])

    # Active jobs (not rejected/withdrawn)
    active_statuses = {JobStatus.NEW, JobStatus.INTERESTED, JobStatus.APPLIED, JobStatus.INTERVIEWING, JobStatus.OFFER}
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
        j for j in jobs
        if j.status == JobStatus.APPLIED and j.date_updated < stale_threshold
    ]

    # Response rate
    total_applied = status_counts.get("APPLIED", 0) + status_counts.get("INTERVIEWING", 0) + status_counts.get("OFFER", 0) + status_counts.get("REJECTED", 0)
    responses = status_counts.get("INTERVIEWING", 0) + status_counts.get("OFFER", 0) + status_counts.get("REJECTED", 0)
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
        }
    )
```

**Constraints:**
- Stale = APPLIED status, date_updated > 7 days ago
- Response rate = (INTERVIEWING + OFFER + REJECTED) / (all who applied)
- Round percentages to integers

---

### `src/jobhunt/web/templates/prospects.html`

**Purpose:** Prospect review page with bulk actions
**Extends:** `base.html`
**Context variables:** `prospects: list[JobProspect]`, `pending_count: int`, etc.

**Structure:**
```html
{% extends "base.html" %}
{% block title %}Review Prospects - JobHunt{% endblock %}

{% block content %}
<div class="flex justify-between items-center mb-6">
    <div>
        <h1 class="text-2xl font-bold">Review Prospects</h1>
        <p class="text-gray-500">{{ pending_count }} prospects pending review</p>
    </div>
    <div class="flex gap-2">
        <button hx-post="/prospects/bulk?action=dismiss&below=60"
                hx-target="#prospect-list"
                hx-confirm="Dismiss all prospects with score below 60?"
                class="bg-red-100 text-red-700 px-4 py-2 rounded hover:bg-red-200">
            Dismiss All &lt; 60
        </button>
    </div>
</div>

<div class="bg-white rounded-lg shadow overflow-hidden">
    <table class="w-full">
        <thead class="bg-gray-50 border-b">
            <tr>
                <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Score</th>
                <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Title</th>
                <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Company</th>
                <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Location</th>
                <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Actions</th>
            </tr>
        </thead>
        <tbody id="prospect-list" class="divide-y">
            {% for prospect in prospects %}
                {% include "partials/prospect_row.html" %}
            {% endfor %}

            {% if not prospects %}
            <tr>
                <td colspan="5" class="px-4 py-8 text-center text-gray-400">
                    No pending prospects. Run /job-find to discover new opportunities.
                </td>
            </tr>
            {% endif %}
        </tbody>
    </table>
</div>

<div class="mt-4 text-sm text-gray-500">
    <span class="inline-block mr-4">Tracked: {{ tracked_count }}</span>
    <span class="inline-block">Dismissed: {{ dismissed_count }}</span>
</div>
{% endblock %}
```

**Constraints:**
- Table layout for easy scanning
- Bulk dismiss confirms before action
- Empty state prompts /job-find

---

### `src/jobhunt/web/templates/stats.html`

**Purpose:** Analytics dashboard
**Extends:** `base.html`
**Context variables:** `status_counts`, `avg_score`, `score_dist`, `stale_jobs`, `response_rate`

**Structure:**
```html
{% extends "base.html" %}
{% block title %}Analytics - JobHunt{% endblock %}

{% block content %}
<h1 class="text-2xl font-bold mb-6">Analytics</h1>

<!-- Summary cards -->
<div class="grid grid-cols-4 gap-4 mb-8">
    <div class="bg-white rounded-lg shadow p-4 text-center">
        <p class="text-3xl font-bold text-gray-800">{{ total_active }}</p>
        <p class="text-sm text-gray-500">Active Jobs</p>
    </div>
    <div class="bg-white rounded-lg shadow p-4 text-center">
        <p class="text-3xl font-bold text-gray-800">{{ avg_score }}</p>
        <p class="text-sm text-gray-500">Avg Score</p>
    </div>
    <div class="bg-white rounded-lg shadow p-4 text-center">
        <p class="text-3xl font-bold text-gray-800">{{ status_counts.get('APPLIED', 0) }}</p>
        <p class="text-sm text-gray-500">Applied</p>
    </div>
    <div class="bg-white rounded-lg shadow p-4 text-center">
        <p class="text-3xl font-bold text-gray-800">{{ response_rate }}%</p>
        <p class="text-sm text-gray-500">Response Rate</p>
    </div>
</div>

<!-- Pipeline breakdown -->
<div class="bg-white rounded-lg shadow p-6 mb-8">
    <h2 class="text-lg font-semibold mb-4">Pipeline Breakdown</h2>
    {% for status, count in status_counts.items() %}
    <div class="flex items-center mb-2">
        <span class="w-28 text-sm text-gray-600">{{ status }}</span>
        <div class="flex-1 bg-gray-100 rounded-full h-4 mr-4">
            <div class="bg-blue-500 h-4 rounded-full"
                 style="width: {{ (count / total_active * 100) if total_active > 0 else 0 }}%"></div>
        </div>
        <span class="text-sm text-gray-600 w-8">{{ count }}</span>
    </div>
    {% endfor %}
</div>

<!-- Score distribution -->
<div class="bg-white rounded-lg shadow p-6 mb-8">
    <h2 class="text-lg font-semibold mb-4">Score Distribution</h2>
    {% for range, count in score_dist.items() %}
    <div class="flex items-center mb-2">
        <span class="w-20 text-sm text-gray-600">{{ range }}</span>
        <div class="flex-1 bg-gray-100 rounded-full h-4 mr-4">
            <div class="bg-green-500 h-4 rounded-full"
                 style="width: {{ count * 20 }}%"></div>
        </div>
        <span class="text-sm text-gray-600 w-8">{{ count }}</span>
    </div>
    {% endfor %}
</div>

<!-- Follow-up reminders -->
{% if stale_jobs %}
<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
    <h2 class="text-lg font-semibold text-yellow-800 mb-4">Follow-up Reminders</h2>
    <ul class="space-y-2">
        {% for job in stale_jobs %}
        <li class="flex items-center text-yellow-700">
            <span class="mr-2">&#9888;</span>
            <a href="/jobs/{{ job.id }}" class="hover:underline">
                {{ job.company }} - {{ job.title }}
            </a>
            <span class="text-sm ml-2">
                (applied {{ ((now - job.date_updated).days) }} days ago)
            </span>
        </li>
        {% endfor %}
    </ul>
</div>
{% endif %}
{% endblock %}
```

**Constraints:**
- Progress bars use inline width styles (simple, no JS)
- Stale jobs link to detail page
- Empty stale section hidden entirely

---

### `src/jobhunt/web/templates/partials/prospect_row.html`

**Purpose:** Single row in prospect review table
**Context variables:** `prospect: JobProspect`

**Structure:**
```html
<tr id="prospect-{{ prospect.id }}" class="hover:bg-gray-50">
    <td class="px-4 py-3">
        <span class="inline-flex items-center justify-center w-10 h-10 rounded-full
                     {% if prospect.quick_score >= 80 %}bg-green-100 text-green-800
                     {% elif prospect.quick_score >= 60 %}bg-yellow-100 text-yellow-800
                     {% else %}bg-gray-100 text-gray-600{% endif %}
                     font-bold text-sm">
            {{ prospect.quick_score|int if prospect.quick_score else "-" }}
        </span>
    </td>
    <td class="px-4 py-3">
        <a href="{{ prospect.url }}" target="_blank" class="text-blue-600 hover:underline">
            {{ prospect.title }}
        </a>
        {% if prospect.summary %}
        <p class="text-xs text-gray-500 truncate max-w-md">{{ prospect.summary }}</p>
        {% endif %}
    </td>
    <td class="px-4 py-3 text-gray-700">{{ prospect.company }}</td>
    <td class="px-4 py-3 text-gray-500 text-sm">{{ prospect.location or "-" }}</td>
    <td class="px-4 py-3">
        <div class="flex gap-2">
            <a href="{{ prospect.url }}" target="_blank"
               class="text-gray-400 hover:text-gray-600" title="Preview">
                &#128065;
            </a>
            <button hx-post="/prospects/{{ prospect.id }}/track"
                    hx-target="#prospect-{{ prospect.id }}"
                    hx-swap="outerHTML"
                    class="text-green-600 hover:text-green-800" title="Track">
                &#10003;
            </button>
            <button hx-post="/prospects/{{ prospect.id }}/dismiss"
                    hx-target="#prospect-{{ prospect.id }}"
                    hx-swap="delete"
                    class="text-red-600 hover:text-red-800" title="Dismiss">
                &#10005;
            </button>
        </div>
    </td>
</tr>
```

**Constraints:**
- Row has unique ID for HTMX targeting
- Track swaps row with success message, Dismiss deletes row
- Title links to original posting (external)
- Summary truncated with CSS

---

### `src/jobhunt/web/templates/partials/stats_cards.html`

**Purpose:** Reusable stats summary cards
**Context variables:** `total_active`, `avg_score`, `applied_count`, `response_rate`

**Structure:**
```html
<div class="grid grid-cols-4 gap-4">
    <div class="bg-white rounded-lg shadow p-4 text-center">
        <p class="text-3xl font-bold text-gray-800">{{ total_active }}</p>
        <p class="text-sm text-gray-500">Active Jobs</p>
    </div>
    <div class="bg-white rounded-lg shadow p-4 text-center">
        <p class="text-3xl font-bold text-gray-800">{{ avg_score }}</p>
        <p class="text-sm text-gray-500">Avg Score</p>
    </div>
    <div class="bg-white rounded-lg shadow p-4 text-center">
        <p class="text-3xl font-bold text-gray-800">{{ applied_count }}</p>
        <p class="text-sm text-gray-500">Applied</p>
    </div>
    <div class="bg-white rounded-lg shadow p-4 text-center">
        <p class="text-3xl font-bold text-gray-800">{{ response_rate }}%</p>
        <p class="text-sm text-gray-500">Response Rate</p>
    </div>
</div>
```

---

## Files to Modify

### `src/jobhunt/web/routers/__init__.py` (MODIFY)

**Change:** Add prospects and stats router imports
**Exact change:**
```python
from . import dashboard, jobs, prospects, stats
```

---

### `src/jobhunt/web/app.py` (MODIFY)

**Change:** Include prospects and stats routers
**Exact change:** Add after existing router includes:
```python
from .routers import dashboard, jobs, prospects, stats

# In create_app():
app.include_router(prospects.router)
app.include_router(stats.router)
```

---

## Verification

After implementation:
1. `uv run jobhunt serve` — Start server
2. Visit `/prospects` — See pending prospects table
3. Click track/dismiss buttons — Rows update via HTMX
4. Visit `/stats` — See analytics dashboard
5. Check stale jobs reminder appears for old applications
