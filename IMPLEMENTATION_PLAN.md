# JobHunt Implementation Plan

**Date:** 2026-03-05
**Features:** Job search automation system
**Total Phases:** 3
**Tech Stack:** Python 3.13, uv, SQLite, typer, httpx, pydantic, pyyaml

---

## Overview

Build a job search automation system with:
1. **Phase 1:** Core infrastructure (profile config, SQLite tracker, CLI, skills)
2. **Phase 2:** Matching and scoring engine (scraper, LLM-based scoring)
3. **Phase 3:** Application helpers (cover letter generation, company research)

---

## Phase Summary

| Phase | Title | Files | Agent | Dependencies |
|-------|-------|-------|-------|--------------|
| 1 | Core Infrastructure | 10 | python-cli | None |
| 2 | Matching & Scoring | 4 | python-cli | Phase 1 |
| 3 | Application Helpers | 3 | python-cli | Phase 1, 2 |

---

## Cross-Phase Dependencies

- **Phase 2** requires: `db.py` (Job model), `config.py` (profile loading) from Phase 1
- **Phase 3** requires: `matcher.py` (job context), `db.py` (job records) from Phase 1-2

---

## Phase Files

| Phase | File | Type |
|-------|------|------|
| 1 | `job_profile.yaml` | Config |
| 1 | `src/jobhunt/__init__.py` | Module |
| 1 | `src/jobhunt/config.py` | Core |
| 1 | `src/jobhunt/db.py` | Core |
| 1 | `src/jobhunt/models.py` | Core |
| 1 | `src/jobhunt/cli.py` | CLI |
| 1 | `.claude/skills/job-add/skill.md` | Skill |
| 1 | `.claude/skills/job-list/skill.md` | Skill |
| 1 | `pyproject.toml` | Config (modify) |
| 1 | `ARCHITECTURE.md` | Docs |
| 2 | `src/jobhunt/scraper.py` | Core |
| 2 | `src/jobhunt/matcher.py` | Core |
| 2 | `.claude/skills/job-match/skill.md` | Skill |
| 2 | `src/jobhunt/cli.py` | CLI (modify) |
| 3 | `src/jobhunt/cover_letter.py` | Core |
| 3 | `src/jobhunt/research.py` | Core |
| 3 | `.claude/skills/job-apply/skill.md` | Skill |

---

## Next Steps

1. Review `IMPLEMENTATION_PLAN_PHASE_1.md` for detailed per-file specs
2. Run `/implement-phase 1` to begin implementation
3. After Phase 1 complete, proceed to Phase 2

---

## Future Vision (Post Phase 3)

**Hybrid Architecture** - Best of CLI + Web UI:

- SQLite backend + Claude Code skills for daily use (Phases 1-3)
- Simple web UI (localhost) for visualization when you want it
- Build incrementally - CLI first, web later

**Phase 4 (future):** Web Dashboard
- FastAPI backend serving job data
- Simple HTML/HTMX or React frontend
- Kanban board view of pipeline
- Charts for application stats

**Phase 5 (future):** Automation
- Browser extension to capture jobs while browsing
- Scheduled job board scraping
- Email notifications for status changes

---

## Job Profile Data (from discovery session)

```yaml
target_roles:
  - CTO
  - VP Engineering
  - Technical Lead / Architect

company_size: "200+"

industries:
  preferred:
    - BioTech / HealthTech
    - Cybersecurity
    - Industrial / Manufacturing
    - Telecoms
    - Energy / Climate Tech
  avoid:
    - Finance
    - Real Estate
    - IT Consulting

tech_focus:
  - AI/ML & LLMs
  - Product Engineering

anti_patterns:
  - Toxic culture
  - Pure management (no technical work)
  - Legacy tech debt without modernization mandate

work_arrangement: flexible

superpower: "Architect who bridges all levels - talks to devs AND directors, solves complex problems"
```
