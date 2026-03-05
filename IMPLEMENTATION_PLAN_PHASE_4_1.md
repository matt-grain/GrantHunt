# Phase 4.1: FastAPI Backend Core

**Dependencies:** Existing `db.py`, `models.py`
**Agent:** python-fastapi

---

## Files to Create

### `src/jobhunt/web/__init__.py`

**Purpose:** Package marker for web module
**Content:** Empty file or single docstring

---

### `src/jobhunt/web/app.py`

**Purpose:** FastAPI application factory with Jinja2 templates
**Dependencies:** FastAPI, Jinja2Templates, StaticFiles
**Functions:**
- `create_app() -> FastAPI` — Factory that:
  1. Creates FastAPI instance with title="JobHunt"
  2. Mounts static files from `web/static` at `/static`
  3. Configures Jinja2Templates from `web/templates`
  4. Includes routers: dashboard, jobs
  5. Adds HTMX response headers middleware

**Code pattern:**
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .routers import dashboard, jobs

def create_app() -> FastAPI:
    app = FastAPI(title="JobHunt")

    base_path = Path(__file__).parent
    app.mount("/static", StaticFiles(directory=base_path / "static"), name="static")

    templates = Jinja2Templates(directory=base_path / "templates")
    app.state.templates = templates

    app.include_router(dashboard.router)
    app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

    return app
```

**Constraints:**
- Use `Path(__file__).parent` for relative paths, not hardcoded strings
- Store templates in `app.state.templates` for access in routers
- No lifespan/startup needed — db.py handles connections per-request

---

### `src/jobhunt/web/dependencies.py`

**Purpose:** Dependency injection for database connection and templates
**Functions:**
- `get_db() -> Generator[sqlite3.Connection, None, None]` — Yields db connection, closes after request
- `get_templates(request: Request) -> Jinja2Templates` — Returns templates from app.state

**Code pattern:**
```python
from typing import Generator
import sqlite3
from fastapi import Request
from fastapi.templating import Jinja2Templates

from jobhunt.db import init_db

def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = init_db()
    try:
        yield conn
    finally:
        conn.close()

def get_templates(request: Request) -> Jinja2Templates:
    return request.app.state.templates
```

**Constraints:**
- Always close connection in finally block
- Use existing `init_db()` from `jobhunt.db`

---

### `src/jobhunt/web/routers/__init__.py`

**Purpose:** Router package exports
**Content:**
```python
from . import dashboard, jobs
```

---

### `src/jobhunt/web/routers/dashboard.py`

**Purpose:** Main dashboard routes (pipeline view, kanban)
**Dependencies:** `get_db`, `get_templates`, `list_jobs`, `JobStatus`
**Endpoints:**

1. `GET /` — Pipeline view
   - Query all jobs grouped by status
   - Count jobs per status
   - Render `dashboard.html`

2. `GET /kanban` — Kanban board view
   - Same data as pipeline
   - Render `kanban.html`

**Code pattern:**
```python
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
import sqlite3

from jobhunt.db import list_jobs
from jobhunt.models import JobStatus
from ..dependencies import get_db, get_templates

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def pipeline_view(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
):
    templates = get_templates(request)
    jobs = list_jobs(conn)

    # Group by status
    jobs_by_status = {status: [] for status in JobStatus}
    for job in jobs:
        jobs_by_status[job.status].append(job)

    # Count per status
    status_counts = {status: len(jobs_by_status[status]) for status in JobStatus}

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "jobs_by_status": jobs_by_status, "status_counts": status_counts}
    )

@router.get("/kanban", response_class=HTMLResponse)
async def kanban_view(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
):
    templates = get_templates(request)
    jobs = list_jobs(conn)
    jobs_by_status = {status: [] for status in JobStatus}
    for job in jobs:
        jobs_by_status[job.status].append(job)

    return templates.TemplateResponse(
        "kanban.html",
        {"request": request, "jobs_by_status": jobs_by_status}
    )
