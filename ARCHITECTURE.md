# GrantHunt Architecture

## Overview

Grant discovery and application tracking system for climate tech startups. Built for Flotexa (Quebec, Canada) to find, evaluate, and manage grants through a full pipeline from discovery to approval. Provides both a CLI for power users and a FastAPI web dashboard with HTMX-driven interactions. Claude Code skills automate discovery via Chrome browser automation.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.13 |
| Package manager | uv |
| Database | SQLite (grants.db, project root) |
| CLI | typer + rich |
| Web framework | FastAPI + Jinja2 |
| Frontend interactivity | HTMX + Tailwind CSS (CDN, no build step) |
| HTTP client | httpx |
| Config & validation | YAML + Pydantic v2 |
| Build backend | hatchling |

## Project Structure

```
GrantHunt/
├── grant_profile.yaml              # Startup profile for grant matching
├── grant_sources.yaml              # 12+ grant source configurations with priorities
├── grants.db                       # SQLite database (gitignored)
├── profile/
│   └── flotexa.md                  # Detailed company description for LOI generation
├── applications/                   # Per-grant application artifacts (gitignored)
│   └── {id}-{org}-{date}/
│       ├── research.md
│       └── loi.md
├── src/granthunt/
│   ├── __init__.py
│   ├── models.py                   # Pydantic models + GrantStatus/ProspectStatus enums
│   ├── config.py                   # GrantProfile loading from YAML
│   ├── db.py                       # SQLite database layer (raw sqlite3)
│   ├── cli.py                      # typer CLI entrypoint
│   ├── matcher.py                  # Grant-profile scoring engine
│   ├── scraper.py                  # Grant posting fetcher (httpx + BeautifulSoup)
│   ├── research.py                 # Organization research
│   ├── application.py              # LOI generation
│   └── web/
│       ├── __init__.py
│       ├── app.py                  # FastAPI app factory
│       ├── dependencies.py         # FastAPI DI (get_db, get_templates)
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── dashboard.py        # Pipeline view (/) and Kanban (/kanban)
│       │   ├── grants.py           # Grant CRUD + status update (HTMX)
│       │   ├── prospects.py        # Prospect triage (/prospects)
│       │   └── stats.py            # Analytics dashboard (/stats)
│       ├── templates/
│       │   ├── base.html           # Dark mode layout with HTMX + Tailwind
│       │   ├── dashboard.html      # Pipeline overview by status
│       │   ├── kanban.html         # Drag-free kanban columns
│       │   ├── grant_detail.html   # Grant detail with inline status update
│       │   ├── add_grant.html      # Add grant form
│       │   ├── application.html    # LOI viewer
│       │   ├── prospects.html      # Prospect review table
│       │   ├── stats.html          # Analytics charts and counters
│       │   └── partials/
│       │       ├── grant_card.html       # HTMX swap target for status updates
│       │       ├── grant_list.html       # Reusable grant list
│       │       ├── prospect_row.html     # HTMX swap target for track/dismiss
│       │       ├── stats_cards.html      # Summary stat cards
│       │       └── status_counts.html    # Pipeline status badges
│       └── static/
│           └── app.css             # Dark mode theme overrides
└── .claude/
    ├── agents/
    │   └── company-researcher.md   # Sub-agent for org research
    └── skills/
        ├── grant-add/skill.md      # /grant-add — add a grant to tracker
        ├── grant-list/skill.md     # /grant-list — show pipeline
        ├── grant-match/skill.md    # /grant-match — score a URL against profile
        ├── grant-find/skill.md     # /grant-find — Chrome discovery from sources
        ├── grant-review/skill.md   # /grant-review — triage pending prospects
        └── grant-apply/skill.md    # /grant-apply — generate LOI + checklist
```

## Layer Responsibilities

### config (`config.py`)
Loads and validates `grant_profile.yaml` into a `GrantProfile` Pydantic model. Provides `get_project_root()` to locate the profile file regardless of CWD.

