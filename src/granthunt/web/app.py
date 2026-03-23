"""FastAPI application factory for the JobHunt web dashboard."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routers import dashboard, jobs, prospects, stats


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app = FastAPI(title="GrantHunt")

    base_path = Path(__file__).parent

    app.mount(
        "/static",
        StaticFiles(directory=base_path / "static"),
        name="static",
    )

    templates = Jinja2Templates(directory=base_path / "templates")
    app.state.templates = templates

    app.include_router(dashboard.router)
    app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
    app.include_router(prospects.router)
    app.include_router(stats.router)

    return app
