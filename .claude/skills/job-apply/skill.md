# Job Application Assistant

Help with job application workflow - research, cover letter, and artifact management.

## Usage

```
/job-apply <job_id>
```

## Instructions

### 1. Get job details

```bash
uv run jobhunt show <job_id>
```

Extract: title, company, date for folder naming.

### 2. Create application folder

Create folder structure:
```
applications/<id>-<company_slug>-<YYYY-MM-DD>/
```

Example: `applications/4-cae-2026-03-05/`

```bash
mkdir -p "applications/<id>-<slug>-<date>"
```

### 3. Research the company

```bash
uv run jobhunt research <job_id>
```

Save output to `applications/<folder>/research.md`

### 4. Generate cover letter

```bash
uv run jobhunt cover-letter <job_id> --output "applications/<folder>/cover_letter.md"
```

### 5. Create checklist

Write `applications/<folder>/checklist.md`:

```markdown
# Application: <Title> at <Company>

**Job URL:** <url>
**Applied:** [ ] Yes / Date: ___
**Status:** NEW

## Pre-Application
- [ ] Review job posting
- [ ] Company research saved
- [ ] Tailor resume if needed
- [ ] Personalize cover letter
- [ ] Proofread everything

## Application
- [ ] Submit application
- [ ] Save confirmation/screenshot
- [ ] Update tracker: `jobhunt update <id> --status APPLIED`

## Follow-up
- [ ] Send LinkedIn connection request
- [ ] Set 2-week follow-up reminder
- [ ] Prepare interview questions
```

### 6. Report to user

Show:
- Folder created: `applications/<folder>/`
- Files saved:
  - `research.md`
  - `cover_letter.md`
  - `checklist.md`
- Next steps

### 7. After applying

```bash
uv run jobhunt update <job_id> --status APPLIED --notes "Applied via LinkedIn"
```

## Folder Structure

```
applications/
├── 4-cae-2026-03-05/
│   ├── research.md
│   ├── cover_letter.md
│   ├── checklist.md
│   └── (resume_tailored.pdf)  # optional, added by user
├── 5-techcorp-2026-03-06/
│   └── ...
```
