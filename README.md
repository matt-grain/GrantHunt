# JobHunt — Job Search Automation & Interview Prep

Job pipeline tracker with CLI and web dashboard, plus interactive study tools for AI/ML interview preparation.

## Quick Start

```bash
# Install dependencies
uv sync

# Run the web dashboard
uv run jobhunt serve              # http://127.0.0.1:9999
uv run jobhunt serve --reload     # with hot reload for development
uv run jobhunt serve --port 8080  # custom port
```

## CLI Commands

### Job Tracking
```bash
uv run jobhunt add <url> --title "Job Title" --company "Company"
uv run jobhunt list                    # show all jobs
uv run jobhunt list --status applied   # filter by status
uv run jobhunt show <job_id>           # job details
uv run jobhunt update <job_id> --status interviewing
uv run jobhunt delete <job_id>
uv run jobhunt stats                   # pipeline statistics
```

### Job Discovery
```bash
uv run jobhunt match <url>             # score a job posting against your profile
uv run jobhunt match <url> --add       # score and add to tracker
uv run jobhunt research <job_id>       # research a company
uv run jobhunt cover-letter <job_id>   # generate cover letter
```

### Prospects (Auto-scraped Jobs)
```bash
uv run jobhunt prospects               # list prospects
uv run jobhunt review                  # interactive review of pending prospects
uv run jobhunt track <prospect_id>     # promote to tracked job
uv run jobhunt dismiss <prospect_id>   # dismiss a prospect
uv run jobhunt add-prospect <url> --title "Title" --company "Co" --source "Source"
uv run jobhunt scrape-history          # view scrape history
```

### Web Dashboard
```bash
uv run jobhunt serve                   # start at http://127.0.0.1:9999
```

## Project Structure

```
src/jobhunt/
├── cli.py              # Typer CLI commands
├── config.py           # Profile and settings
├── db.py               # SQLite database layer
├── models.py           # Pydantic models & enums
├── scraper.py          # Job posting scraper
├── matcher.py          # Job-profile matching/scoring
├── research.py         # Company research
├── cover_letter.py     # Cover letter generation
└── web/
    ├── app.py          # FastAPI app factory
    ├── dependencies.py # Shared dependencies
    ├── routers/        # Dashboard, jobs, prospects, stats
    ├── templates/      # Jinja2 HTML templates
    └── static/         # CSS, JS assets

study/                  # Interview preparation
├── STUDY_PLAN.md       # 19 modules across 3 tiers
├── PROGRESS.md         # Per-module scoring tracker
├── sessions/           # Saved quiz sessions
└── cheatsheets/        # Generated reference sheets

jobs/                   # Per-company application materials
├── Sanofi-AI-ML-Lead/
├── AMI-LeCun/
└── LawZero/

docs/                   # Study materials (pptx, pdf, epub)
profile/                # Resume and profile documents
```
