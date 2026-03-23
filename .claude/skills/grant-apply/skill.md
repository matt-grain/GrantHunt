# Grant Application Assistant

Comprehensive grant application workflow — funder research, LOI drafting, eligibility checklist, and application package management.

## Usage

```
/grant-apply <grant_id>
```

## Instructions

### 1. Get grant details

```bash
uv run granthunt show <grant_id>
```

Extract: title, organization, amount range, deadline, grant type, URL, notes.

### 2. Create application folder

```
applications/{id}-{org_slug}-{YYYY-MM-DD}/
```

Example: `applications/4-nrc-irap-2026-03-23/`

```bash
mkdir -p "applications/<id>-<org_slug>-<date>"
```

### 3. Research the funding organization (Agent)

**Spawn the `org-researcher` agent** to gather application-ready intelligence:

```
Use Agent tool with:
- subagent_type: "org-researcher"
- prompt: "Research [ORGANIZATION NAME] as a grant funder for a climate tech startup.
  Grant: [GRANT TITLE]
  URL: [GRANT URL]

  I need intelligence to write a compelling application answering
  'Why is this startup the right fit for this grant?'

  Save the research to: applications/<folder>/research.md"
```

The agent will:
- Fetch funder's website (About, Programs, Eligibility, News)
- Find past funded projects and success factors
- Extract eligibility criteria and application tips
- Compile "Why this grant?" talking points
- Note any red flags or disqualifying conditions

Wait for the agent to complete, then verify `research.md` was saved.

### 4. Read the startup profile

```
profile/flotexa.md
```

Extract key facts: mission, technology, stage, team, traction, and differentiation. These ground the application in concrete startup context.

### 5. Generate LOI draft

```bash
uv run granthunt apply <grant_id> --output "applications/<folder>/loi_draft.md"
```

### 6. Write the enhanced LOI

**After research and profile are loaded, write the LOI yourself** using:
- The generated `loi_draft.md` as structural scaffolding
- The full `research.md` (funder priorities, past funded projects, evaluation criteria)
- The startup profile at `profile/flotexa.md`
- The grant details

Create a compelling, personalized Letter of Intent that:
- Opens with a specific hook tied to the funder's stated mission or recent initiative
- States clearly how the startup's technology addresses the grant's target outcomes
- References specific eligibility criteria from the program and confirms each is met
- Uses concrete metrics and milestones (not generic ambition)
- Closes with a clear ask: amount requested, proposed use of funds, timeline

Save to `applications/<folder>/loi.md`

**This is NOT template filling** — write it as the founder would, synthesizing all the research.

### 7. Generate eligibility checklist

Write `applications/<folder>/eligibility.md` with:
- Every stated eligibility requirement from the program
- Status for each: [x] Met | [ ] Unconfirmed | [!] Risk
- Evidence or source for each confirmed item
- Action items for any unconfirmed criteria

### 8. Create application checklist

Write `applications/<folder>/checklist.md`:

```markdown
# Grant Application: <Title> — <Organization>

**Grant URL:** <url>
**Amount Requested:** $<amount>
**Deadline:** <deadline> (<N days away>)
**Status:** PREPARING

## Pre-Submission
- [x] Funder research completed (research.md)
- [x] Eligibility verified (eligibility.md)
- [x] LOI drafted (loi.md)
- [ ] Internal review of LOI
- [ ] Financial projections prepared
- [ ] Supporting documents gathered (letters of support, IP summary, etc.)

## Submission
- [ ] Submit application via funder portal
- [ ] Save confirmation / submission ID
- [ ] Update tracker: `granthunt update <id> --status SUBMITTED`

## Follow-up
- [ ] Note funder's review timeline
- [ ] Set calendar reminder for follow-up if no response after <N weeks>
- [ ] Prepare for due diligence questions

## Key Talking Points
[Extract 3 "Why us for this grant?" hooks from research.md]

## Watch-outs
[Extract red flags or risk items from eligibility.md]
```

### 9. Report to user

Show:
- Folder created: `applications/<folder>/`
- Files saved:
  - `research.md` (funder intelligence)
  - `loi.md` (AI-written, research-powered)
  - `eligibility.md` (criteria checklist)
  - `checklist.md` (application checklist with deadline countdown)
- Top 3 "Why us?" hooks
- Any red flags or eligibility risks
- Next steps

### 10. After submitting

```bash
uv run granthunt update <grant_id> --status SUBMITTED --notes "Submitted via portal on <date>"
```

## Folder Structure

```
applications/
├── 4-nrc-irap-2026-03-23/
│   ├── research.md         # Funder intelligence from org-researcher agent
│   ├── loi.md              # Personalized, research-informed LOI
│   ├── eligibility.md      # Eligibility criteria checklist
│   └── checklist.md        # Full application checklist
├── 5-sdtc-2026-04-01/
│   └── ...
```

## Quality Bar

The LOI must contain:
- At least 2 specific references to the funder's stated priorities or past-funded projects
- Explicit confirmation of all key eligibility criteria
- Concrete financial ask with proposed use of funds breakdown
- No generic language — every paragraph must be specific to this grant and this startup

If funder research is thin (private/limited info), flag it and request manual research before drafting the LOI.
