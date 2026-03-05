# Job Review - Review Pending Prospects

Review discovered job prospects and decide which to track or dismiss.

## Usage

```
/job-review
```

## Instructions

### 1. List Pending Prospects

Query the database directly to get full details:

```python
from jobhunt.db import init_db, list_prospects
from jobhunt.models import ProspectStatus

conn = init_db()
prospects = list_prospects(conn, ProspectStatus.PENDING)
conn.close()
```

If no prospects pending, inform the user:
```
No pending prospects to review.
Run /job-find to discover new opportunities.
```

### 2. Present Options

Display prospects with full details including URL, summary, and salary:

```
Pending Prospects (9 to review)

[2] 88 - Chef des solutions intégrées
    CAE | Montreal, QC
    Salary: -
    Summary: Leadership role in integrated solutions...
    https://linkedin.com/jobs/view/...

[3] 85 - Technical Cloud & AI Strategy Lead
    MTY Food Group | Montreal, QC (Hybrid)
    Salary: -
    Summary: Drive AI strategy and cloud transformation...
    https://linkedin.com/jobs/view/...

[12] 75 - Senior Scientist – Agentic AI Systems
    Sanofi | Toronto, ON
    Salary: CAD 108,900 - 157,300
    Summary: Join the digital engine driving Sanofi's transformation...
    https://biotalent.ca/the-petridish/...

...

Commands:
- "track 2,3,4" - Move IDs to pipeline
- "dismiss 9,10" - Not interested
- "dismiss <60" - Dismiss all below score 60
- "preview 2" - Open URL in Chrome
- "done" - Finish review
```

### 3. Process User Commands

**Track command:**
```bash
uv run jobhunt track <id>
```

**Dismiss command:**
```bash
uv run jobhunt dismiss <id>
```

**Preview command:**
Use Chrome tools to navigate to the job URL for detailed view.

**Bulk operations:**
For "track all" or "dismiss <score", loop through matching prospects.

### 4. Summary

After processing, show summary:
```
Review complete:
- 3 jobs tracked (moved to pipeline)
- 2 jobs dismissed
- 4 prospects remaining

Run /job-list to see your updated pipeline.
```

## Display Format

For each prospect, show:
- **[ID] Score** - Title
- Company | Location
- **Salary:** (if available, else "-")
- **Summary:** First 100 chars (if available)
- URL (clickable)

This gives enough context to decide without opening each link.

## Interactive Mode

Alternatively, run the interactive CLI review:
```bash
uv run jobhunt review
```

This walks through each prospect one by one with t/d/s/q commands.
