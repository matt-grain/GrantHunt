# Job Discovery - Find Matching Opportunities

Discover job opportunities using Chrome browser automation. Searches multiple job boards, extracts listings, scores against your profile, and saves to prospects for later review.

## Prerequisites

**Requires Chrome connection.** If not connected:
```
/chrome
```
Or restart session with `claude --chrome`

## Usage

```
/job-find [search query] [--source <name>] [--all-sources]
```

Examples:
- `/job-find` - Uses defaults from job_profile.yaml, searches LinkedIn
- `/job-find "CTO AI Montreal"` - Search LinkedIn with query
- `/job-find "CTO AI" --source indeed` - Search Indeed only
- `/job-find "VP Engineering" --all-sources` - Search all enabled sources

## Instructions

### 1. Load Configuration

Read `job_profile.yaml` for search criteria:
- Target roles, preferred industries, keywords, location

Read `job_sources.yaml` for enabled sources:
- URL patterns, extraction selectors, priorities

### 2. Determine Sources to Search

**Default:** LinkedIn only (priority 1, most reliable)

**With --source <name>:** Search specified source only
- `linkedin`, `indeed`, `jobboom`, `technomontreal`, `wellfound`, `biotalent`

**With --all-sources:** Search all enabled sources in priority order

### 3. For Each Source

#### 3a. Build Search URL

```python
# From job_sources.yaml
url_template = source["search_url"]
url = url_template.format(
    query=urllib.parse.quote(search_query),
    location=urllib.parse.quote(location)
)
```

#### 3b. Navigate and Extract

Use Chrome tools to:
1. Navigate to the search URL
2. Wait for job cards to load (2-3 seconds)
3. Take screenshot to verify page loaded
4. Scroll 2-3 times to load more results
5. Extract job listings using read_page or javascript_tool

#### 3c. Extract Job Data

For each job card found, extract:
- **title**: Job title text
- **company**: Company name
- **location**: Location text
- **url**: Link to job posting (href)

**LinkedIn example extraction (javascript_tool):**
```javascript
Array.from(document.querySelectorAll('.job-card-container')).map(card => ({
  title: card.querySelector('.job-card-list__title')?.innerText?.trim(),
  company: card.querySelector('.job-card-container__company-name')?.innerText?.trim(),
  location: card.querySelector('.job-card-container__metadata-item')?.innerText?.trim(),
  url: card.querySelector('a')?.href
})).filter(j => j.title && j.company)
```

**Indeed example:**
```javascript
Array.from(document.querySelectorAll('.job_seen_beacon')).map(card => ({
  title: card.querySelector('.jobTitle')?.innerText?.trim(),
  company: card.querySelector('.companyName')?.innerText?.trim(),
  location: card.querySelector('.companyLocation')?.innerText?.trim(),
  url: 'https://ca.indeed.com' + card.querySelector('a')?.getAttribute('href')
})).filter(j => j.title && j.company)
```

### 4. Score Each Job

Calculate quick score based on job_profile.yaml:

**Role Match (40%):**
- Exact match to target_roles: 100%
- Partial match (contains keywords like CTO, VP, Director): 70%
- Leadership indicator bonus: +20%

**Industry/Company (30%):**
- Known preferred industry: 100%
- Known avoid industry: 0%
- Unknown: 50%

**Location (30%):**
- Matches preferred location (Montreal): 100%
- Remote when remote-friendly: 100%
- Other Canadian cities: 70%
- Other: 50%

### 5. Filter and Deduplicate

**Filter out:**
- Jobs from avoid industries (Finance, FinTech, Real Estate, IT Consulting, Staffing)
- Duplicate listings (same company + similar title across sources)

**Deduplication:**
```python
seen = set()
unique_jobs = []
for job in all_jobs:
    key = f"{job.company.lower()}|{job.title.lower()[:30]}"
    if key not in seen:
        seen.add(key)
        unique_jobs.append(job)
```

### 6. Save to Prospects Database

Save ALL discovered jobs to the prospects table:

```bash
uv run jobhunt add-prospect "<url>" \
  --title "<title>" \
  --company "<company>" \
  --location "<location>" \
  --score <quick_score> \
  --source <source_name>
```

Or batch via Python:
```python
from jobhunt.db import init_db, add_prospect
from jobhunt.models import ProspectCreate

conn = init_db()
for job in unique_jobs:
    add_prospect(conn, ProspectCreate(
        url=job["url"],
        title=job["title"],
        company=job["company"],
        location=job["location"],
        quick_score=job["score"],
        source=source_name,
    ))
conn.close()
```

### 7. Present Summary

```
Job Discovery Complete

Sources searched:
  - LinkedIn: 24 jobs found
  - Indeed: 18 jobs found
  - Jobboom: 6 jobs found
  Total: 48 jobs, 41 unique after deduplication

Top Matches (score >= 70):
#   Score  Title                        Company          Source
----------------------------------------------------------------------
1   92     CTO                          ClimateAI        linkedin
2   88     VP Engineering               BioTech Corp     indeed
3   85     Head of Data & AI            CAE              linkedin
4   81     Principal Architect          HealthTech       jobboom
5   76     Technical Lead               StartupXYZ       wellfound

Filtered Out (avoid industries): 7 jobs
  - Morgan Stanley, Deloitte, KPMG, etc.

Saved 41 prospects to review queue.
Run /job-review to track or dismiss prospects.
```

## Source-Specific Notes

### LinkedIn
- Most reliable extraction
- Requires login for full results
- Shows "Promoted" jobs first

### Indeed Canada
- Good coverage, many duplicates from LinkedIn
- Uses infinite scroll
- Shows sponsored listings prominently

### Jobboom
- Quebec-focused, good for local companies
- Mixed French/English listings
- Smaller but relevant set

### TechnoMontreal
- Montreal tech ecosystem jobs
- Smaller pool but highly targeted
- Good for startup/scale-up roles

### Wellfound
- Startup and VC-backed companies
- Good for CTO/VP-level roles
- Requires account for some listings

### BioTalent Canada
- BioTech/HealthTech specific
- Enable when searching those industries
- Smaller but matches your profile preferences

## Error Handling

**If source fails to load:**
```
[!] Indeed search failed: timeout waiting for job cards
    Continuing with other sources...
```

**If Chrome not connected:**
```
Chrome connection required for job discovery.
Run /chrome to connect, or restart with: claude --chrome
```

**If CAPTCHA encountered:**
```
[source] requires verification. Please:
1. Complete the CAPTCHA in the browser
2. Say "continue" when ready
```

## Tips

- LinkedIn alone usually has 80%+ of relevant listings
- Use --all-sources for comprehensive search (takes longer)
- Run during off-peak hours for faster page loads
- Prospects are deduplicated by URL - safe to re-run
- Check job_sources.yaml to enable/disable sources
