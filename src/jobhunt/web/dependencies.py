"""Shared FastAPI dependency factories for the web module."""

from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING, Generator

from fastapi import Request
from fastapi.templating import Jinja2Templates

from jobhunt.db import init_db

if TYPE_CHECKING:
    pass


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Yield a database connection, closing it after the request."""
    conn = init_db()
    try:
        yield conn
    finally:
        conn.close()


def get_templates(request: Request) -> Jinja2Templates:
    """Return the Jinja2Templates instance from app state."""
    return request.app.state.templates  # type: ignore[no-any-return]
