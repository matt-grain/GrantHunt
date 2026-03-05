# Phase 1: Core Infrastructure

**Dependencies:** None
**Agent:** python-cli (general Python with typer CLI)

---

## Overview

Build the foundational infrastructure:
- Job profile configuration (YAML)
- SQLite database for tracking jobs
- CLI interface with typer
- Claude Code skills for `/job-add` and `/job-list`

---

## Files to Create

### `job_profile.yaml`

**Purpose:** Store user's job search preferences for matching
**Format:** YAML configuration file

```yaml
# Job Search Profile
name: "Matthieu Boujonnier"
location: "Montreal, QC"

target_roles:
  - "CTO"
  - "VP Engineering"
  - "VP of Engineering"
  - "Technical Lead"
  - "Principal Architect"
  - "Head of Engineering"

company_size:
  min: 200
  preferred: "200-2000"

industries:
  preferred:
    - "BioTech"
    - "HealthTech"
    - "Cybersecurity"
    - "Industrial"
    - "Manufacturing"
    - "Telecoms"
    - "Energy"
    - "Climate Tech"
  avoid:
    - "Finance"
    - "FinTech"
    - "Real Estate"
    - "IT Consulting"
    - "Staffing"

tech_focus:
  must_have:
    - "AI"
    - "ML"
    - "LLM"
    - "Machine Learning"
  nice_to_have:
    - "Python"
    - "Cloud"
    - "Azure"
    - "Architecture"
    - "IoT"

anti_patterns:
  - "pure management"
  - "no coding"
  - "legacy only"
  - "waterfall"

work_arrangement:
  - "remote"
  - "hybrid"
  - "onsite"

keywords_boost:
  - "AI-first"
  - "technical leadership"
  - "hands-on"
  - "architecture"
  - "product"

keywords_avoid:
  - "entry level"
  - "junior"
  - "contract"
  - "C2C"
```

---

### `src/jobhunt/__init__.py`

**Purpose:** Package initialization
**Content:** Version and exports

```python
__version__ = "0.1.0"
```

---

### `src/jobhunt/models.py`

**Purpose:** Data models for jobs
**Pattern:** Pydantic models + StrEnum for job status

**Enums:**
```python
class JobStatus(StrEnum):
    NEW = "NEW"
    INTERESTED = "INTERESTED"
    APPLIED = "APPLIED"
    INTERVIEWING = "INTERVIEWING"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
```

**Models:**
```python
class Job(BaseModel):
    id: int
    url: str
    title: str
    company: str
    location: str | None = None
    status: JobStatus = JobStatus.NEW
    score: float | None = None
    notes: str | None = None
    date_added: datetime
    date_updated: datetime
    raw_description: str | None = None

class JobCreate(BaseModel):
    url: str
    title: str
    company: str
    location: str | None = None
    notes: str | None = None

class JobUpdate(BaseModel):
    status: JobStatus | None = None
    score: float | None = None
    notes: str | None = None
```

**Constraints:**
- Use `datetime` for dates
- Use `StrEnum` for status (not raw strings) - enables JSON serialization
- Pydantic v2 syntax (`model_validator`, not `validator`)
- All optional fields have `None` defaults

---

### `src/jobhunt/config.py`

**Purpose:** Load and validate job profile configuration
**Dependencies:** pyyaml, pydantic

**Classes:**
- `IndustryPrefs`: preferred (list[str]), avoid (list[str])
- `TechFocus`: must_have (list[str]), nice_to_have (list[str])
- `CompanySize`: min (int), preferred (str)
- `JobProfile`: Full profile model with all fields from YAML

**Functions:**
- `load_profile(path: Path = None) -> JobProfile`: Load YAML, validate, return model
- Default path: `job_profile.yaml` in project root

**Constraints:**
- Raise clear error if profile not found
- Case-insensitive matching for industries/keywords

---

### `src/jobhunt/db.py`

**Purpose:** SQLite database operations
**Dependencies:** sqlite3 (stdlib), models

**Schema:**
```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    status TEXT DEFAULT 'NEW',
    score REAL,
    notes TEXT,
    raw_description TEXT,
    date_added TEXT NOT NULL,
    date_updated TEXT NOT NULL
);

CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_company ON jobs(company);
```

**Functions:**
- `init_db(path: Path = None) -> Connection`: Create tables if not exist
- `add_job(conn, job: JobCreate) -> Job`: Insert job, return with ID
- `get_job(conn, job_id: int) -> Job | None`: Get by ID
- `get_job_by_url(conn, url: str) -> Job | None`: Get by URL (for dedup)
- `list_jobs(conn, status: JobStatus = None) -> list[Job]`: List all or by status
- `update_job(conn, job_id: int, update: JobUpdate) -> Job`: Update fields
- `delete_job(conn, job_id: int) -> bool`: Delete job

**Constraints:**
- Default DB path: `jobs.db` in project root
- Use parameterized queries (no SQL injection)
- Return Pydantic models, not raw dicts/tuples
- Handle duplicate URL gracefully (return existing job)

---

### `src/jobhunt/cli.py`

**Purpose:** CLI interface using typer
**Dependencies:** typer, rich (for tables)

