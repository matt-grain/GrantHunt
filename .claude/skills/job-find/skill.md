# Job Discovery - Find Matching Opportunities

Discover job opportunities using Chrome browser automation. Searches job boards, extracts listings, scores against your profile, and saves to prospects for later review.

## Prerequisites

**Requires Chrome connection.** If not connected:
```
/chrome
```
Or restart session with `claude --chrome`

## Usage

```
/job-find [search query]
```

Examples:
- `/job-find` - Uses defaults from job_profile.yaml
- `/job-find "CTO AI Montreal"`
- `/job-find "VP Engineering climate tech remote"`

## Instructions

### 1. Load Job Profile

Read `job_profile.yaml` to get:
- Target roles
- Preferred industries
- Must-have keywords
- Location preferences
- Company size preferences

Build search query from profile if none provided.

### 2. Search LinkedIn Jobs

**Navigate to LinkedIn Jobs search:**
```
https://www.linkedin.com/jobs/search/?keywords=[query]&location=[location]
```

Use the Chrome tools to:
1. Navigate to the URL
2. Wait for job cards to load
3. Scroll to load more results (2-3 scrolls for ~20-30 jobs)

### 3. Extract Job Listings

For each visible job card, extract:
- Job title
- Company name
- Location
- Posted date (if visible)
- Job URL (the href from the card)

Create a list of extracted jobs.

### 4. Score Each Job

For each extracted job, calculate a quick score based on:

**Role Match (40%):**
- Exact match to target_roles: 100%
- Partial match (contains keywords): 70%
- Leadership indicator (Head of, VP, Director, Lead): +20%

**Industry/Company (30%):**
- Known preferred industry: 100%
- Known avoid industry: 0%
- Unknown: 50%

**Location (30%):**
- Matches preferred location: 100%
- Remote when remote-friendly: 100%
- Other: 50%

### 5. Save to Prospects Database

**IMPORTANT:** Save ALL discovered jobs to the prospects table for later review.

For each job, run:
```bash
uv run jobhunt add-prospect "<url>" \
  --title "<title>" \
  --company "<company>" \
  --location "<location>" \
  --score <quick_score> \
  --source linkedin
```

Or use Python directly:
```python
from jobhunt.db import init_db, add_prospect
from jobhunt.models import ProspectCreate

conn = init_db()
prospect = add_prospect(conn, ProspectCreate(
    url=url,
    title=title,
    company=company,
    location=location,
    quick_score=score,
    source="linkedin",
))
conn.close()
```

### 6. Present Summary

Display results sorted by score:

```
Job Discovery Complete - Found 24 opportunities

Top Matches:
#   Score  Title                        Company          Location
----------------------------------------------------------------------
1   92     CTO                          ClimateAI        Montreal
2   88     VP Engineering               BioTech Corp     Remote
3   85     Head of Data & AI            CAE              Montreal
4   81     Principal Architect          HealthTech       Toronto
5   76     Technical Lead               StartupXYZ       Montreal
...

Filtered Out (avoid industries):
- AI/ML Sector Lead at Morgan Stanley (Finance)
- Director at Deloitte (IT Consulting)

Saved 24 prospects to review queue.
Run /job-review to track or dismiss prospects.
```

### 7. Next Steps

Inform the user:
```
Next steps:
- Run /job-review for interactive triage
- Run `jobhunt prospects --pending` to see all pending
- Run `jobhunt track <id>` to move a prospect to pipeline
- Run `jobhunt dismiss <id>` to remove from review queue
```

## Multi-Site Search (Optional)

If user requests, also search:
- Indeed: `https://www.indeed.com/jobs?q=[query]&l=[location]`
- Glassdoor: `https://www.glassdoor.com/Job/jobs.htm?sc.keyword=[query]`

Extract and merge results, deduplicate by company+title.

## Error Handling

**If Chrome not connected:**
```
Chrome connection required for job discovery.
Run /chrome to connect, or restart with: claude --chrome
```

**If LinkedIn blocks/CAPTCHA:**
```
LinkedIn requires verification. Please:
1. Complete the CAPTCHA in the browser
2. Say "continue" when ready
```

**If no results:**
```
No jobs found matching your criteria.
Try broadening your search or check different keywords.
```

## Tips

- Run during off-peak hours for better LinkedIn response
- Stay logged into LinkedIn before starting
- For best results, have LinkedIn Jobs notifications enabled (shows fresher posts)
- Use specific keywords for better matching
- Prospects are deduplicated by URL - safe to re-run searches
