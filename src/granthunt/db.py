import sqlite3
from datetime import datetime
from pathlib import Path

from granthunt.models import (
    Grant,
    GrantCreate,
    GrantProspect,
    GrantStatus,
    GrantUpdate,
    ProspectCreate,
    ProspectStatus,
    ProspectUpdate,
    ScrapeHistory,
)


def get_project_root() -> Path:
    """Get the project root directory.

    Looks for pyproject.toml in current directory or parent directories.
    """
    cwd = Path.cwd()

    for directory in [cwd, *cwd.parents]:
        if (directory / "pyproject.toml").exists():
            return directory

    return cwd


def get_db_path() -> Path:
    """Return the default database path (grants.db in project root)."""
    return get_project_root() / "grants.db"


def init_db(path: Path | None = None) -> sqlite3.Connection:
    """Initialize the database and create tables if they don't exist.

    Args:
        path: Path to the database file. Defaults to grants.db in project root.

    Returns:
        SQLite connection object.
    """
    if path is None:
        path = get_db_path()

    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS grants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            organization TEXT NOT NULL,
            program TEXT,
            location TEXT,
            status TEXT DEFAULT 'DISCOVERED',
            score REAL,
            notes TEXT,
            raw_description TEXT,
            deadline TEXT,
            amount_min REAL,
            amount_max REAL,
            grant_type TEXT,
            date_added TEXT NOT NULL,
            date_updated TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_grants_status ON grants(status);
        CREATE INDEX IF NOT EXISTS idx_grants_organization ON grants(organization);

        CREATE TABLE IF NOT EXISTS grant_prospects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            organization TEXT NOT NULL,
            program TEXT,
            location TEXT,
            summary TEXT,
            amount_range TEXT,
            quick_score REAL,
            source TEXT DEFAULT 'innovation_canada',
            external_id TEXT,
            status TEXT DEFAULT 'PENDING',
            grant_id INTEGER,
            deadline TEXT,
            discovered_at TEXT NOT NULL,
            FOREIGN KEY (grant_id) REFERENCES grants(id)
        );
        CREATE INDEX IF NOT EXISTS idx_prospects_status ON grant_prospects(status);
        CREATE INDEX IF NOT EXISTS idx_prospects_score ON grant_prospects(quick_score DESC);
        CREATE INDEX IF NOT EXISTS idx_prospects_external ON grant_prospects(source, external_id);

        CREATE TABLE IF NOT EXISTS scrape_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            query TEXT,
            scraped_at TEXT NOT NULL,
            jobs_found INTEGER DEFAULT 0,
            new_jobs INTEGER DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_scrape_source ON scrape_history(source, scraped_at DESC);
    """)
    conn.commit()

    return conn


def _row_to_grant(row: sqlite3.Row) -> Grant:
    """Convert a database row to a Grant model."""
    return Grant(
        id=row["id"],
        url=row["url"],
        title=row["title"],
        organization=row["organization"],
        program=row["program"],
        location=row["location"],
        status=GrantStatus(row["status"]),
        score=row["score"],
        notes=row["notes"],
        raw_description=row["raw_description"],
        deadline=row["deadline"],
        amount_min=row["amount_min"],
        amount_max=row["amount_max"],
        grant_type=row["grant_type"],
        date_added=datetime.fromisoformat(row["date_added"]),
        date_updated=datetime.fromisoformat(row["date_updated"]),
    )


def add_grant(conn: sqlite3.Connection, grant: GrantCreate) -> Grant:
    """Add a new grant to the database.

    If the URL already exists, returns the existing grant instead.

    Args:
        conn: Database connection.
        grant: Grant data to insert.

    Returns:
        The created or existing Grant.
    """
    existing = get_grant_by_url(conn, grant.url)
    if existing:
        return existing

    now = datetime.now().isoformat()
    cursor = conn.execute(
        """
        INSERT INTO grants (url, title, organization, program, location, notes, deadline, amount_min, amount_max, grant_type, date_added, date_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            grant.url,
            grant.title,
            grant.organization,
            grant.program,
            grant.location,
            grant.notes,
            grant.deadline,
            grant.amount_min,
            grant.amount_max,
            grant.grant_type,
            now,
            now,
        ),
    )
    conn.commit()

    return get_grant(conn, cursor.lastrowid)  # type: ignore


