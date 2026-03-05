# List Job Pipeline

Show your job search pipeline.

## Usage

```
/job-list [status]
```

## Instructions

1. Run the jobhunt CLI:
   ```bash
   uv run jobhunt list
   ```

   Or filter by status:
   ```bash
   uv run jobhunt list --status APPLIED
   ```

2. Display the results in a readable format.

## Statuses

- NEW: Just added, not yet reviewed
- INTERESTED: Worth pursuing
- APPLIED: Application submitted
- INTERVIEWING: In interview process
- OFFER: Received offer
- REJECTED: Rejected by company
- WITHDRAWN: Withdrew application
