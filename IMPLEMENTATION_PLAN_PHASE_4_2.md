# Phase 4.2: Templates & Dashboard

**Dependencies:** Phase 4.1 (app.py, routers)
**Agent:** python-fastapi

---

## Files to Create

### `src/jobhunt/web/templates/base.html`

**Purpose:** Base layout with HTMX, Tailwind CDN, navigation
**Structure:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}JobHunt{% endblock %}</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="/static/app.css">
</head>
<body class="bg-gray-100 min-h-screen">
    <nav class="bg-white shadow-sm border-b">
        <div class="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
            <a href="/" class="text-xl font-bold text-gray-800">JobHunt</a>
            <div class="flex gap-4">
                <a href="/" class="text-gray-600 hover:text-gray-900">Pipeline</a>
                <a href="/kanban" class="text-gray-600 hover:text-gray-900">Kanban</a>
                <a href="/prospects" class="text-gray-600 hover:text-gray-900">Prospects</a>
                <a href="/stats" class="text-gray-600 hover:text-gray-900">Stats</a>
            </div>
            <button hx-get="/jobs/add" hx-target="#modal" hx-swap="innerHTML"
                    class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                + Add Job
            </button>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 py-6">
        {% block content %}{% endblock %}
    </main>

    <div id="modal"></div>
</body>
</html>
```

**Constraints:**
- Use Tailwind CDN for MVP (no build step)
- HTMX 1.9.x for stability
- Modal container at bottom for HTMX swaps

---

### `src/jobhunt/web/templates/dashboard.html`

**Purpose:** Pipeline view with status counts and job cards
**Extends:** `base.html`
**Context variables:** `jobs_by_status: dict[JobStatus, list[Job]]`, `status_counts: dict[JobStatus, int]`

**Structure:**
```html
{% extends "base.html" %}
{% block title %}Pipeline - JobHunt{% endblock %}

{% block content %}
<div class="mb-8">
    <h1 class="text-2xl font-bold mb-4">Pipeline Overview</h1>

    <!-- Status counts bar -->
    {% include "partials/status_counts.html" %}
</div>

<!-- Job lists by status -->
{% for status in ["NEW", "INTERESTED", "APPLIED", "INTERVIEWING", "OFFER"] %}
<div class="mb-6">
    <h2 class="text-lg font-semibold text-gray-700 mb-3 flex items-center gap-2">
        {{ status }}
        <span class="bg-gray-200 text-gray-600 text-sm px-2 py-0.5 rounded-full">
            {{ status_counts[status] }}
        </span>
    </h2>

    <div class="space-y-3" id="list-{{ status|lower }}">
        {% for job in jobs_by_status[status] %}
            {% include "partials/job_card.html" %}
        {% endfor %}

        {% if not jobs_by_status[status] %}
            <p class="text-gray-400 italic">No jobs in this stage</p>
        {% endif %}
    </div>
</div>
{% endfor %}
{% endblock %}
```

**Constraints:**
- Use Jinja2 `{% include %}` for partials
- Status order: NEW, INTERESTED, APPLIED, INTERVIEWING, OFFER (skip REJECTED/WITHDRAWN in main view)
- Empty state message for each status group

---

### `src/jobhunt/web/templates/job_detail.html`

**Purpose:** Full job detail page with match analysis, research, notes
**Extends:** `base.html`
**Context variables:** `job: Job`, `research: str | None`, `has_cover_letter: bool`

**Structure:**
```html
{% extends "base.html" %}
{% block title %}{{ job.title }} - JobHunt{% endblock %}

{% block content %}
<a href="/" class="text-blue-600 hover:underline mb-4 inline-block">&larr; Back to Pipeline</a>

<div class="bg-white rounded-lg shadow p-6 mb-6">
    <h1 class="text-2xl font-bold">{{ job.title }}</h1>
    <p class="text-gray-600">{{ job.company }} &middot; {{ job.location or "Location not specified" }}</p>

    <div class="mt-4 flex items-center gap-4">
        <span class="text-sm text-gray-500">Status:</span>
        <select hx-post="/jobs/{{ job.id }}/status" hx-swap="none"
                name="status" class="border rounded px-2 py-1">
            {% for s in statuses %}
                <option value="{{ s.value }}" {% if s == job.status %}selected{% endif %}>
                    {{ s.value }}
                </option>
            {% endfor %}
        </select>

        {% if job.score %}
        <span class="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
            Score: {{ job.score|int }}/100
        </span>
        {% endif %}
    </div>
