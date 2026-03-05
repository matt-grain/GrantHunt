# Job Application Assistant

Comprehensive job application workflow - deep research, personalized cover letter, and artifact management.

## Usage

```
/job-apply <job_id>
```

## Instructions

### 1. Get job details

```bash
uv run jobhunt show <job_id>
```

Extract: title, company, location, URL, notes for context.

### 2. Create application folder

Create folder structure:
```
applications/<id>-<company_slug>-<YYYY-MM-DD>/
```

Example: `applications/4-cae-2026-03-05/`

```bash
mkdir -p "applications/<id>-<slug>-<date>"
```

### 3. Deep Company Research (Agent)

**Spawn the `company-researcher` agent** to gather interview-ready intelligence:

```
Use Agent tool with:
- subagent_type: "company-researcher"
- prompt: "Research [COMPANY NAME] for a job interview.
  Role: [JOB TITLE]
  Location: [LOCATION]

  I need comprehensive intel to answer 'Why are you interested in [COMPANY]?'

  Save the research to: applications/<folder>/research.md"
```

The agent will:
- Fetch company website (About, Careers, News)
- Check LinkedIn and recent press
- Find AI/tech initiatives
- Compile "Why [Company]?" talking points
- Generate smart interview questions

Wait for agent to complete, then verify `research.md` was saved.

### 4. Generate Cover Letter

Now generate a cover letter using BOTH the research AND the resume:

```bash
uv run jobhunt cover-letter <job_id> --output "applications/<folder>/cover_letter_draft.md"
```

**Then enhance the cover letter** by reading:
- The generated draft
- The research.md (for "Why [Company]?" section)
- The resume at `profile/resume_matthieu_boujonnier.md`

Create an improved `cover_letter.md` that:
- Fills in the "Why [Company]?" section with specific hooks from research
- Connects experience to the specific role requirements
- Uses concrete company facts (not generic praise)

### 5. Create checklist

Write `applications/<folder>/checklist.md`:

```markdown
# Application: <Title> at <Company>

**Job URL:** <url>
**Applied:** [ ] Yes / Date: ___
**Status:** NEW

## Pre-Application
- [x] Deep company research completed
- [x] Cover letter generated
- [ ] Tailor resume if needed
- [ ] Review and personalize cover letter
- [ ] Proofread everything

## Application
- [ ] Submit application
- [ ] Save confirmation/screenshot
- [ ] Update tracker: `jobhunt update <id> --status APPLIED`

## Follow-up
- [ ] Send LinkedIn connection to hiring manager
- [ ] Set 2-week follow-up reminder
- [ ] Review interview questions from research.md

## Key Talking Points
[Extract 3 "Why [Company]?" hooks from research.md]

## Interview Questions to Ask
[Extract top 3 questions from research.md]
```

### 6. Write Killer Cover Letter

**After research is complete, write the cover letter yourself** using:
- The full `research.md` content
- The resume at `profile/resume_matthieu_boujonnier.md`
- The job details

Create a compelling, personalized cover letter that:
- Opens with a specific company fact that shows research (not generic)
- Has 3 specific "Why [Company]?" hooks tied to their strategy/products/news
- References specific company initiatives, contracts, or products by name
- Connects Matt's experience directly to their challenges
- Ends with a P.S. containing a specific research-based question

Save to `applications/<folder>/cover_letter.md`

**This is NOT template filling** — write it as a human would, synthesizing all the research.

### 7. Report to user

Show:
- Folder created: `applications/<folder>/`
- Files saved:
  - `research.md` (with key highlights)
  - `cover_letter.md` (AI-written, research-powered)
  - `checklist.md`
- Top 3 "Why [Company]?" hooks
- Next steps

### 8. After applying

```bash
uv run jobhunt update <job_id> --status APPLIED --notes "Applied via LinkedIn"
```

## Folder Structure

```
applications/
├── 4-cae-2026-03-05/
│   ├── research.md         # Deep company intel from agent
│   ├── cover_letter.md     # Personalized, research-informed
│   ├── checklist.md        # Application checklist
│   └── (resume_tailored.pdf)  # optional, added by user
├── 5-stripe-2026-03-06/
│   └── ...
```

## Quality Bar

The cover letter "Why [Company]?" section must contain:
- At least 2 specific company facts (not generic)
- Connection to role requirements
- Reference to recent news/initiatives if available

If the agent research is thin, flag it and suggest manual research before applying.
