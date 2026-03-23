# GrantHunt

Grant discovery and application tracking for climate tech startups.

Built for [Flotexa](https://flotexa.ca/) (Quebec, Canada) to find, evaluate, and manage grants through a full pipeline from discovery to approval.

## Quick Start

```bash
# Install dependencies
uv sync

# See all commands
uv run granthunt --help

# Start the web dashboard
uv run granthunt serve              # http://127.0.0.1:8888
uv run granthunt serve --reload     # with hot reload (development)
uv run granthunt serve --port 9999  # custom port
```

## Features

- Track grants through a full pipeline: `DISCOVERED` → `EVALUATING` → `PREPARING` → `SUBMITTED` → `UNDER_REVIEW` → `APPROVED`
- Score grants against your startup profile (sector, amount, keywords)
- Web dashboard with pipeline view, kanban board, prospect triage, and analytics
- Generate Letters of Intent (LOI) with organization research context
- Chrome-based grant discovery from 12+ federal, Quebec, climate, and academic sources
- Claude Code skills for hands-free discovery and review workflow

## Configuration

| File | Purpose |
|------|---------|
| `grant_profile.yaml` | Startup profile: sector, stage, location, funding preferences, keyword boost/avoid lists |
| `grant_sources.yaml` | Grant source configurations with priority, URL, and category |
| `profile/flotexa.md` | Detailed company description used by LOI generation |

## CLI Commands

### Grant Tracking

```bash
uv run granthunt add <url> --title "Title" --organization "Org"
uv run granthunt list                         # active grants (excludes REJECTED/WITHDRAWN)
uv run granthunt list --status PREPARING      # filter by status
uv run granthunt list --all                   # include REJECTED and WITHDRAWN
uv run granthunt show <id>                    # grant details panel
uv run granthunt update <id> --status SUBMITTED
uv run granthunt update <id> --notes "Submitted LOI" --deadline 2026-06-01
uv run granthunt delete <id>
uv run granthunt stats                        # pipeline statistics
```

### Grant Evaluation

```bash
uv run granthunt match <url>                  # score a grant URL against your profile
uv run granthunt match <url> --add            # score and add to tracker
uv run granthunt research <id>                # research the granting organization
```

### Application Materials

```bash
uv run granthunt apply <id>                   # generate LOI draft to stdout
uv run granthunt apply <id> --output loi.md   # save to file
uv run granthunt apply <id> --research applications/1-nrc-2026/research.md
```

### Prospect Management

```bash
uv run granthunt prospects                    # list all prospects
uv run granthunt prospects --pending          # pending only
uv run granthunt review                       # interactive triage (t/d/s/q)
uv run granthunt track <prospect_id>          # promote to tracked grant
uv run granthunt dismiss <prospect_id>        # not interested
uv run granthunt add-prospect <url> --title "Title" --organization "Org" --source irap
uv run granthunt scrape-history               # view discovery run history
```

### Web Dashboard

```bash
uv run granthunt serve                        # http://127.0.0.1:8888
```

## Grant Sources

Sources are configured in `grant_sources.yaml` with priority 1 (highest) to 5 (lowest).

**Federal (Canada-wide)**
- Innovation Canada — federal portal aggregating NRC, ISED programs
- NRC IRAP — flagship SME R&D support program
- SDTC — non-repayable contributions for clean technology
- SR&ED — federal R&D tax credit (refundable for CCPCs)
- Clean Growth Hub — federal clean tech funding navigator

**Quebec (Provincial)**
- MEI — Quebec's primary economic development ministry
- Investissement Quebec — provincial development bank and grant administrator
- PME MTL — Montreal-area SME support and micro-loans
- Fonds vert — Quebec green fund for climate plan projects

**Climate & Sector-Specific**
- EcoAction — ECCC community environmental project funding

**Academic / Collaborative**
- Mitacs Accelerate — subsidized graduate student R&D internships (~$15K/intern)
- NSERC Alliance — industry-university collaborative grants with matching

## Skills (Claude Code)

| Skill | Usage | Description |
|-------|-------|-------------|
| `/grant-add` | `/grant-add <url>` | Add a grant URL to the tracker |
| `/grant-list` | `/grant-list [status]` | Show the pipeline |
| `/grant-match` | `/grant-match <url>` | Score a URL against your profile |
| `/grant-find` | `/grant-find [query]` | Chrome-based discovery from configured sources |
| `/grant-review` | `/grant-review` | Triage pending prospects (track/dismiss) |
| `/grant-apply` | `/grant-apply <id>` | Generate LOI + research + checklist |

The `/grant-find` skill requires Chrome connection (`claude --chrome` or `/chrome`).
