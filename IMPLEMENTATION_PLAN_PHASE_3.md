# Phase 3: Application Helpers

**Dependencies:** Phase 1 (db, models), Phase 2 (scraper, matcher)
**Agent:** python-cli

---

## Overview

Add application assistance features:
- Cover letter generation using LLM
- Company research automation
- `/job-apply` skill for application workflow

---

## Files to Create

### `src/jobhunt/cover_letter.py`

**Purpose:** Generate tailored cover letters
**Dependencies:** models, config, (Claude API or prompt for user)

**Functions:**
- `generate_cover_letter(job: Job, profile: JobProfile, resume_path: Path) -> str`: Generate cover letter
- `extract_key_requirements(job_description: str) -> list[str]`: Pull key requirements
- `match_experience(requirements: list[str], resume: str) -> dict`: Map requirements to experience
- `format_letter(content: str, format: str = "markdown") -> str`: Format output

**Cover letter structure:**
1. Opening: Why this role/company specifically
2. Body: 2-3 paragraphs mapping experience to requirements
3. Closing: Call to action, availability

**Constraints:**
- Load resume from `profile/resume_matthieu_boujonnier.md`
- Keep under 400 words
- Avoid generic phrases
- Highlight AI transformation story (user's key differentiator)
- Output as markdown (can convert to plain text)

**Note:** This module prepares the prompt. The actual generation happens via:
- Claude Code (user runs generation in conversation)
- Or future: direct API call

---

### `src/jobhunt/research.py`

**Purpose:** Automate company research
**Dependencies:** httpx, scraper

**Functions:**
- `research_company(company_name: str) -> CompanyResearch`: Aggregate company info
- `fetch_company_website(url: str) -> dict`: Scrape about/careers pages
- `fetch_linkedin_company(company_name: str) -> dict`: LinkedIn company page
- `summarize_research(data: dict) -> str`: Create research summary

**CompanyResearch model:**
```python
class CompanyResearch(BaseModel):
    name: str
    website: str | None
    industry: str | None
    size: str | None
    description: str | None
    tech_stack: list[str]
    recent_news: list[str]
    culture_signals: list[str]
    interview_prep: list[str]  # Suggested questions to ask
```

**Constraints:**
- Use public sources only
- Cache results to avoid repeated fetches
- Generate 3-5 interview questions based on research

---

### `.claude/skills/job-apply/skill.md`

**Purpose:** Application workflow assistant

```markdown
# Job Application Assistant

Help with job application workflow.

## Usage

\`\`\`
/job-apply <job_id>
\`\`\`

## Instructions

This skill helps you apply to a tracked job.

1. **Get job details:**
   \`\`\`bash
   uv run jobhunt show <job_id>
   \`\`\`

2. **Research the company:**
   \`\`\`bash
   uv run jobhunt research <job_id>
   \`\`\`

   Review the company research summary.

3. **Generate cover letter:**
   \`\`\`bash
   uv run jobhunt cover-letter <job_id>
   \`\`\`

   This outputs a draft cover letter. Review and refine as needed.

4. **Update status:**
   After applying:
   \`\`\`bash
   uv run jobhunt update <job_id> --status APPLIED --notes "Applied via LinkedIn"
   \`\`\`

## Workflow Checklist

- [ ] Review job posting and score
- [ ] Research company
- [ ] Tailor resume if needed
- [ ] Generate cover letter
- [ ] Submit application
- [ ] Update tracker status
- [ ] Set follow-up reminder (2 weeks)
```

---

## Files to Modify

### `src/jobhunt/cli.py` (MODIFY)

**Changes:** Add research and cover-letter commands

**New commands:**
- `jobhunt research <job_id>`: Show company research
- `jobhunt cover-letter <job_id> [--output FILE]`: Generate cover letter

**research command:**
1. Get job from database
2. Call `research_company(job.company)`
3. Display with rich panels:
   - Company overview
   - Tech stack
   - Culture signals
   - Suggested interview questions

**cover-letter command:**
1. Get job from database
2. Load job profile and resume
3. Generate cover letter prompt/output
4. Display or save to file

---

## Implementation Order

1. `src/jobhunt/research.py` - Company research module
2. `src/jobhunt/cover_letter.py` - Cover letter generator
3. `src/jobhunt/cli.py` - Add new commands
4. `.claude/skills/job-apply/skill.md` - Application workflow skill

---

## Verification

After implementation:
1. Add a test job: `uv run jobhunt add "https://example.com/job" --title "CTO" --company "TechCorp"`
2. Run `uv run jobhunt research 1`
3. Run `uv run jobhunt cover-letter 1`
4. Verify output quality and formatting

---

## Future Enhancements (not in this phase)

- Email integration for application tracking
- Calendar integration for interview scheduling
- Automated follow-up reminders
- LinkedIn Easy Apply automation
- Salary negotiation helper
