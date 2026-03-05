# Phase 4: Web Dashboard — Overview

**Date:** 2026-03-05
**Feature:** Web dashboard for visual pipeline management
**Sub-phases:** 3
**Tech Stack:** FastAPI, Jinja2, HTMX, Tailwind CSS (CDN)

---

## Overview

Add a localhost web dashboard that provides visual pipeline management while reusing existing `db.py` functions. CLI remains primary; web is for visualization.

Key views (from MOCKUPS.md):
- Pipeline View — Status counts + job cards grouped by status
- Job Detail — Match analysis, company research, notes, timeline
- Kanban Board — Drag-drop status changes
- Prospect Review — Bulk review discovered jobs
- Stats Dashboard — Application analytics

---

## Sub-Phase Summary

| Phase | Title | Files | Agent | Dependencies |
|-------|-------|-------|-------|--------------|
| 4.1 | FastAPI Backend Core | 8 | python-fastapi | Existing db.py |
| 4.2 | Templates & Dashboard | 9 | python-fastapi | Phase 4.1 |
| 4.3 | Prospect Review + Stats | 6 | python-fastapi | Phase 4.1, 4.2 |

---

## Cross-Phase Dependencies

- **Phase 4.2** requires: `app.py`, routers from Phase 4.1
- **Phase 4.3** requires: `base.html`, partials from Phase 4.2

---

## File Summary

### Phase 4.1 — FastAPI Backend Core
| File | Type |
|------|------|
| `src/jobhunt/web/__init__.py` | Module |
| `src/jobhunt/web/app.py` | App factory |
| `src/jobhunt/web/dependencies.py` | DI |
| `src/jobhunt/web/routers/__init__.py` | Module |
| `src/jobhunt/web/routers/dashboard.py` | Router |
| `src/jobhunt/web/routers/jobs.py` | Router |
| `src/jobhunt/cli.py` | MODIFY: add serve command |
| `pyproject.toml` | MODIFY: add fastapi, jinja2, uvicorn |

### Phase 4.2 — Templates & Dashboard
| File | Type |
|------|------|
| `src/jobhunt/web/templates/base.html` | Layout |
| `src/jobhunt/web/templates/dashboard.html` | Page |
| `src/jobhunt/web/templates/job_detail.html` | Page |
| `src/jobhunt/web/templates/kanban.html` | Page |
| `src/jobhunt/web/templates/add_job.html` | Modal |
| `src/jobhunt/web/templates/partials/job_card.html` | Partial |
| `src/jobhunt/web/templates/partials/status_counts.html` | Partial |
| `src/jobhunt/web/templates/partials/job_list.html` | Partial |
| `src/jobhunt/web/static/app.css` | Styles |

### Phase 4.3 — Prospect Review + Stats
| File | Type |
|------|------|
| `src/jobhunt/web/routers/prospects.py` | Router |
| `src/jobhunt/web/routers/stats.py` | Router |
| `src/jobhunt/web/templates/prospects.html` | Page |
| `src/jobhunt/web/templates/stats.html` | Page |
| `src/jobhunt/web/templates/partials/prospect_row.html` | Partial |
| `src/jobhunt/web/templates/partials/stats_cards.html` | Partial |

---

## Architecture Notes

### Reuse existing db.py
The web layer calls existing functions directly:
- `list_jobs()`, `get_job()`, `update_job()`, `add_job()`
- `list_prospects()`, `track_prospect()`, `dismiss_prospect()`
- No new ORM or repository layer needed

### HTMX Patterns
- Status changes via `hx-post` + `hx-swap`
- Partial updates return HTML fragments
- No client-side JavaScript framework

### URL Structure
```
/                     → Dashboard (pipeline view)
/kanban               → Kanban board
/jobs/{id}            → Job detail
/jobs/{id}/status     → HTMX: Update status
/jobs/add             → HTMX: Add job modal
/prospects            → Prospect review
/prospects/{id}/track → HTMX: Track prospect
/prospects/{id}/dismiss → HTMX: Dismiss prospect
/stats                → Analytics dashboard
```

---

## Next Steps

1. Review `IMPLEMENTATION_PLAN_PHASE_4_1.md` for backend specs
2. Run `/plan-validate` to check spec completeness
3. Run `/implement-phase 4.1` to begin implementation