</div>

<!-- Actions -->
<div class="bg-white rounded-lg shadow p-4 mb-6 flex gap-4">
    <a href="{{ job.url }}" target="_blank"
       class="bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded">
        View Posting
    </a>
    {% if has_cover_letter %}
    <a href="/jobs/{{ job.id }}/cover-letter" class="bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded">
        Cover Letter
    </a>
    {% endif %}
</div>

<!-- Company Research -->
{% if research %}
<div class="bg-white rounded-lg shadow p-6 mb-6">
    <h2 class="text-lg font-semibold mb-3">Company Research</h2>
    <div class="prose prose-sm max-w-none text-gray-700">
        {{ research | safe }}
    </div>
</div>
{% endif %}

<!-- Notes -->
<div class="bg-white rounded-lg shadow p-6 mb-6">
    <h2 class="text-lg font-semibold mb-3">Notes</h2>
    <p class="text-gray-700">{{ job.notes or "No notes yet" }}</p>
</div>
{% endblock %}
```

**Constraints:**
- Status dropdown triggers HTMX POST on change
- Research content rendered with `| safe` (it's markdown converted to HTML)
- Links open in new tab (`target="_blank"`)

---

### `src/jobhunt/web/templates/kanban.html`

**Purpose:** Kanban board with draggable cards
**Extends:** `base.html`
**Context variables:** `jobs_by_status: dict[JobStatus, list[Job]]`

**Structure:**
```html
{% extends "base.html" %}
{% block title %}Kanban - JobHunt{% endblock %}

{% block content %}
<h1 class="text-2xl font-bold mb-6">Kanban Board</h1>

<div class="flex gap-4 overflow-x-auto pb-4">
    {% for status in ["NEW", "INTERESTED", "APPLIED", "INTERVIEWING", "OFFER"] %}
    <div class="flex-shrink-0 w-72 bg-gray-50 rounded-lg p-4">
        <h2 class="font-semibold text-gray-700 mb-3">{{ status }}</h2>

        <div class="space-y-3 min-h-[200px]" id="kanban-{{ status|lower }}">

            {% for job in jobs_by_status[status] %}
            <a href="/jobs/{{ job.id }}" class="block bg-white rounded shadow p-3 hover:shadow-md transition-shadow">
                <p class="font-medium text-sm">{{ job.title }}</p>
                <p class="text-xs text-gray-500">{{ job.company }}</p>
                {% if job.score %}
                <span class="text-xs text-green-600">{{ job.score|int }}</span>
                {% endif %}
            </a>
            {% endfor %}
        </div>
    </div>
    {% endfor %}
</div>

<p class="text-gray-400 text-sm mt-4">Click cards to view details and change status</p>
{% endblock %}
```

**Constraints:**
- Horizontal scroll for many columns
- Fixed column width (w-72 = 18rem)
- Cards link to detail page (drag-drop deferred to Phase 5)

---

### `src/jobhunt/web/templates/add_job.html`

**Purpose:** Modal form for adding new job
**Context variables:** None (standalone modal)

**Structure:**
```html
<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
     onclick="this.remove()">
    <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md" onclick="event.stopPropagation()">
        <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold">Add New Job</h2>
            <button onclick="this.closest('#modal').innerHTML=''" class="text-gray-400 hover:text-gray-600">
                &times;
            </button>
        </div>

        <form hx-post="/jobs/add" hx-target="body" hx-swap="outerHTML">
            <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">Job URL *</label>
                <input type="url" name="url" required
                       class="w-full border rounded px-3 py-2"
                       placeholder="https://linkedin.com/jobs/view/...">
            </div>

            <div class="grid grid-cols-2 gap-4 mb-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                    <input type="text" name="title" required class="w-full border rounded px-3 py-2">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Company *</label>
                    <input type="text" name="company" required class="w-full border rounded px-3 py-2">
                </div>
            </div>

            <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
                <input type="text" name="location" class="w-full border rounded px-3 py-2">
            </div>

            <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <textarea name="notes" rows="3" class="w-full border rounded px-3 py-2"></textarea>
            </div>

            <div class="flex justify-end gap-3">
                <button type="button" onclick="this.closest('#modal').innerHTML=''"
                        class="px-4 py-2 text-gray-600 hover:text-gray-800">
                    Cancel
                </button>
                <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                    Add to Pipeline
                </button>
            </div>
        </form>
    </div>
