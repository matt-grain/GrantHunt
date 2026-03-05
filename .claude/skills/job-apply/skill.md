# Job Application Assistant

Help with job application workflow.

## Usage

```
/job-apply <job_id>
```

## Instructions

This skill helps you apply to a tracked job.

1. **Get job details:**
   ```bash
   uv run jobhunt show <job_id>
   ```

2. **Research the company:**
   ```bash
   uv run jobhunt research <job_id>
   ```

   Review the company research summary.

3. **Generate cover letter:**
   ```bash
   uv run jobhunt cover-letter <job_id>
   ```

   This outputs a draft cover letter. Review and refine as needed.

4. **Update status:**
   After applying:
   ```bash
   uv run jobhunt update <job_id> --status APPLIED --notes "Applied via LinkedIn"
   ```

## Workflow Checklist

- [ ] Review job posting and score (`jobhunt show <id>`)
- [ ] Research company (`jobhunt research <id>`)
- [ ] Tailor resume if needed
- [ ] Generate cover letter (`jobhunt cover-letter <id>`)
- [ ] Submit application
- [ ] Update tracker status (`jobhunt update <id> --status APPLIED`)
- [ ] Set follow-up reminder (2 weeks)

## Quick Apply

For fast applications:
```bash
# Match and add to tracker
uv run jobhunt match "<url>" --add

# Research and prep
uv run jobhunt research <id>
uv run jobhunt cover-letter <id> --output cover_letter.md

# After applying
uv run jobhunt update <id> --status APPLIED
```
