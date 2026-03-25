# GrantHunt — Agentic Grant Discovery & Tracking

Grant discovery and application tracking for startups, with **Claude Code skills** for AI-assisted grant finding, matching, and application preparation.

This is not just a grant tracker — it's designed to work **with Claude Code** as your grant search co-pilot. The skills in `.claude/skills/` let you say things like `/grant-find "clean tech"` and Claude will search grant sources, score matches, and save prospects for review.

![Screenshot](docs\screenshot.png)

## Quick Start

### 1. Install Dependencies

```bash
# Requires uv (https://docs.astral.sh/uv/)
uv sync
```

### 2. Create Your Profile

Copy and customize the example configs:

```bash
cp grant_profile.example.yaml grant_profile.yaml
cp grant_sources.example.yaml grant_sources.yaml
```

**Edit `grant_profile.yaml`** with:
- Your startup name, description, industry, stage
- Eligible sectors and activities
- Funding preferences (amount range, types)
- Keywords that boost or lower grant relevance

**Edit `grant_sources.yaml`** with:
- Grant sources relevant to your region (federal, provincial, academic)
- Priority ranking (1 = highest relevance)
- URLs and notes for each source

### 3. (Optional) Create Company Profile

Create `profile/company.md` with a detailed description of your startup. This is used by the LOI (Letter of Intent) generator:

```bash
mkdir -p profile
# Create profile/company.md with your company description
```

### 4. Run the Web Dashboard

```bash
uv run granthunt serve              # http://127.0.0.1:8888
uv run granthunt serve --reload     # with hot reload
```

## Using with Claude Code

The real power is in the Claude Code skills. Open the project with Claude Code:

```bash
claude
```

### Available Skills

| Skill | Description |
|-------|-------------|
| `/grant-find [query]` | Search grant sources, score matches, save to prospects |
| `/grant-match <url>` | Analyze a grant against your profile |
| `/grant-add <url>` | Add a grant to your tracker |
| `/grant-list` | Show all tracked grants |
| `/grant-review` | Interactive review of pending prospects |
| `/grant-apply <id>` | Generate LOI draft + research + checklist |

### Example Workflow

```
> /grant-find "clean technology R&D"
# Claude searches configured sources, scores grants, saves 15 prospects

> /grant-review
# Claude shows each prospect, you say "track" or "dismiss"

> /grant-match https://innovation.gov/grants/cleantech-2026
# Claude analyzes the grant, shows eligibility score breakdown

> /grant-apply 3
# Claude researches the organization, drafts an LOI
```

### Chrome Integration (for grant discovery)

Grant discovery requires Chrome automation. Start Claude with Chrome:

```bash
claude --chrome
```

Or connect mid-session with `/chrome`.

## Features

- **Pipeline tracking**: `DISCOVERED` → `EVALUATING` → `PREPARING` → `SUBMITTED` → `UNDER_REVIEW` → `APPROVED`
- **Profile-based scoring**: Match grants against your startup profile
- **Web dashboard**: Pipeline view, kanban board, prospect triage, analytics
- **LOI generation**: Draft Letters of Intent with organization research
- **Multi-source discovery**: Chrome-based search across configured grant sources

## CLI Commands

### Grant Tracking

```bash
uv run granthunt add <url> --title "Title" --organization "Org"
uv run granthunt list                         # active grants
uv run granthunt list --status PREPARING      # filter by status
uv run granthunt show <id>                    # grant details
uv run granthunt update <id> --status SUBMITTED
uv run granthunt update <id> --deadline 2026-06-01
uv run granthunt delete <id>
uv run granthunt stats                        # pipeline statistics
```

### Grant Evaluation

```bash
uv run granthunt match <url>                  # score against profile
uv run granthunt match <url> --add            # score and add
uv run granthunt research <id>                # research the organization
```

### Application Materials

```bash
uv run granthunt apply <id>                   # generate LOI to stdout
uv run granthunt apply <id> --output loi.md   # save to file
```

### Prospect Management

```bash
uv run granthunt prospects                    # list all prospects
uv run granthunt prospects --pending          # pending only
uv run granthunt review                       # interactive triage
uv run granthunt track <prospect_id>          # promote to tracked
uv run granthunt dismiss <prospect_id>        # not interested
```

## Project Structure

```
src/granthunt/
├── cli.py              # Typer CLI commands
├── config.py           # Profile and settings loader
├── db.py               # SQLite database layer
├── models.py           # Pydantic models & enums
├── scraper.py          # Grant page scraper
├── matcher.py          # Grant-profile matching/scoring
├── research.py         # Organization research with AI
├── application.py      # LOI generation
└── web/
    ├── app.py          # FastAPI app factory
    ├── routers/        # Dashboard, grants, prospects, stats
    ├── templates/      # Jinja2 HTML templates (dark mode)
    └── static/         # CSS assets

.claude/
├── skills/             # Claude Code slash commands
│   ├── grant-find/     # Grant discovery with Chrome
│   ├── grant-match/    # Score a grant against profile
│   ├── grant-add/      # Add grant to tracker
│   ├── grant-list/     # List tracked grants
│   ├── grant-review/   # Review prospects
│   └── grant-apply/    # LOI generation
└── agents/
    └── company-researcher.md  # Subagent for org research

grant_profile.yaml      # Your startup profile (create from example)
grant_sources.yaml      # Grant sources config (create from example)
profile/company.md      # Detailed company description for LOIs
```

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for dependency management
- [Claude Code](https://claude.ai/claude-code) for the AI-assisted features
- Chrome browser (for grant discovery via `/grant-find`)

## License

MIT