</div>
```

**Constraints:**
- Modal closes on backdrop click or X button
- Form submits via HTMX, replaces entire page on success
- Required fields: url, title, company

---

### `src/jobhunt/web/templates/partials/job_card.html`

**Purpose:** Single job card for pipeline view
**Context variables:** `job: Job`

**Structure:**
```html
<div id="job-card-{{ job.id }}"
     class="bg-white rounded-lg shadow p-4 flex justify-between items-center hover:shadow-md transition-shadow">
    <div>
        <a href="/jobs/{{ job.id }}" class="font-medium text-gray-900 hover:text-blue-600">
            {{ job.title }}
        </a>
        <p class="text-sm text-gray-500">{{ job.company }} &middot; {{ job.location or "Remote" }}</p>
    </div>

    <div class="flex items-center gap-3">
        {% if job.score %}
        <span class="bg-{% if job.score >= 80 %}green{% elif job.score >= 60 %}yellow{% else %}gray{% endif %}-100
                     text-{% if job.score >= 80 %}green{% elif job.score >= 60 %}yellow{% else %}gray{% endif %}-800
                     px-2 py-1 rounded text-sm">
            {{ job.score|int }}
        </span>
        {% endif %}

        <select hx-post="/jobs/{{ job.id }}/status" hx-target="#job-card-{{ job.id }}" hx-swap="outerHTML"
                name="status" class="text-sm border rounded px-2 py-1">
            {% for s in ["NEW", "INTERESTED", "APPLIED", "INTERVIEWING", "OFFER", "REJECTED", "WITHDRAWN"] %}
                <option value="{{ s }}" {% if s == job.status.value %}selected{% endif %}>{{ s }}</option>
            {% endfor %}
        </select>
    </div>
</div>
```

**Constraints:**
- Card has unique ID for HTMX targeting
- Score color: green >= 80, yellow >= 60, gray below
- Status dropdown swaps entire card on change

---

### `src/jobhunt/web/templates/partials/status_counts.html`

**Purpose:** Status count badges bar
**Context variables:** `status_counts: dict[str, int]`

**Structure:**
```html
<div class="flex gap-4 mb-6">
    {% for status, count in status_counts.items() %}
    <div class="bg-white rounded-lg shadow px-4 py-3 text-center min-w-[100px]">
        <p class="text-2xl font-bold text-gray-800">{{ count }}</p>
        <p class="text-xs text-gray-500 uppercase">{{ status }}</p>
    </div>
    {% endfor %}
</div>
```

---

### `src/jobhunt/web/templates/partials/job_list.html`

**Purpose:** List of job cards for a single status (HTMX refresh target)
**Context variables:** `jobs: list[Job]`, `status: str`

**Structure:**
```html
<div class="space-y-3" id="list-{{ status|lower }}">
    {% for job in jobs %}
        {% include "partials/job_card.html" %}
    {% endfor %}

    {% if not jobs %}
        <p class="text-gray-400 italic">No jobs in this stage</p>
    {% endif %}
</div>
```

---

### `src/jobhunt/web/static/app.css`

**Purpose:** Custom styles beyond Tailwind
**Content:**
```css
/* Custom scrollbar for kanban */
.overflow-x-auto::-webkit-scrollbar {
    height: 8px;
}
.overflow-x-auto::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}
.overflow-x-auto::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 4px;
}

/* HTMX loading indicator */
.htmx-request {
    opacity: 0.5;
    transition: opacity 200ms;
}

/* Modal backdrop animation */
#modal > div {
    animation: fadeIn 150ms ease-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}
```

---

## Verification

After implementation:
1. `uv run jobhunt serve` — Start server
2. Open `http://127.0.0.1:8000/` — See pipeline view
3. Click job card — Navigate to detail
4. Change status dropdown — Card updates via HTMX
5. Click "+ Add Job" — Modal appears
6. Visit `/kanban` — See kanban view