def get_grant(conn: sqlite3.Connection, grant_id: int) -> Grant | None:
    """Get a grant by its ID.

    Args:
        conn: Database connection.
        grant_id: The grant's ID.

    Returns:
        The Grant if found, None otherwise.
    """
    cursor = conn.execute("SELECT * FROM grants WHERE id = ?", (grant_id,))
    row = cursor.fetchone()
    if row is None:
        return None
    return _row_to_grant(row)


def get_grant_by_url(conn: sqlite3.Connection, url: str) -> Grant | None:
    """Get a grant by its URL.

    Args:
        conn: Database connection.
        url: The grant posting URL.

    Returns:
        The Grant if found, None otherwise.
    """
    cursor = conn.execute("SELECT * FROM grants WHERE url = ?", (url,))
    row = cursor.fetchone()
    if row is None:
        return None
    return _row_to_grant(row)


def list_grants(
    conn: sqlite3.Connection, status: GrantStatus | None = None
) -> list[Grant]:
    """List all grants, optionally filtered by status.

    Args:
        conn: Database connection.
        status: Optional status to filter by.

    Returns:
        List of Grant objects.
    """
    if status is not None:
        cursor = conn.execute(
            "SELECT * FROM grants WHERE status = ? ORDER BY date_updated DESC",
            (status.value,),
        )
    else:
        cursor = conn.execute("SELECT * FROM grants ORDER BY date_updated DESC")

    return [_row_to_grant(row) for row in cursor.fetchall()]


def update_grant(
    conn: sqlite3.Connection, grant_id: int, update: GrantUpdate
) -> Grant | None:
    """Update a grant's fields.

    Args:
        conn: Database connection.
        grant_id: The grant's ID.
        update: Fields to update.

    Returns:
        The updated Grant if found, None otherwise.
    """
    existing = get_grant(conn, grant_id)
    if existing is None:
        return None

    updates = []
    values = []

    if update.status is not None:
        updates.append("status = ?")
        values.append(update.status.value)

    if update.score is not None:
        updates.append("score = ?")
        values.append(update.score)

    if update.notes is not None:
        updates.append("notes = ?")
        values.append(update.notes)

    if not updates:
        return existing

    updates.append("date_updated = ?")
    values.append(datetime.now().isoformat())
    values.append(grant_id)

    conn.execute(
        f"UPDATE grants SET {', '.join(updates)} WHERE id = ?",
        values,
    )
    conn.commit()

    return get_grant(conn, grant_id)


def delete_grant(conn: sqlite3.Connection, grant_id: int) -> bool:
    """Delete a grant from the database.

    Args:
        conn: Database connection.
        grant_id: The grant's ID.

    Returns:
        True if the grant was deleted, False if it didn't exist.
    """
    cursor = conn.execute("DELETE FROM grants WHERE id = ?", (grant_id,))
    conn.commit()
    return cursor.rowcount > 0


def _row_to_prospect(row: sqlite3.Row) -> GrantProspect:
    """Convert a database row to a GrantProspect model."""
    keys = row.keys()
    return GrantProspect(
        id=row["id"],
        url=row["url"],
        title=row["title"],
        organization=row["organization"],
        program=row["program"] if "program" in keys else None,
        location=row["location"],
        summary=row["summary"] if "summary" in keys else None,
        amount_range=row["amount_range"] if "amount_range" in keys else None,
        quick_score=row["quick_score"],
        source=row["source"],
        external_id=row["external_id"] if "external_id" in keys else None,
        status=ProspectStatus(row["status"]),
        grant_id=row["grant_id"],
        deadline=row["deadline"] if "deadline" in keys else None,
        discovered_at=datetime.fromisoformat(row["discovered_at"]),
    )