**Commands:**
- `jobhunt add <url> [--title] [--company] [--location] [--notes]`: Add a job
- `jobhunt list [--status STATUS] [--all]`: List jobs (default: active pipeline)
- `jobhunt show <id>`: Show job details
- `jobhunt update <id> --status STATUS [--notes]`: Update job status
- `jobhunt delete <id>`: Delete job
- `jobhunt stats`: Show pipeline statistics

**Output:**
- Use `rich.table.Table` for list output
- Color-code by status (NEW=blue, APPLIED=yellow, INTERVIEWING=green, etc.)
- Show count per status in stats

**Constraints:**
- Entry point: `jobhunt` command
- Graceful error handling with helpful messages
- Confirm before delete

---

### `.claude/skills/job-add/skill.md`

**Purpose:** Claude Code skill to add jobs via CLI

```markdown
# Add Job to Tracker

Add a job posting to your job search tracker.

## Usage

\`\`\`
/job-add <url> [title] [company]
\`\`\`

## Instructions

1. Run the jobhunt CLI to add the job:
   \`\`\`bash
   uv run jobhunt add "<url>" --title "<title>" --company "<company>"
   \`\`\`

2. If title/company not provided, the skill should fetch the page and extract them.

3. Report the result to the user.

## Example

\`\`\`
/job-add https://linkedin.com/jobs/view/123456
\`\`\`
```

---

### `.claude/skills/job-list/skill.md`

**Purpose:** Claude Code skill to list job pipeline

```markdown
# List Job Pipeline

Show your job search pipeline.

## Usage

\`\`\`
/job-list [status]
\`\`\`

## Instructions

1. Run the jobhunt CLI:
   \`\`\`bash
   uv run jobhunt list
   \`\`\`

   Or filter by status:
   \`\`\`bash
   uv run jobhunt list --status APPLIED
   \`\`\`

2. Display the results in a readable format.

## Statuses

- NEW: Just added, not yet reviewed
- INTERESTED: Worth pursuing
- APPLIED: Application submitted
- INTERVIEWING: In interview process
- OFFER: Received offer
- REJECTED: Rejected by company
- WITHDRAWN: Withdrew application
```

---

### `pyproject.toml` (MODIFY)

**Change:** Add dependencies and CLI entry point

**Dependencies to add:**
- `typer[all]>=0.9.0`
- `rich>=13.0.0`
- `pyyaml>=6.0`
- `pydantic>=2.0`
- `httpx>=0.27.0`

**Entry point to add:**
```toml
[project.scripts]
jobhunt = "jobhunt.cli:app"
```

**Exact changes:**
```toml
[project]
name = "interviews"
version = "0.1.0"
description = "Job search automation and interview preparation"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "typer[all]>=0.9.0",
    "rich>=13.0.0",
    "pyyaml>=6.0",
    "pydantic>=2.0",
    "httpx>=0.27.0",
]

[project.scripts]
jobhunt = "jobhunt.cli:app"
```

---

### `ARCHITECTURE.md`

**Purpose:** Document the project architecture

```markdown
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

\`\`\`
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
\`\`\`

## Data Flow

1. User runs `/job-add <url>` or `jobhunt add <url>`
2. CLI fetches job posting (if URL provided)
3. Job saved to SQLite with status=NEW
4. User runs `/job-list` to see pipeline
5. User updates status as they progress through applications

## Key Domain Concepts

- **Job:** A job posting with URL, title, company, status, score
- **JobProfile:** User's preferences for matching (roles, industries, tech)
- **JobStatus:** Pipeline stages (NEW → INTERESTED → APPLIED → INTERVIEWING → OFFER/REJECTED)

## State Machine: Job Status

\`\`\`
NEW → INTERESTED → APPLIED → INTERVIEWING → OFFER
  ↓        ↓           ↓            ↓           ↓
  └────────┴───────────┴────────────┴───────────┴→ REJECTED
  └────────┴───────────┴────────────┴───────────┴→ WITHDRAWN
\`\`\`
```

---

### `.gitignore` (MODIFY)

**Change:** Add database file to gitignore

**Exact change:** Add these lines:
```
# JobHunt database
jobs.db
```

---

## Implementation Order

1. `pyproject.toml` - Add dependencies
2. `.gitignore` - Add jobs.db
3. `job_profile.yaml` - Create profile config
4. `src/jobhunt/__init__.py` - Package init
5. `src/jobhunt/models.py` - Data models
6. `src/jobhunt/config.py` - Config loader
7. `src/jobhunt/db.py` - Database layer
8. `src/jobhunt/cli.py` - CLI commands
9. `.claude/skills/job-add/skill.md` - Skill
10. `.claude/skills/job-list/skill.md` - Skill
11. `ARCHITECTURE.md` - Documentation

---

## Verification

After implementation:
1. Run `uv sync` to install dependencies
2. Run `uv run jobhunt --help` to verify CLI works
3. Run `uv run jobhunt add "https://example.com/job" --title "Test" --company "Test Co"`
4. Run `uv run jobhunt list` to see the job
5. Run `uv run jobhunt stats` to see pipeline stats
