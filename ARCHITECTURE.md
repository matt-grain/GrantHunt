# JobHunt Architecture

## Overview

Job search automation system for tracking opportunities, matching against profile, and managing the application pipeline. Includes both CLI and web dashboard interfaces.

## Tech Stack

- **Language:** Python 3.13
- **Package Manager:** uv
- **Database:** SQLite
- **CLI:** typer + rich
- **Web:** FastAPI + Jinja2 + HTMX + Tailwind CSS (CDN)
- **HTTP:** httpx
- **Config:** YAML + Pydantic

## Project Structure

```
interviews/
├── job_profile.yaml              # Job search preferences
├── job_sources.yaml              # Job board configurations
├── jobs.db                       # SQLite database (gitignored)
├── applications/                 # Per-job application materials
│   └── {id}-{company}-{date}/
│       ├── research.md
│       └── cover_letter.md
├── src/
│   └── jobhunt/
│       ├── __init__.py
│       ├── models.py             # Pydantic models + enums
│       ├── config.py             # Profile loading
│       ├── db.py                 # Database operations
│       ├── cli.py                # typer CLI
│       ├── scraper.py            # Job posting fetcher
│       ├── matcher.py            # Scoring engine
│       ├── research.py           # Company research
│       ├── cover_letter.py       # Cover letter generation
│       └── web/                  # FastAPI web dashboard
│           ├── __init__.py
│           ├── app.py            # App factory
│           ├── dependencies.py   # FastAPI DI
│           ├── routers/
│           │   ├── __init__.py
│           │   ├── dashboard.py  # Pipeline + Kanban views
│           │   ├── jobs.py       # Job CRUD
│           │   ├── prospects.py  # Prospect review
│           │   └── stats.py      # Analytics
│           ├── templates/        # Jinja2 templates
│           │   ├── base.html
│           │   ├── dashboard.html
│           │   ├── kanban.html
│           │   ├── job_detail.html
│           │   ├── add_job.html
│           │   ├── prospects.html
│           │   ├── stats.html
│           │   └── partials/
│           │       ├── job_card.html
│           │       ├── job_list.html
│           │       ├── status_counts.html
│           │       ├── prospect_row.html
│           │       └── stats_cards.html
│           └── static/
│               └── app.css       # Dark mode theme
├── .claude/skills/
│   ├── job-add/                  # /job-add skill
│   ├── job-list/                 # /job-list skill
│   ├── job-match/                # /job-match skill
│   ├── job-apply/                # /job-apply skill
│   ├── job-find/                 # /job-find skill
│   └── job-review/               # /job-review skill
├── profile/                      # Resume and LinkedIn exports
└── docs/                         # Interview prep materials
```

## Data Flow

### CLI Flow
1. User runs `/job-add <url>` or `jobhunt add <url>`
2. CLI adds job to SQLite with status=NEW
3. User runs `/job-list` to see pipeline
4. User updates status as they progress through applications

### Web Dashboard Flow
1. User runs `jobhunt serve` to start the dashboard
2. Dashboard shows pipeline view at `/`
3. User can switch to Kanban (`/kanban`), Prospects (`/prospects`), or Stats (`/stats`)
4. HTMX enables in-place updates without full page reloads

### Prospect Discovery Flow
1. User runs `/job-find` to discover new opportunities
2. Prospects stored in `job_prospects` table with PENDING status
3. User reviews at `/prospects` or via `/job-review`
4. Track adds to main pipeline, Dismiss removes from view

## Key Domain Concepts

- **Job:** A job posting with URL, title, company, status, score
- **JobProspect:** A discovered opportunity pending review
- **JobProfile:** User's preferences for matching (roles, industries, tech)
- **JobStatus:** Pipeline stages (NEW -> INTERESTED -> APPLIED -> INTERVIEWING -> OFFER/REJECTED)
- **ProspectStatus:** Triage stages (PENDING -> TRACKED/DISMISSED)

## State Machines

### Job Status
```
NEW -> INTERESTED -> APPLIED -> INTERVIEWING -> OFFER
  |        |           |            |           |
  +--------+-----------+------------+-----------+-> REJECTED
  +--------+-----------+------------+-----------+-> WITHDRAWN
```

### Prospect Status
```
PENDING -> TRACKED (becomes Job with status=NEW)
        -> DISMISSED
```

## Web Dashboard Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Pipeline dashboard |
| `/kanban` | GET | Kanban board view |
| `/jobs/add` | GET | Add job modal |
| `/jobs/add` | POST | Create new job |
| `/jobs/{id}` | GET | Job detail page |
| `/jobs/{id}/status` | POST | Update job status (HTMX) |
| `/prospects` | GET | Prospect review page |
| `/prospects/{id}/track` | POST | Track prospect (HTMX) |
| `/prospects/{id}/dismiss` | POST | Dismiss prospect (HTMX) |
| `/stats` | GET | Analytics dashboard |
