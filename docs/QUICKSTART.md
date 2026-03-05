# JobHunt Quick Guide

## The Workflow

```
Discover → Review Prospects → Track → Research → Cover Letter → Apply → Update
    │           │                │
    │           │                └── jobs table (your pipeline)
    │           └── job_prospects table (staging area)
    └── /job-find searches multiple sources
```

---

## 1. Discover Jobs (NEW!)

Use Chrome automation to search multiple job boards:

```bash
# In Claude Code with Chrome connected:
/job-find "CTO AI Montreal"           # Search LinkedIn (default)
/job-find "VP Engineering" --all-sources  # Search all enabled sources
```

Or search specific sources:
```bash
/job-find "Technical Lead" --source indeed
/job-find "Head of Engineering" --source jobboom
```

**Enabled sources** (in `job_sources.yaml`):
- LinkedIn, Indeed.ca, Jobboom, TechnoMontreal, Wellfound

Results are saved to the **prospects table** for later review.

---

## 2. Review Prospects (NEW!)

Prospects are staged jobs awaiting your decision:

```bash
jobhunt prospects             # List all prospects
jobhunt prospects --pending   # Show only pending review
jobhunt scrape-history        # See when sources were last scraped
```

**Triage options:**
```bash
jobhunt track 3               # Move prospect #3 to your pipeline
jobhunt dismiss 5             # Not interested in #5
jobhunt review                # Interactive review (t/d/s/q)
```

Or use the Claude Code skill:
```
/job-review                   # Interactive triage session
```

---

## 3. Score a Job Before Adding

Found a job posting manually? Check if it's worth pursuing:

```bash
jobhunt match "https://linkedin.com/jobs/view/123456"
```

This scrapes the posting and scores it against your `job_profile.yaml`:
- **Role fit** (30%) - Does the title match CTO/VP Eng/etc?
- **Keywords** (25%) - AI, ML, Python, Cloud mentioned?
- **Industry** (20%) - BioTech/ClimateTech (good) vs Finance (avoid)?
- **Red flags** (25%) - "Unlimited PTO", "Fast-paced", 10+ years required?

Output: Score + recommendation (STRONG MATCH / WORTH CONSIDERING / SKIP)

Add `--add` to auto-track if score > 70:
```bash
jobhunt match "https://..." --add
```

---

## 4. Track Your Pipeline

```bash
jobhunt list              # Active jobs (not rejected/withdrawn)
jobhunt list --all        # Everything
jobhunt list --status INTERVIEWING  # Filter by stage
jobhunt stats             # Dashboard
```

Stages: `NEW → INTERESTED → APPLIED → INTERVIEWING → OFFER`
(or `REJECTED` / `WITHDRAWN`)

---

## 5. Prepare to Apply

For a tracked job:

```bash
jobhunt research 1        # Company intel + interview questions
jobhunt cover-letter 1    # Draft from your resume
jobhunt cover-letter 1 -o cover_techcorp.md  # Save to file
```

Or use the all-in-one skill:
```
/job-apply 1              # Research + cover letter + save to applications/
```

---

## 6. Update Progress

```bash
jobhunt update 1 --status APPLIED
jobhunt update 1 --status INTERVIEWING --notes "Phone screen scheduled March 10"
jobhunt update 1 --score 92  # Manually adjust score after learning more
```

---

## Claude Code Skills (Conversational)

Instead of CLI, just tell me:

| Skill | What it does |
|-------|--------------|
| `/job-find "query"` | Search job boards, save to prospects |
| `/job-review` | Interactive prospect triage |
| `/job-match https://...` | Analyze and recommend |
| `/job-add https://...` | Add directly to pipeline |
| `/job-list` | Show your pipeline |
| `/job-apply 1` | Research + draft cover letter |

---

## Configuration Files

### `job_profile.yaml` - Your Preferences
- Target: CTO, VP Engineering, Technical Lead, Principal Architect
- Sweet spot: 200-2000 employees
- Love: BioTech, ClimateTech, Cybersecurity, Industrial
- Avoid: Finance, FinTech, IT Consulting, Staffing
- Must-have: AI/ML focus

### `job_sources.yaml` - Job Board Configuration (NEW!)
- URL patterns for each source
- Enable/disable sources
- Extraction selectors for Chrome automation

---

## Typical Session

```bash
# Morning: Discover new jobs
/job-find "CTO AI"                    # In Claude Code with Chrome

# Review what was found
jobhunt prospects --pending           # 15 pending review
jobhunt review                        # Interactive: t=track, d=dismiss, s=skip

# Prep for application
jobhunt research 2
jobhunt cover-letter 2 -o covers/company_name.md
# Edit the draft, then apply

# Update status
jobhunt update 2 --status APPLIED --notes "Applied via website"

# End of week
jobhunt stats
jobhunt scrape-history                # Check source coverage
```

---

## Command Reference

### Pipeline Management
| Command | Description |
|---------|-------------|
| `jobhunt add <url>` | Add job directly to tracker |
| `jobhunt list [--status X] [--all]` | View pipeline |
| `jobhunt show <id>` | Job details |
| `jobhunt update <id> [--status X] [--notes X] [--score X]` | Update job |
| `jobhunt delete <id>` | Remove job |
| `jobhunt stats` | Pipeline dashboard |

### Job Analysis
| Command | Description |
|---------|-------------|
| `jobhunt match <url> [--add]` | Score against profile |
| `jobhunt research <id>` | Company research |
| `jobhunt cover-letter <id> [-o FILE] [-r research.md]` | Generate cover letter |

### Prospect Management (NEW!)
| Command | Description |
|---------|-------------|
| `jobhunt prospects [--pending] [--status X]` | List prospects |
| `jobhunt track <id>` | Move prospect to pipeline |
| `jobhunt dismiss <id>` | Mark as not interested |
| `jobhunt review` | Interactive triage session |
| `jobhunt add-prospect <url> -t TITLE -c COMPANY` | Add prospect manually |
| `jobhunt scrape-history [--source X]` | View scrape history |
