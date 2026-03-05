# Job Review - Review Pending Prospects

Review discovered job prospects and decide which to track or dismiss.

## Usage

```
/job-review
```

## Instructions

### 1. List Pending Prospects

Run the CLI command to show pending prospects:

```bash
uv run jobhunt prospects --pending
```

If no prospects pending, inform the user:
```
No pending prospects to review.
Run /job-find to discover new opportunities.
```

### 2. Present Options

Display prospects in a table format sorted by score:

```
Pending Prospects (9 to review)

ID  Score  Title                              Company         Location
──────────────────────────────────────────────────────────────────────
2   88     Chef des solutions intégrées       CAE             Montreal
3   85     Technical Cloud & AI Strategy      MTY Food Group  Montreal (H)
4   85     VP Ingénierie et technologie       Hypertec Group  Montreal (H)
...

Commands:
- "track 2,3,4" - Move IDs 2,3,4 to your pipeline
- "dismiss 9,10" - Dismiss IDs 9,10
- "track all" - Track all pending
- "dismiss <60" - Dismiss all with score < 60
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

## Interactive Mode

Alternatively, run the interactive review:
```bash
uv run jobhunt review
```

This walks through each prospect one by one with t/d/s/q commands.
