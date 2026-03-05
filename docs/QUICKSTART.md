# JobHunt Quick Guide

## The Workflow

```
Find Job → Match → Add (if good) → Research → Cover Letter → Apply → Track
```

---

## 1. Score a Job Before Adding

Found a job posting? Check if it's worth pursuing:

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

## 2. Track Your Pipeline

```bash
jobhunt list              # Active jobs (not rejected/withdrawn)
jobhunt list --all        # Everything
jobhunt list --status INTERVIEWING  # Filter by stage
jobhunt stats             # Dashboard
```

Stages: `NEW → INTERESTED → APPLIED → INTERVIEWING → OFFER`
(or `REJECTED` / `WITHDRAWN`)

---

## 3. Prepare to Apply

For a tracked job:

```bash
jobhunt research 1        # Company intel + interview questions
jobhunt cover-letter 1    # Draft from your resume
jobhunt cover-letter 1 -o cover_techcorp.md  # Save to file
```

---

## 4. Update Progress

```bash
jobhunt update 1 --status APPLIED
jobhunt update 1 --status INTERVIEWING --notes "Phone screen scheduled March 10"
jobhunt update 1 --score 92  # Manually adjust score after learning more
```

---

## 5. Claude Code Skills (Conversational)

Instead of CLI, just tell me:

- **"/job-match https://..."** - I'll analyze and recommend
- **"/job-add https://..."** - I'll add it for you
- **"/job-list"** - I'll show your pipeline
- **"/job-apply 1"** - I'll research + draft cover letter

---

## Your Profile (`job_profile.yaml`)

Already configured with your preferences:
- Target: CTO, VP Engineering, Technical Lead, Principal Architect
- Sweet spot: 200-2000 employees
- Love: BioTech, ClimateTech, Cybersecurity, Industrial
- Avoid: Finance, FinTech, IT Consulting, Staffing
- Must-have: AI/ML focus

Edit anytime to refine matching.

---

## Typical Session

```bash
# Morning: Check new postings
jobhunt match "https://linkedin.com/jobs/view/abc" --add
jobhunt match "https://company.com/careers/cto"

# Prep for application
jobhunt research 2
jobhunt cover-letter 2 -o covers/company_name.md
# Edit the draft, then apply

# Update status
jobhunt update 2 --status APPLIED --notes "Applied via website"

# End of week
jobhunt stats
```

---

## Command Reference

| Command | Description |
|---------|-------------|
| `jobhunt add <url>` | Add job to tracker |
| `jobhunt list [--status X] [--all]` | View pipeline |
| `jobhunt show <id>` | Job details |
| `jobhunt update <id> [--status X] [--notes X] [--score X]` | Update job |
| `jobhunt delete <id>` | Remove job |
| `jobhunt stats` | Pipeline dashboard |
| `jobhunt match <url> [--add]` | Score against profile |
| `jobhunt research <id>` | Company research |
| `jobhunt cover-letter <id> [-o FILE]` | Generate cover letter |