Must NOT: access the database, perform I/O beyond YAML reading.

```python
profile = load_profile()          # GrantProfile with startup, eligibility, funding_prefs
profile.startup.name              # "Flotexa"
profile.eligibility.sectors       # ["clean technology", "climate tech", ...]
```

### models (`models.py`)
All domain entities as Pydantic BaseModels. Enums use `StrEnum` for SQLite text storage compatibility.

Must NOT: contain business logic, import from other granthunt modules.

```python
class GrantStatus(StrEnum):
    DISCOVERED = "DISCOVERED"
    EVALUATING = "EVALUATING"
    PREPARING  = "PREPARING"
    SUBMITTED  = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED   = "APPROVED"
    REJECTED   = "REJECTED"
    WITHDRAWN  = "WITHDRAWN"
```

### db (`db.py`)
Raw `sqlite3` operations — no ORM. Each function takes a `sqlite3.Connection` and returns Pydantic models. `init_db()` creates tables and returns the connection.

Must NOT: contain business logic, call the CLI or web layers.

```python
conn = init_db()                        # create tables, return connection
grant = add_grant(conn, GrantCreate(...))
grant = get_grant(conn, grant_id)
grants = list_grants(conn, status_filter)
track_prospect(conn, prospect_id)       # creates Grant, updates Prospect status
```

### matcher (`matcher.py`)
Scores a `GrantCreate` against a `GrantProfile`. Returns a score result with overall score (0–100), per-category breakdown, highlights, and red flags.

Must NOT: access the database or network.

### scraper (`scraper.py`)
Fetches a grant posting URL with httpx, parses with BeautifulSoup, returns a `GrantCreate`. Used by `granthunt match <url>`.

