# GrantHunt Refactoring Plan

## Overview

Transform the **jobhunt** job search tracker into **granthunt**, a grant discovery and application tracking tool for climate tech startups. The user is the founder of [Flotexa](https://flotexa.ca/), a Quebec-based climate tech startup.

**Same screens, different domain.** The UI flow (dashboard, kanban, prospects, stats) stays identical. The domain model, terminology, profile, sources, and skills change.

## Design Decisions

- **Pipeline:** DISCOVERED -> EVALUATING -> PREPARING -> SUBMITTED -> UNDER_REVIEW -> APPROVED / REJECTED / WITHDRAWN
- **CLI name:** `granthunt`
- **Package:** `granthunt` (under `src/granthunt/`)
- **Apply skill:** Generates Letter of Intent + Executive Summary + eligibility checklist
- **Sources:** Federal + Quebec + Climate-specific + Academic/Collab

---

## Phase 1: Package Rename (mechanical)

Rename the Python package from `jobhunt` to `granthunt`. Pure find-and-replace, no logic changes.

### Task 1.1: Rename src directory
**Files:** `src/jobhunt/` -> `src/granthunt/`
**Action:** `mv src/jobhunt src/granthunt`

### Task 1.2: Update pyproject.toml
**File:** `pyproject.toml`
**Changes:**
- `name = "granthunt"`
- `description = "Grant discovery and application tracking for startups"`
- `[project.scripts]` -> `granthunt = "granthunt.cli:app"`
- `[tool.hatch.build.targets.wheel]` -> `packages = ["src/granthunt"]`

### Task 1.3: Update all Python imports
**Files:** All `.py` files under `src/granthunt/`
**Action:** Replace all `from jobhunt.` with `from granthunt.` and `import jobhunt.` with `import granthunt.`
- `src/granthunt/cli.py` (many imports)
- `src/granthunt/matcher.py`
- `src/granthunt/cover_letter.py`
- `src/granthunt/web/app.py`
- `src/granthunt/web/dependencies.py`
- `src/granthunt/web/routers/*.py`

### Task 1.4: Update web app title
**File:** `src/granthunt/web/app.py`
**Change:** `FastAPI(title="GrantHunt")`

### Task 1.5: Update CLI help text
**File:** `src/granthunt/cli.py`
**Change:** `app = typer.Typer(help="Grant search and application tracking CLI")`

### Task 1.6: Verify with uv
**Command:** `cd C:/Projects/GrantHunt && uv sync && uv run granthunt --help`

---

## Phase 2: Domain Model Refactoring

Replace job-specific domain concepts with grant concepts.

### Task 2.1: Rewrite models.py — enums and core models
**File:** `src/granthunt/models.py`
**Changes:**

Replace `JobStatus` with `GrantStatus`:
```python
class GrantStatus(StrEnum):
    DISCOVERED = "DISCOVERED"
    EVALUATING = "EVALUATING"
    PREPARING = "PREPARING"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
```

Replace `Job` with `Grant`:
```python
class Grant(BaseModel):
    id: int
    url: str
    title: str                          # Grant program name
    organization: str                   # Funding body (was: company)
    program: str | None = None          # NEW: specific program name
    location: str | None = None         # Eligibility region
    status: GrantStatus = GrantStatus.DISCOVERED
    score: float | None = None
    notes: str | None = None
    deadline: datetime | None = None    # NEW: application deadline
    amount_min: float | None = None     # NEW: min funding amount
    amount_max: float | None = None     # NEW: max funding amount
    grant_type: str | None = None       # NEW: R&D, innovation, tax credit, etc.
    date_added: datetime
    date_updated: datetime
    raw_description: str | None = None
```

Replace `JobCreate`/`JobUpdate` with `GrantCreate`/`GrantUpdate`:
```python
class GrantCreate(BaseModel):
    url: str
    title: str
    organization: str
    program: str | None = None
    location: str | None = None
    notes: str | None = None
    deadline: datetime | None = None
    amount_min: float | None = None
    amount_max: float | None = None
    grant_type: str | None = None

class GrantUpdate(BaseModel):
    status: GrantStatus | None = None
    score: float | None = None
    notes: str | None = None
    deadline: datetime | None = None
```

Replace `JobProspect` with `GrantProspect`:
```python
class GrantProspect(BaseModel):
    id: int
    url: str
    title: str
    organization: str
    program: str | None = None
    location: str | None = None
    summary: str | None = None
    amount_range: str | None = None     # Was: salary
    quick_score: float | None = None
    source: str = "innovation_canada"
    external_id: str | None = None
    status: ProspectStatus = ProspectStatus.PENDING
    grant_id: int | None = None         # Was: job_id
    deadline: str | None = None         # NEW
    discovered_at: datetime
```

Replace `ProspectCreate`/`ProspectUpdate` similarly.
Keep `ScrapeHistory` as-is (it's source-agnostic).

### Task 2.2: Rewrite db.py — schema and CRUD
**File:** `src/granthunt/db.py`
**Changes:**
- Rename table `jobs` -> `grants`
- Rename table `job_prospects` -> `grant_prospects`
- Add new columns: `deadline TEXT`, `amount_min REAL`, `amount_max REAL`, `grant_type TEXT`, `program TEXT`
- Replace `amount_range` for `salary` in prospects
- Add `deadline TEXT` column to prospects
- Rename `job_id` -> `grant_id` in prospects FK
- Rename all functions: `add_job` -> `add_grant`, `get_job` -> `get_grant`, `list_jobs` -> `list_grants`, etc.
- Rename `_row_to_job` -> `_row_to_grant`, `_row_to_prospect` stays
- Update `track_prospect` to create a Grant instead of a Job
- DB file: `grants.db` instead of `jobs.db`

### Task 2.3: Rewrite config.py — grant profile model
**File:** `src/granthunt/config.py`
**Changes:**

Replace `JobProfile` with `GrantProfile`:
```python
class StartupInfo(BaseModel):
    name: str
    description: str
    industry: str
    stage: str                  # seed, pre-seed, series-a, growth
    location: str
    founded_year: int | None = None
    employees: int | None = None
    website: str | None = None

class EligibilityCriteria(BaseModel):
    sectors: list[str]          # climate tech, clean energy, etc.
    activities: list[str]       # R&D, commercialization, export, etc.
    certifications: list[str]   # ISO, B-Corp, etc.

class FundingPrefs(BaseModel):
    min_amount: float | None = None
    max_amount: float | None = None
    types: list[str]            # grant, tax_credit, loan, equity

class GrantProfile(BaseModel):
    startup: StartupInfo
    eligibility: EligibilityCriteria
    funding_prefs: FundingPrefs
    keywords_boost: list[str]
    keywords_avoid: list[str]
```

Rename `load_profile` -> loads `grant_profile.yaml` instead of `job_profile.yaml`.

### Task 2.4: Create grant_profile.yaml
**File:** `grant_profile.yaml` (replaces `job_profile.yaml`)
**Content:** Pre-filled for Flotexa (climate tech startup in Quebec):
```yaml
startup:
  name: "Flotexa"
  description: "Climate tech startup developing innovative solutions for environmental challenges"
  industry: "Climate Tech"
  stage: "seed"
  location: "Quebec, Canada"
  website: "https://flotexa.ca/"

eligibility:
  sectors:
    - "clean technology"
    - "climate tech"
    - "environmental technology"
    - "sustainable development"
    - "green energy"
    - "circular economy"
  activities:
    - "R&D"
    - "innovation"
    - "commercialization"
    - "prototyping"
    - "pilot project"
    - "scale-up"
  certifications: []

funding_prefs:
  min_amount: 10000
  max_amount: 5000000
  types:
    - "grant"
    - "tax_credit"
    - "non-repayable"
    - "loan"

keywords_boost:
  - "clean tech"
  - "climate"
  - "environment"
  - "innovation"
  - "SME"
  - "startup"
  - "Quebec"
  - "prototype"

keywords_avoid:
  - "large enterprise only"
  - "publicly traded"
  - "minimum 250 employees"
```

Delete `job_profile.yaml`.

### Task 2.5: Create grant_sources.yaml
**File:** `grant_sources.yaml` (replaces `job_sources.yaml`)
**Content:**
```yaml
sources:
  # --- Federal ---
  innovation_canada:
    name: "Innovation Canada"
    enabled: true
    priority: 1
    url: "https://innovation.ised-isde.canada.ca/innovation/s/?language=en"
    category: "federal"
    notes: "Aggregator of federal grants. Use search filters for clean tech."

  irap:
    name: "NRC-IRAP"
    enabled: true
    priority: 1
    url: "https://nrc.canada.ca/en/support-technology-innovation"
    category: "federal"
    notes: "Non-repayable up to $10M for innovative SMEs. Advisory + funding."

  sdtc:
    name: "SDTC (Sustainable Development Technology Canada)"
    enabled: true
    priority: 2
    url: "https://www.sdtc.ca/"
    category: "federal"
    notes: "Dedicated to clean tech. Up to $10M per project. Now under NRC."

  sred:
    name: "SR&ED Tax Credit"
    enabled: true
    priority: 2
    url: "https://www.canada.ca/en/revenue-agency/services/scientific-research-experimental-development-tax-incentive-program.html"
    category: "federal"
    notes: "Tax credits for R&D. 35% refundable for CCPCs. Apply after fiscal year."

  # --- Quebec ---
  mei:
    name: "MEI (Ministere de l'Economie)"
    enabled: true
    priority: 1
    url: "https://www.economie.gouv.qc.ca/en/objective/financing"
    category: "quebec"
    notes: "Quebec economic development programs. Multiple streams."

  investissement_quebec:
    name: "Investissement Quebec"
    enabled: true
    priority: 2
    url: "https://www.investquebec.com/quebec/en/financial-products.html"
    category: "quebec"
    notes: "Loans, guarantees, equity. Green economy focus."

  pme_mtl:
    name: "PME MTL"
    enabled: true
    priority: 3
    url: "https://pmemtl.com/en"
    category: "quebec"
    notes: "Montreal-specific. Technical assistance + financing for SMEs."

  cycle_capital:
    name: "Cycle Capital"
    enabled: false
    priority: 4
    url: "https://cyclecapital.com/"
    category: "quebec"
    notes: "VC fund focused on clean tech. Not a grant but relevant for funding pipeline."

  # --- Climate-specific ---
  erf:
    name: "Emissions Reduction Fund"
    enabled: true
    priority: 2
    url: "https://natural-resources.canada.ca/climate-change/emissions-reduction-fund"
    category: "climate"
    notes: "NRCan fund for emission reduction technologies."

  clean_growth_hub:
    name: "Clean Growth Hub"
    enabled: true
    priority: 1
    url: "https://www.cleangrowthHub.gc.ca/"
    category: "climate"
    notes: "Federal clean tech concierge. Helps navigate programs."

  ecoaction:
    name: "EcoAction Community Funding"
    enabled: true
    priority: 3
    url: "https://www.canada.ca/en/environment-climate-change/services/environmental-funding/ecoaction-community-program.html"
    category: "climate"
    notes: "Community-level environmental projects. Smaller amounts."

  fcm_gmf:
    name: "FCM Green Municipal Fund"
    enabled: false
    priority: 4
    url: "https://greenmunicipalfund.ca/"
    category: "climate"
    notes: "Municipal focus. Enable if working with cities."

  # --- Academic / Collaborative ---
  mitacs:
    name: "Mitacs"
    enabled: true
    priority: 2
    url: "https://www.mitacs.ca/our-programs/"
    category: "academic"
    notes: "Industry-academic partnerships. Accelerate/Elevate programs."

  crsng:
    name: "NSERC/CRSNG Alliance"
    enabled: true
    priority: 3
    url: "https://www.nserc-crsng.gc.ca/professors-professeurs/rpp-pp/alliance-alliance_eng.asp"
    category: "academic"
    notes: "Alliance grants for industry-academic research collaboration."

defaults:
  region: "Quebec, Canada"
  eligible_regions:
    - "Quebec"
    - "Canada"
    - "National"

deduplication:
  match_fields:
    - organization
    - title
  fuzzy_threshold: 0.85
```

Delete `job_sources.yaml`.

---

## Phase 3: Matcher & Scraper Refactoring

Adapt the scoring engine and scraper for grants.

### Task 3.1: Rewrite matcher.py for grant scoring
**File:** `src/granthunt/matcher.py`
**Changes:**
- Rename `score_job` -> `score_grant`
- Replace `JobPostingData` references with `GrantPostingData`
- Replace `JobProfile` references with `GrantProfile`
- **Scoring weights for grants:**
  - Sector match (30%): Does the grant target climate tech / clean tech?
  - Eligibility match (25%): SME, Quebec, stage-appropriate?
  - Funding fit (20%): Amount range matches? Type matches (grant vs loan)?
  - Keywords (15%): Boost/avoid keywords from profile
  - Red flags (10%): "large enterprise only", "publicly traded", etc.
- Replace `role_score` with `sector_score`
- Replace `keyword_score` logic to use `eligibility.sectors` and `eligibility.activities`
- Replace `industry_score` with `funding_fit_score`
- Keep `red_flag_score` pattern but change anti-patterns to grant-specific ones
- Replace ROLE_VARIATIONS with SECTOR_VARIATIONS (clean tech synonyms)

### Task 3.2: Rewrite scraper.py for grant pages
**File:** `src/granthunt/scraper.py`
**Changes:**
- Rename `JobPostingData` -> `GrantPostingData`
- Fields: `title`, `organization`, `program`, `description`, `eligibility_text`, `amount_range`, `deadline`, `source_url`
- Remove LinkedIn/Indeed-specific extractors
- Add `extract_from_generic` that looks for:
  - Funding amounts (patterns: "$X to $Y", "up to $X million", etc.)
  - Deadlines (patterns: "deadline:", "applications due:", dates)
  - Eligibility criteria sections
- Keep `fetch_grant_posting` (was `fetch_job_posting`) for generic HTML scraping
- Remove `detect_remote` (not relevant), add `extract_deadline`, `extract_funding_amount`

### Task 3.3: Rewrite research.py -> org_research.py
**File:** `src/granthunt/research.py` (rename conceptually, keep filename)
**Changes:**
- `CompanyResearch` -> `OrganizationResearch`
- Remove `tech_stack` extraction (not relevant for funding orgs)
- Add `programs` field: list of known grant programs
- Add `success_stories` field: past funded projects
- Replace `extract_culture_signals` with `extract_funding_signals`:
  - "climate", "clean tech", "SME", "innovation", "Quebec"
- Replace `generate_interview_questions` with `generate_application_tips`:
  - Tips specific to the funding body (e.g., "IRAP values innovation + market potential")
- Keep cache mechanism

### Task 3.4: Rewrite cover_letter.py -> application.py
**File:** `src/granthunt/cover_letter.py` -> rename to `src/granthunt/application.py`
**Changes:**
- Replace cover letter generation with LOI + Executive Summary generator
- `generate_cover_letter` -> `generate_loi` (Letter of Intent)
- New function: `generate_executive_summary`
- New function: `generate_eligibility_checklist`
- Remove resume loading (not relevant for grants)
- Add startup profile loading for the narrative
- Template structure for LOI:
  - Project title
  - Applicant (Flotexa info from profile)
  - Project description
  - Alignment with grant objectives
  - Expected outcomes / impact
  - Budget summary
  - Timeline

---

## Phase 4: CLI Refactoring

Update all CLI commands to use grant terminology.

### Task 4.1: Rewrite cli.py — commands and terminology
**File:** `src/granthunt/cli.py`
**Changes:**
- `app = typer.Typer(help="Grant search and application tracking CLI")`
- Rename all status colors for `GrantStatus`:
  ```python
  STATUS_COLORS = {
      GrantStatus.DISCOVERED: "blue",
      GrantStatus.EVALUATING: "cyan",
      GrantStatus.PREPARING: "yellow",
      GrantStatus.SUBMITTED: "magenta",
      GrantStatus.UNDER_REVIEW: "green",
      GrantStatus.APPROVED: "bright_green",
      GrantStatus.REJECTED: "red",
      GrantStatus.WITHDRAWN: "dim",
  }
  ```
- Rename commands:
  - `add` -> adds a grant (--title, --organization instead of --company, --deadline, --amount-min, --amount-max, --grant-type)
  - `list` -> lists grants with deadline column instead of score
  - `show` -> shows grant detail with deadline, amount, type
  - `update` -> updates grant (status, notes, score, deadline)
  - `match` -> analyzes a grant URL against profile
  - `research` -> researches a funding organization
  - `cover-letter` -> `apply` (generates LOI + summary)
  - `prospects` -> same but with amount_range instead of salary
  - `track` / `dismiss` / `review` -> same logic, grant terminology
  - `serve` -> `serve` (starts GrantHunt dashboard)
- Update all user-facing strings: "job" -> "grant", "company" -> "organization"
- Table headers: add "Deadline" column, rename "Company" to "Organization"

---

## Phase 5: Web Dashboard Refactoring

Update templates and routers for grant domain.

### Task 5.1: Rewrite web routers — grant terminology
**Files:** All files under `src/granthunt/web/routers/`
**Changes per file:**

`dashboard.py`:
- Import `list_grants` instead of `list_jobs`
- Import `GrantStatus` instead of `JobStatus`
- Context: `grants` instead of `jobs`

`jobs.py` -> rename to `grants.py`:
- All routes: `/grants/add`, `/grants/{id}`, `/grants/{id}/status`
- Import/use Grant models instead of Job models
- Form fields: organization, deadline, amount_min, amount_max, grant_type

`prospects.py`:
- Update display: "amount_range" instead of "salary"
- "grant_id" instead of "job_id"

`stats.py`:
- Grant-specific stats: by grant_type, by organization, by status
- Deadline-based stats: upcoming deadlines

`app.py`:
- Include `grants` router instead of `jobs` router
- `prefix="/grants"` instead of `prefix="/jobs"`

`dependencies.py`:
- No changes needed (DB connection is generic)

### Task 5.2: Rewrite base.html template
**File:** `src/granthunt/web/templates/base.html`
**Changes:**
- Title: "GrantHunt" instead of "JobHunt"
- Nav links: same structure, grant labels
- Branding: green/teal theme (climate tech feel) instead of current palette

### Task 5.3: Rewrite dashboard.html and kanban.html
**Files:** `dashboard.html`, `kanban.html`
**Changes:**
- Status columns use GrantStatus values (DISCOVERED, EVALUATING, PREPARING, SUBMITTED, UNDER_REVIEW, APPROVED)
- Card content: organization instead of company, deadline badge, amount range
- "Add Grant" instead of "Add Job"

### Task 5.4: Rewrite job_detail.html -> grant_detail.html
**File:** Rename `job_detail.html` -> `grant_detail.html`
**Changes:**
- Show deadline prominently (with countdown if approaching)
- Show funding amount range
- Show grant type badge
- "Organization" instead of "Company"
- Status dropdown uses GrantStatus values

### Task 5.5: Rewrite add_job.html -> add_grant.html
**File:** Rename `add_job.html` -> `add_grant.html`
**Changes:**
- Form fields: URL, title, organization, program, deadline, amount_min, amount_max, grant_type (dropdown), location, notes

### Task 5.6: Rewrite prospects.html and prospect_row.html
**Files:** `prospects.html`, `partials/prospect_row.html`
**Changes:**
- "Amount" instead of "Salary"
- "Organization" instead of "Company"
- Add deadline column
- "Track Grant" instead of "Track Job"

### Task 5.7: Rewrite stats.html and stats_cards.html
**Files:** `stats.html`, `partials/stats_cards.html`
**Changes:**
- Grant pipeline stats by GrantStatus
- Upcoming deadlines widget
- Funding amounts summary (total applied for, total approved)
- By source category breakdown (Federal, Quebec, Climate, Academic)

### Task 5.8: Rewrite cover_letter.html -> application.html
**File:** Rename `cover_letter.html` -> `application.html`
**Changes:**
- Display LOI and Executive Summary
- Eligibility checklist display

### Task 5.9: Rename partials
**Files:**
- `partials/job_card.html` -> `partials/grant_card.html`
- `partials/job_list.html` -> `partials/grant_list.html`
- Update all template references (extends, includes)

---

## Phase 6: Skills Refactoring

Update Claude Code skills from job- to grant-focused.

### Task 6.1: Rename and rewrite grant-add skill
**Dir:** `.claude/skills/job-add/` -> `.claude/skills/grant-add/`
**Content:** Same pattern, `uv run granthunt add` with grant-specific flags (--organization, --deadline, --amount-min, --amount-max, --grant-type)

### Task 6.2: Rename and rewrite grant-list skill
**Dir:** `.claude/skills/job-list/` -> `.claude/skills/grant-list/`
**Content:** Grant statuses: DISCOVERED, EVALUATING, PREPARING, SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED, WITHDRAWN

### Task 6.3: Rename and rewrite grant-match skill
**Dir:** `.claude/skills/job-match/` -> `.claude/skills/grant-match/`
**Content:** Score grant against startup profile. Sector match, eligibility, funding fit.

### Task 6.4: Rename and rewrite grant-find skill
**Dir:** `.claude/skills/job-find/` -> `.claude/skills/grant-find/`
**Content:** Browse grant sources via Chrome. Extract grant programs, deadlines, amounts. Save to prospects.
- Use grant_sources.yaml for configured sources
- Extraction patterns for government sites (different from job boards)
- Focus on Innovation Canada aggregator as primary source

### Task 6.5: Rename and rewrite grant-review skill
**Dir:** `.claude/skills/job-review/` -> `.claude/skills/grant-review/`
**Content:** Review pending grant prospects. Show deadline urgency, amount, eligibility match.

### Task 6.6: Rename and rewrite grant-apply skill
**Dir:** `.claude/skills/job-apply/` -> `.claude/skills/grant-apply/`
**Content:** Full grant application workflow:
1. Get grant details
2. Create application folder: `applications/{id}-{org_slug}-{date}/`
3. Research funding organization (spawn agent)
4. Generate LOI (Letter of Intent)
5. Generate Executive Summary
6. Generate eligibility checklist
7. Create application checklist with deadline countdown

### Task 6.7: Rename company-researcher agent -> org-researcher
**File:** `.claude/agents/company-researcher.md`
**Changes:** Adapt to research funding organizations instead of companies. Focus on: programs offered, eligibility criteria, past funded projects, application tips, success rates.

---

## Phase 7: Documentation & Finalization

### Task 7.1: Rewrite ARCHITECTURE.md
**File:** `ARCHITECTURE.md`
**Content:** Full architecture doc for GrantHunt with grant domain concepts, data flow, state machines, routes.

### Task 7.2: Rewrite README.md
**File:** `README.md`
**Content:** Project overview, setup instructions, usage guide for grant tracking.

### Task 7.3: Create .gitignore
**File:** `.gitignore`
**Content:** Standard Python + `grants.db`, `.venv/`, `__pycache__/`, `.granthunt_cache/`, `applications/`

### Task 7.4: Final uv sync and smoke test
**Commands:**
```bash
cd C:/Projects/GrantHunt
uv sync
uv run granthunt --help
uv run granthunt serve
```

---

## Execution Order & Dependencies

```
Phase 1 (package rename)     <- do first, everything depends on this
  |
Phase 2 (domain models)      <- models.py, db.py, config.py, yaml files
  |
Phase 3 (matcher/scraper)    <- depends on new models from Phase 2
  |
Phase 4 (CLI)                <- depends on Phase 2 + 3
  |
Phase 5 (web dashboard)      <- depends on Phase 2 + 4 (routers import from models/db)
  |
Phase 6 (skills)             <- depends on Phase 4 (skills call CLI commands)
  |
Phase 7 (docs)               <- last, reflects final state
```

## Task Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| 1 | 6 tasks | Package rename (mechanical) |
| 2 | 5 tasks | Domain model refactoring |
| 3 | 4 tasks | Matcher, scraper, research, application |
| 4 | 1 task | CLI rewrite |
| 5 | 9 tasks | Web dashboard templates + routers |
| 6 | 7 tasks | Claude Code skills |
| 7 | 4 tasks | Documentation |
| **Total** | **36 tasks** | |

Each task is scoped for a Sonnet agent: single file or small group of related files, clear inputs/outputs, no ambiguity.
