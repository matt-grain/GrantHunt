# Add Job to Tracker

Add a job posting to your job search tracker.

## Usage

```
/job-add <url> [title] [company]
```

## Instructions

1. Run the jobhunt CLI to add the job:
   ```bash
   uv run jobhunt add "<url>" --title "<title>" --company "<company>"
   ```

2. If title/company not provided, ask the user for them.

3. Report the result to the user.

## Example

```
/job-add https://linkedin.com/jobs/view/123456 "CTO" "TechCorp"
```