Must NOT: access the database. Must NOT use Chrome (that is the `/grant-find` skill's domain).

### research (`research.py`)
Given an organization name, returns structured research (description, programs, funding signals, application tips). Called by `granthunt research <id>`.

### application (`application.py`)
Generates a Letter of Intent (LOI) draft for a grant. Reads `profile/flotexa.md` and optional `research.md` from the applications folder for personalization.

### cli (`cli.py`)
Typer app wiring all commands. Calls db, matcher, scraper, research, and application layers. Uses `rich` for terminal output.

Must NOT: contain business logic — delegates to domain layers.

### web (`web/`)
FastAPI app factory pattern. Each router gets `sqlite3.Connection` via `get_db` DI and `Jinja2Templates` via `get_templates`. HTMX partial responses use the `partials/` templates.

Must NOT: contain business logic — delegates to db layer directly.

```python
# Canonical router pattern
@router.post("/{grant_id}/status", response_class=HTMLResponse)
async def update_status(request: Request, grant_id: int, conn: DBDep, status: Annotated[GrantStatus, Form()]):
    update_grant(conn, grant_id, GrantUpdate(status=status))
    grant = get_grant(conn, grant_id)
    return templates.TemplateResponse("partials/grant_card.html", {"request": request, "grant": grant})
```

## Data Flow

### CLI Flow

1. `granthunt add <url> --title "..." --organization "..."` — CLI calls `add_grant(conn, GrantCreate(...))`, grant stored with `DISCOVERED` status.
2. `granthunt list` — reads all grants from SQLite, renders rich table with color-coded statuses.
3. `granthunt match <url>` — scraper fetches URL, matcher scores against `GrantProfile`, user optionally confirms add to tracker.
4. `granthunt update <id> --status PREPARING` — updates status field in SQLite.
5. `granthunt apply <id>` — reads grant + `profile/flotexa.md`, generates LOI, saves to `applications/{id}-{org}-{date}/loi.md`.

### Web Dashboard Flow

1. `granthunt serve` — uvicorn starts FastAPI at `http://127.0.0.1:8888`.
2. `GET /` — `dashboard.py` loads all grants, groups by status, renders `dashboard.html`.
3. `GET /kanban` — same data rendered as kanban columns.
4. `POST /grants/{id}/status` — HTMX posts new status, returns `partials/grant_card.html` fragment only.
5. `GET /prospects` — lists `PENDING` prospects sorted by `quick_score` desc.
6. `POST /prospects/{id}/track` — calls `track_prospect()`, returns empty string (HTMX deletes row).
7. `GET /stats` — aggregates counts, scores, stale grants, response rate.

### Grant Discovery Flow (Claude Code skill)

1. `/grant-find` — Claude reads `grant_sources.yaml`, uses Chrome automation (`mcp__claude-in-chrome`) to navigate each source.
2. Extracts grant listings (title, org, amount, deadline, URL) from each source page.
3. Scores each against `GrantProfile` using inline scoring logic (sector match, amount range, keywords).
4. Calls `granthunt add-prospect <url> --title "..." --organization "..." --score <n> --source <id>` for each result.
5. `/grant-review` — Claude lists `PENDING` prospects and processes user commands (`track 2,3`, `dismiss 9,10`, `dismiss <60`).

## Key Domain Concepts

| Concept | Description |
|---------|-------------|
| `Grant` | A tracked grant program: URL, title, organization, program, deadline, amount range, status, score, notes |
| `GrantProspect` | A discovered grant pending triage: lighter schema, `quick_score`, source identifier, `amount_range` as string |
| `GrantProfile` | Startup profile used for matching: `StartupInfo`, `EligibilityCriteria`, `FundingPrefs`, keyword boost/avoid lists |
| `GrantStatus` | Pipeline stage enum — 8 states (see state machine below) |
| `ProspectStatus` | Triage stage enum — 3 states: `PENDING`, `TRACKED`, `DISMISSED` |
| `ScrapeHistory` | Log entry per discovery run: source, query, timestamp, found/new counts |

## State Machines

### Grant Status

```
DISCOVERED ──► EVALUATING ──► PREPARING ──► SUBMITTED ──► UNDER_REVIEW ──► APPROVED
     │              │              │              │               │
     └──────────────┴──────────────┴──────────────┴───────────────┴──► REJECTED
     └──────────────┴──────────────┴──────────────┴───────────────┴──► WITHDRAWN
```

All active states can transition directly to `REJECTED` or `WITHDRAWN`. There is no enforced transition validation in the code — the CLI and web UI both accept any status update.

### Prospect Status

```
PENDING ──► TRACKED    (track_prospect() creates a Grant with DISCOVERED status)
        ──► DISMISSED  (dismiss_prospect() sets status, keeps the row)
```

## Web Dashboard Routes

| Route | Method | Handler | Purpose |
|-------|--------|---------|---------|
| `/` | GET | `dashboard.pipeline_view` | Pipeline overview grouped by status |
| `/kanban` | GET | `dashboard.kanban_view` | Kanban columns by status |
| `/grants/add` | GET | `grants.add_grant_modal` | Add grant form |
| `/grants/add` | POST | `grants.create_grant` | Create grant, redirect to `/` |
| `/grants/{id}` | GET | `grants.grant_detail` | Grant detail page |
| `/grants/{id}/status` | POST | `grants.update_status` | Update status, return HTMX partial |
| `/grants/{id}/notes` | POST | `grants.add_note` | Append timestamped note |
| `/grants/{id}/delete` | POST | `grants.delete_grant_route` | Delete grant, redirect to `/` |
| `/prospects` | GET | `prospects.prospect_review` | Prospect triage table |
| `/prospects/{id}/track` | POST | `prospects.track` | Track prospect (HTMX delete row) |
| `/prospects/{id}/dismiss` | POST | `prospects.dismiss` | Dismiss prospect (HTMX delete row) |
| `/stats` | GET | `stats.stats_dashboard` | Analytics: counts, scores, stale, rate |