```

**Constraints:**
- Use `response_class=HTMLResponse` for all HTML endpoints
- Always pass `request` to template context
- Group jobs using existing `JobStatus` enum values

---

### `src/jobhunt/web/routers/jobs.py`

**Purpose:** Job CRUD endpoints
**Dependencies:** `get_db`, `get_templates`, db functions, models
**Endpoints:**

1. `GET /jobs/{job_id}` — Job detail page
   - Fetch job by ID
   - Load research.md if exists in `applications/{job_id}-{company}/`
   - Render `job_detail.html`

2. `POST /jobs/{job_id}/status` — Update job status (HTMX)
   - Accept new status in form data
   - Update via `update_job()`
   - Return partial `job_card.html` or redirect

3. `GET /jobs/add` — Add job modal (HTMX)
   - Render `add_job.html` partial

4. `POST /jobs/add` — Create new job
   - Accept URL, title, company, location, notes
   - Call `add_job()`
   - Redirect to dashboard or return HTMX partial

**Code pattern:**
```python
from pathlib import Path
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import sqlite3

from jobhunt.db import get_job, update_job, add_job
from jobhunt.models import JobStatus, JobUpdate, JobCreate
from ..dependencies import get_db, get_templates

router = APIRouter()

@router.get("/{job_id}", response_class=HTMLResponse)
async def job_detail(
    request: Request,
    job_id: int,
    conn: sqlite3.Connection = Depends(get_db),
):
    templates = get_templates(request)
    job = get_job(conn, job_id)
    if job is None:
        return RedirectResponse("/", status_code=302)

    # Load research.md if exists
    research = None
    research_paths = list(Path("applications").glob(f"{job_id}-*/research.md"))
    if research_paths:
        research = research_paths[0].read_text()

    # Check for cover letter
    cover_paths = list(Path("applications").glob(f"{job_id}-*/cover_letter.md"))
    has_cover_letter = bool(cover_paths)

    return templates.TemplateResponse(
        "job_detail.html",
        {
            "request": request,
            "job": job,
            "statuses": list(JobStatus),
            "research": research,
            "has_cover_letter": has_cover_letter,
        }
    )

@router.post("/{job_id}/status", response_class=HTMLResponse)
async def update_status(
    request: Request,
    job_id: int,
    status: JobStatus = Form(...),
    conn: sqlite3.Connection = Depends(get_db),
):
    templates = get_templates(request)
    update_job(conn, job_id, JobUpdate(status=status))
    job = get_job(conn, job_id)

    return templates.TemplateResponse(
        "partials/job_card.html",
        {"request": request, "job": job}
    )

@router.get("/add", response_class=HTMLResponse)
async def add_job_modal(request: Request):
    templates = get_templates(request)
    return templates.TemplateResponse("add_job.html", {"request": request})

@router.post("/add", response_class=HTMLResponse)
async def create_job(
    request: Request,
    url: str = Form(...),
    title: str = Form(...),
    company: str = Form(...),
    location: str = Form(None),
    notes: str = Form(None),
    conn: sqlite3.Connection = Depends(get_db),
):
    add_job(conn, JobCreate(
        url=url,
        title=title,
        company=company,
        location=location,
        notes=notes,
    ))
    return RedirectResponse("/", status_code=302)
```

**Constraints:**
- Status must be validated as `JobStatus` enum via Form
- Return HTML partials for HTMX endpoints, not JSON
- Check if research.md exists using pathlib before including

---

## Files to Modify

### `src/jobhunt/cli.py` (MODIFY)

**Change:** Add `serve` command to start web server
**Exact change:**
```python
@app.command()
def serve(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
) -> None:
    """Start the web dashboard server."""
    import uvicorn
    from jobhunt.web.app import create_app

    console.print(f"[green]Starting JobHunt dashboard at http://{host}:{port}[/green]")
    uvicorn.run(
        "jobhunt.web.app:create_app",
        host=host,
        port=port,
        reload=reload,
        factory=True,
    )
```

**Location:** After existing commands, before `if __name__ == "__main__"`

---

### `pyproject.toml` (MODIFY)

**Change:** Add web dependencies
**Exact change:** Add to `[project.dependencies]`:
```toml
"fastapi>=0.115.0",
"uvicorn[standard]>=0.32.0",
"jinja2>=3.1.0",
```

---

## Directory Structure After Phase 4.1

```
src/jobhunt/
├── web/
│   ├── __init__.py
│   ├── app.py
│   ├── dependencies.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   └── jobs.py
│   ├── templates/           # Created but empty until 4.2
│   └── static/              # Created but empty until 4.2
```

---

## Verification

After implementation:
1. `uv sync` — Install new dependencies
2. `uv run pyright src/jobhunt/web/` — Type check
3. `uv run ruff check src/jobhunt/web/` — Lint
4. `uv run jobhunt serve` — Should start (will fail on missing templates, expected)
