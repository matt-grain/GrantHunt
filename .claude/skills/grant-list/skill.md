# List Grant Pipeline

Show your active grant tracking pipeline.

## Usage

```
/grant-list [status]
```

## Instructions

1. Run the granthunt CLI:
   ```bash
   uv run granthunt list
   ```

   Or filter by status:
   ```bash
   uv run granthunt list --status EVALUATING
   ```

2. Display results in a readable table with title, organization, amount range, deadline, and status.

## Statuses

| Status | Meaning |
|--------|---------|
| DISCOVERED | Found, not yet evaluated |
| EVALUATING | Reviewing eligibility and fit |
| PREPARING | Application in progress |
| SUBMITTED | Application submitted, awaiting response |
| UNDER_REVIEW | Funder is reviewing the application |
| APPROVED | Grant awarded |
| REJECTED | Application declined |
| WITHDRAWN | Application withdrawn |