def add_prospect(conn: sqlite3.Connection, prospect: ProspectCreate) -> GrantProspect:
    """Add a new prospect to the database.

    If the URL already exists, returns the existing prospect instead.
    """
    existing = get_prospect_by_url(conn, prospect.url)
    if existing:
        return existing

    now = datetime.now().isoformat()
    cursor = conn.execute(
        """
        INSERT INTO grant_prospects (url, title, organization, program, location, summary, amount_range, quick_score, source, external_id, deadline, discovered_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            prospect.url,
            prospect.title,
            prospect.organization,
            prospect.program,
            prospect.location,
            prospect.summary,
            prospect.amount_range,
            prospect.quick_score,
            prospect.source,
            prospect.external_id,
            prospect.deadline,
            now,
        ),
    )
    conn.commit()

    return get_prospect(conn, cursor.lastrowid)  # type: ignore


def get_prospect(conn: sqlite3.Connection, prospect_id: int) -> GrantProspect | None:
    """Get a prospect by its ID."""
    cursor = conn.execute("SELECT * FROM grant_prospects WHERE id = ?", (prospect_id,))
    row = cursor.fetchone()
    if row is None:
        return None
    return _row_to_prospect(row)


def get_prospect_by_url(conn: sqlite3.Connection, url: str) -> GrantProspect | None:
    """Get a prospect by its URL."""
    cursor = conn.execute("SELECT * FROM grant_prospects WHERE url = ?", (url,))
    row = cursor.fetchone()
    if row is None:
        return None
    return _row_to_prospect(row)


def list_prospects(
    conn: sqlite3.Connection,
    status: ProspectStatus | None = None,
    sort_by: str = "quick_score",
    sort_dir: str = "desc",
) -> list[GrantProspect]:
    """List all prospects, optionally filtered by status.

    Args:
        conn: Database connection.
        status: Optional status filter.
        sort_by: Column to sort by (quick_score, discovered_at, title, organization).
        sort_dir: Sort direction (asc or desc).
    """
    valid_columns = {
        "quick_score",
        "discovered_at",
        "title",
        "organization",
        "location",
    }
    if sort_by not in valid_columns:
        sort_by = "quick_score"
    sort_dir = "ASC" if sort_dir.lower() == "asc" else "DESC"

    if status is not None:
        cursor = conn.execute(
            f"SELECT * FROM grant_prospects WHERE status = ? ORDER BY {sort_by} {sort_dir}",
            (status.value,),
        )
    else:
        cursor = conn.execute(
            f"SELECT * FROM grant_prospects ORDER BY {sort_by} {sort_dir}"
        )

    return [_row_to_prospect(row) for row in cursor.fetchall()]


def update_prospect(
    conn: sqlite3.Connection, prospect_id: int, update: ProspectUpdate
) -> GrantProspect | None:
    """Update a prospect's status."""
    existing = get_prospect(conn, prospect_id)
    if existing is None:
        return None

    updates = []
    values = []

    if update.status is not None:
        updates.append("status = ?")
        values.append(update.status.value)

    if update.grant_id is not None:
        updates.append("grant_id = ?")
        values.append(update.grant_id)

    if not updates:
        return existing

    values.append(prospect_id)

    conn.execute(
        f"UPDATE grant_prospects SET {', '.join(updates)} WHERE id = ?",
        values,
    )
    conn.commit()

    return get_prospect(conn, prospect_id)


def dismiss_prospect(conn: sqlite3.Connection, prospect_id: int) -> bool:
    """Mark a prospect as dismissed."""
    result = update_prospect(
        conn, prospect_id, ProspectUpdate(status=ProspectStatus.DISMISSED)
    )
    return result is not None


def track_prospect(conn: sqlite3.Connection, prospect_id: int) -> Grant | None:
    """Move a prospect to the grants tracker.

    Creates a new grant from the prospect and marks the prospect as tracked.
    """
    prospect = get_prospect(conn, prospect_id)
    if prospect is None:
        return None

    grant = add_grant(
        conn,
        GrantCreate(
            url=prospect.url,
            title=prospect.title,
            organization=prospect.organization,
            program=prospect.program,
            location=prospect.location,
            notes=f"Quick score: {prospect.quick_score}",
            deadline=prospect.deadline,
        ),
    )

    update_prospect(
        conn,
        prospect_id,
        ProspectUpdate(status=ProspectStatus.TRACKED, grant_id=grant.id),
    )

    return grant


def count_prospects_by_status(conn: sqlite3.Connection) -> dict[str, int]:
    """Get counts of prospects by status."""
    cursor = conn.execute(
        "SELECT status, COUNT(*) as count FROM grant_prospects GROUP BY status"
    )
    return {row["status"]: row["count"] for row in cursor.fetchall()}


def prospect_exists_by_external_id(
    conn: sqlite3.Connection, source: str, external_id: str
) -> bool:
    """Check if a prospect with this external_id already exists for this source."""
    cursor = conn.execute(
        "SELECT 1 FROM grant_prospects WHERE source = ? AND external_id = ?",
        (source, external_id),
    )
    return cursor.fetchone() is not None


def get_known_external_ids(conn: sqlite3.Connection, source: str) -> set[str]:
    """Get all known external IDs for a source (for batch checking)."""
    cursor = conn.execute(
        "SELECT external_id FROM grant_prospects WHERE source = ? AND external_id IS NOT NULL",
        (source,),
    )
    return {row["external_id"] for row in cursor.fetchall()}


def _row_to_scrape_history(row: sqlite3.Row) -> ScrapeHistory:
    """Convert a database row to a ScrapeHistory model."""
    return ScrapeHistory(
        id=row["id"],
        source=row["source"],
        query=row["query"],
        scraped_at=datetime.fromisoformat(row["scraped_at"]),
        jobs_found=row["jobs_found"],
        new_jobs=row["new_jobs"],
    )


def record_scrape(
    conn: sqlite3.Connection,
    source: str,
    query: str | None,
    jobs_found: int,
    new_jobs: int,
) -> ScrapeHistory:
    """Record a scrape event."""
    now = datetime.now().isoformat()
    cursor = conn.execute(
        """
        INSERT INTO scrape_history (source, query, scraped_at, jobs_found, new_jobs)
        VALUES (?, ?, ?, ?, ?)
        """,
        (source, query, now, jobs_found, new_jobs),
    )
    conn.commit()

    return _row_to_scrape_history(
        conn.execute(
            "SELECT * FROM scrape_history WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    )


def get_last_scrape(conn: sqlite3.Connection, source: str) -> ScrapeHistory | None:
    """Get the most recent scrape for a source."""
    cursor = conn.execute(
        "SELECT * FROM scrape_history WHERE source = ? ORDER BY scraped_at DESC LIMIT 1",
        (source,),
    )
    row = cursor.fetchone()
    if row is None:
        return None
    return _row_to_scrape_history(row)


def list_scrape_history(
    conn: sqlite3.Connection, source: str | None = None, limit: int = 10
) -> list[ScrapeHistory]:
    """List recent scrape history."""
    if source:
        cursor = conn.execute(
            "SELECT * FROM scrape_history WHERE source = ? ORDER BY scraped_at DESC LIMIT ?",
            (source, limit),
        )
    else:
        cursor = conn.execute(
            "SELECT * FROM scrape_history ORDER BY scraped_at DESC LIMIT ?",
            (limit,),
        )
    return [_row_to_scrape_history(row) for row in cursor.fetchall()]
