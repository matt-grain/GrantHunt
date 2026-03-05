# JobHunt Architecture

## Overview

Job search automation system for tracking opportunities, matching against profile, and managing the application pipeline.

## Tech Stack

- **Language:** Python 3.13
- **Package Manager:** uv
- **Database:** SQLite
- **CLI:** typer + rich
- **HTTP:** httpx
- **Config:** YAML + Pydantic

## Project Structure

```
interviews/
├── job_profile.yaml          # Job search preferences
├── jobs.db                    # SQLite database (gitignored)
├── src/
│   └── jobhunt/
│       ├── __init__.py
│       ├── models.py          # Pydantic models + enums
│       ├── config.py          # Profile loading
│       ├── db.py              # Database operations
│       ├── cli.py             # typer CLI
│       ├── scraper.py         # Job posting fetcher (Phase 2)
│       └── matcher.py         # Scoring engine (Phase 2)
├── .claude/skills/
│   ├── job-add/               # /job-add skill
│   ├── job-list/              # /job-list skill
│   └── job-match/             # /job-match skill (Phase 2)
├── profile/                   # Resume and LinkedIn exports
└── docs/                      # Interview prep materials
```

## Data Flow

1. User runs `/job-add <url>` or `jobhunt add <url>`
2. CLI adds job to SQLite with status=NEW
3. User runs `/job-list` to see pipeline
4. User updates status as they progress through applications

## Key Domain Concepts

- **Job:** A job posting with URL, title, company, status, score
- **JobProfile:** User's preferences for matching (roles, industries, tech)
- **JobStatus:** Pipeline stages (NEW → INTERESTED → APPLIED → INTERVIEWING → OFFER/REJECTED)

## State Machine: Job Status

```
NEW → INTERESTED → APPLIED → INTERVIEWING → OFFER
  ↓        ↓           ↓            ↓           ↓
  └────────┴───────────┴────────────┴───────────┴→ REJECTED
  └────────┴───────────┴────────────┴───────────┴→ WITHDRAWN
```
