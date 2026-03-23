# Grant Review - Review Pending Prospects

Review discovered grant prospects and decide which to track or dismiss.

## Usage

```
/grant-review
```

## Instructions

### 1. List Pending Prospects

Query the database directly to get full details:

```python
from granthunt.db import init_db, list_prospects
from granthunt.models import ProspectStatus

conn = init_db()
prospects = list_prospects(conn, ProspectStatus.PENDING)
conn.close()
```

If no prospects pending, inform the user:
```
No pending prospects to review.
Run /grant-find to discover new opportunities.
```

### 2. Present Options

Display prospects with full details including score, organization, amount range, and deadline:

```
Pending Prospects (8 to review)

[1] 92 - Industrial Research Assistance Program
    NRC IRAP | Federal
    Amount: $50,000 – $500,000 | Deadline: rolling
    Summary: Non-dilutive funding for R&D salaries and contractors...
    https://nrc.canada.ca/en/support-technology-innovation/about-nrc-irap

[2] 88 - Sustainable Development Technology Fund
    SDTC | Federal
    Amount: $1,000,000 – $5,000,000 | Deadline: 2026-09-30
    Summary: Supports late-stage cleantech companies developing net-zero solutions...
    https://www.sdtc.ca/en/apply/

[3] 78 - Green Transition — PME en action
    PME MTL | Municipal
    Amount: $25,000 – $100,000 | Deadline: 2026-06-15
    Summary: Montreal SMEs transitioning to low-carbon operations...
    https://pmemtl.com/programmes/...

...

Commands:
- "track 1,2,3" - Move IDs to pipeline
- "dismiss 6,7" - Not a fit
- "dismiss <60" - Dismiss all below score 60
- "preview 2" - Open URL in Chrome
- "done" - Finish review
```

### 3. Process User Commands

**Track command:**
```bash
uv run granthunt track <id>
```

**Dismiss command:**
```bash
uv run granthunt dismiss <id>
```

**Preview command:**
Use Chrome tools to navigate to the grant URL for detailed view.

**Bulk operations:**
For "track all" or "dismiss <score", loop through matching prospects and run the appropriate command for each.

### 4. Summary

After processing, show summary:
```
Review complete:
- 3 grants tracked (moved to pipeline)
- 2 prospects dismissed
- 3 prospects remaining

Run /grant-list to see your updated pipeline.
```

## Display Format

For each prospect, show:
- **[ID] Score** - Title
- Organization | Jurisdiction (Federal / Provincial / Municipal)
- **Amount:** range (if known, else "-") | **Deadline:** (if known, else "rolling" or "-")
- **Summary:** First 120 chars (if available)
- URL

This gives enough context to decide without opening each link.
