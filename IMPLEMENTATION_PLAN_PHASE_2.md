# Phase 2: Matching & Scoring Engine

**Dependencies:** Phase 1 (models, config, db)
**Agent:** python-cli

---

## Overview

Add intelligent job matching:
- Scrape job postings from URLs
- Score jobs against profile using LLM
- Update CLI with match command
- Add `/job-match` skill

---

## Files to Create

### `src/jobhunt/scraper.py`

**Purpose:** Fetch and parse job postings from URLs
**Dependencies:** httpx, beautifulsoup4 (add to pyproject.toml)

**Models:**
```python
class JobPostingData(BaseModel):
    """Scraped job posting data."""
    title: str
    company: str
    location: str
    description: str
    requirements: list[str] = []  # Extracted bullet points
    salary: str | None = None
    remote: bool | None = None
    source_url: str
```

**Functions:**
- `fetch_job_posting(url: str) -> JobPostingData`: Fetch URL, extract job details
- `extract_from_linkedin(html: str, url: str) -> JobPostingData`: LinkedIn-specific parsing
- `extract_from_generic(html: str, url: str) -> JobPostingData`: Generic job board parsing
- `clean_description(text: str) -> str`: Strip HTML, normalize whitespace

**Constraints:**
- Handle common job boards: LinkedIn, Indeed, Greenhouse, Lever
- Graceful fallback for unknown formats
- Respect rate limits (add delay parameter)
- User-agent header to avoid blocks
- Timeout after 30 seconds
- Return typed `JobPostingData` model, never raw dict

---

### `src/jobhunt/matcher.py`

**Purpose:** Score jobs against user profile
**Dependencies:** config, models

**Functions:**
- `score_job(job_data: JobPostingData, profile: JobProfile) -> MatchResult`: Main scoring function
- `keyword_score(description: str, profile: JobProfile) -> float`: Keyword matching (0-1)
- `industry_score(description: str, profile: JobProfile) -> float`: Industry match (0-1, negative for avoid)
- `role_score(title: str, profile: JobProfile) -> float`: Title match (0-1)
- `red_flag_score(description: str, profile: JobProfile) -> float`: Anti-pattern detection (0-1, lower is worse)

**Models:**
```python
class MatchResult(BaseModel):
    overall_score: float  # 0-100
    breakdown: dict[str, float]  # Per-category scores
    red_flags: list[str]  # Detected anti-patterns
    highlights: list[str]  # Positive matches
    recommendation: str  # "Strong match", "Worth reviewing", "Likely skip"
```

**Scoring weights:**
- Role match: 30%
- Tech keywords: 25%
- Industry: 20%
- Red flags: 25% (penalty)

**Constraints:**
- Case-insensitive matching
- Fuzzy matching for role titles (CTO ≈ Chief Technology Officer)
- Return explanation with scores
- Score range: 0-100

---

### `.claude/skills/job-match/skill.md`

**Purpose:** Score a job against profile

```markdown
# Match Job Against Profile

Analyze a job posting and score it against your profile.

## Usage

\`\`\`
/job-match <url>
\`\`\`

## Instructions

1. Fetch and analyze the job posting:
   \`\`\`bash
   uv run jobhunt match "<url>"
   \`\`\`

2. Display the match results:
   - Overall score (0-100)
   - Breakdown by category
   - Red flags detected
   - Highlights found
   - Recommendation

3. Ask user if they want to add it to their tracker.

## Example Output

\`\`\`
Job: Senior Engineering Manager at TechCorp
Score: 72/100

Breakdown:
  Role match: 85% (close to target titles)
  Tech focus: 70% (mentions AI, ML)
  Industry: 60% (B2B SaaS - neutral)
  Red flags: 75% (no major concerns)

Highlights:
  ✓ "AI-first product development"
  ✓ "Technical leadership"
  ✓ "Hands-on when needed"

Red flags:
  ⚠ "Some travel required"

Recommendation: Worth reviewing

Add to tracker? [y/n]
\`\`\`
```

---

### `src/jobhunt/cli.py` (MODIFY)

**Change:** Add `match` command

**New command:**
- `jobhunt match <url> [--add]`: Fetch, score, optionally add to tracker

**Behavior:**
1. Fetch job posting with scraper
2. Score against profile with matcher
3. Display results with rich formatting
4. If `--add` flag or user confirms, add to tracker with score

**Output format:**
- Use `rich.panel.Panel` for results
- Color-code score (green >70, yellow 50-70, red <50)
- Bullet list for highlights/red flags

---

## Files to Modify

### `pyproject.toml` (MODIFY)

**Change:** Add beautifulsoup4 dependency

```toml
dependencies = [
    ...
    "beautifulsoup4>=4.12.0",
    "lxml>=5.0.0",  # Fast HTML parser
]
```

---

## Implementation Order

1. `pyproject.toml` - Add beautifulsoup4, lxml
2. `src/jobhunt/scraper.py` - Job posting fetcher
3. `src/jobhunt/matcher.py` - Scoring engine
4. `src/jobhunt/cli.py` - Add match command
5. `.claude/skills/job-match/skill.md` - Skill

---

## Verification

After implementation:
1. Run `uv sync` to install new dependencies
2. Run `uv run jobhunt match "https://www.linkedin.com/jobs/view/123456"`
3. Verify score output and breakdown
4. Test `--add` flag to add scored job to tracker
