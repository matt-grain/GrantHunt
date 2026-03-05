import sqlite3
from datetime import datetime
from pathlib import Path

from jobhunt.models import (
    Job,
    JobCreate,
    JobProspect,
    JobStatus,
    JobUpdate,
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
    """Return the default database path (jobs.db in project root)."""
    return get_project_root() / "jobs.db"


def init_db(path: Path | None = None) -> sqlite3.Connection:
    """Initialize the database and create tables if they don't exist.

    Args:
        path: Path to the database file. Defaults to jobs.db in project root.

    Returns:
        SQLite connection object.
    """
    if path is None:
        path = get_db_path()

    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            status TEXT DEFAULT 'NEW',
            score REAL,
            notes TEXT,
            raw_description TEXT,
            date_added TEXT NOT NULL,
            date_updated TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
        CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);

        CREATE TABLE IF NOT EXISTS job_prospects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            summary TEXT,
            salary TEXT,
            quick_score REAL,
            source TEXT DEFAULT 'linkedin',
            external_id TEXT,
            status TEXT DEFAULT 'PENDING',
            job_id INTEGER,
            discovered_at TEXT NOT NULL,
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        );
        CREATE INDEX IF NOT EXISTS idx_prospects_status ON job_prospects(status);
        CREATE INDEX IF NOT EXISTS idx_prospects_score ON job_prospects(quick_score DESC);
        CREATE INDEX IF NOT EXISTS idx_prospects_external ON job_prospects(source, external_id);

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


def _row_to_job(row: sqlite3.Row) -> Job:
    """Convert a database row to a Job model."""
    return Job(
        id=row["id"],
        url=row["url"],
        title=row["title"],
        company=row["company"],
        location=row["location"],
        status=JobStatus(row["status"]),
        score=row["score"],
        notes=row["notes"],
        raw_description=row["raw_description"],
        date_added=datetime.fromisoformat(row["date_added"]),
        date_updated=datetime.fromisoformat(row["date_updated"]),
    )


def add_job(conn: sqlite3.Connection, job: JobCreate) -> Job:
    """Add a new job to the database.

    If the URL already exists, returns the existing job instead.

    Args:
        conn: Database connection.
        job: Job data to insert.

    Returns:
        The created or existing Job.
    """
    existing = get_job_by_url(conn, job.url)
    if existing:
        return existing

    now = datetime.now().isoformat()
    cursor = conn.execute(
        """
        INSERT INTO jobs (url, title, company, location, notes, date_added, date_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (job.url, job.title, job.company, job.location, job.notes, now, now),
    )
    conn.commit()

    return get_job(conn, cursor.lastrowid)  # type: ignore


def get_job(conn: sqlite3.Connection, job_id: int) -> Job | None:
    """Get a job by its ID.

    Args:
        conn: Database connection.
        job_id: The job's ID.

    Returns:
        The Job if found, None otherwise.
    """
    cursor = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    if row is None:
        return None
    return _row_to_job(row)


def get_job_by_url(conn: sqlite3.Connection, url: str) -> Job | None:
    """Get a job by its URL.

    Args:
        conn: Database connection.
        url: The job posting URL.

    Returns:
        The Job if found, None otherwise.
    """
    cursor = conn.execute("SELECT * FROM jobs WHERE url = ?", (url,))
    row = cursor.fetchone()
    if row is None:
        return None
    return _row_to_job(row)


def list_jobs(
    conn: sqlite3.Connection, status: JobStatus | None = None
) -> list[Job]:
    """List all jobs, optionally filtered by status.

    Args:
        conn: Database connection.
        status: Optional status to filter by.

    Returns:
        List of Job objects.
    """
    if status is not None:
        cursor = conn.execute(
            "SELECT * FROM jobs WHERE status = ? ORDER BY date_updated DESC",
            (status.value,),
        )
    else:
        cursor = conn.execute("SELECT * FROM jobs ORDER BY date_updated DESC")

    return [_row_to_job(row) for row in cursor.fetchall()]


def update_job(
    conn: sqlite3.Connection, job_id: int, update: JobUpdate
) -> Job | None:
    """Update a job's fields.

    Args:
        conn: Database connection.
        job_id: The job's ID.
        update: Fields to update.

    Returns:
        The updated Job if found, None otherwise.
    """
    existing = get_job(conn, job_id)
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
    values.append(job_id)

    conn.execute(
        f"UPDATE jobs SET {', '.join(updates)} WHERE id = ?",
        values,
    )
    conn.commit()

    return get_job(conn, job_id)


def delete_job(conn: sqlite3.Connection, job_id: int) -> bool:
    """Delete a job from the database.

    Args:
        conn: Database connection.
        job_id: The job's ID.

    Returns:
        True if the job was deleted, False if it didn't exist.
    """
    cursor = conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    return cursor.rowcount > 0


def _row_to_prospect(row: sqlite3.Row) -> JobProspect:
    """Convert a database row to a JobProspect model."""
    keys = row.keys()
    return JobProspect(
        id=row["id"],
        url=row["url"],
        title=row["title"],
        company=row["company"],
        location=row["location"],
        summary=row["summary"] if "summary" in keys else None,
        salary=row["salary"] if "salary" in keys else None,
        quick_score=row["quick_score"],
        source=row["source"],
        external_id=row["external_id"] if "external_id" in keys else None,
        status=ProspectStatus(row["status"]),
        job_id=row["job_id"],
        discovered_at=datetime.fromisoformat(row["discovered_at"]),
    )


def add_prospect(conn: sqlite3.Connection, prospect: ProspectCreate) -> JobProspect:
    """Add a new prospect to the database.

    If the URL already exists, returns the existing prospect instead.
    """
    existing = get_prospect_by_url(conn, prospect.url)
    if existing:
        return existing

    now = datetime.now().isoformat()
    cursor = conn.execute(
        """
        INSERT INTO job_prospects (url, title, company, location, summary, salary, quick_score, source, external_id, discovered_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            prospect.url,
            prospect.title,
            prospect.company,
            prospect.location,
            prospect.summary,
            prospect.salary,
            prospect.quick_score,
            prospect.source,
            prospect.external_id,
            now,
        ),
    )
    conn.commit()

    return get_prospect(conn, cursor.lastrowid)  # type: ignore


def get_prospect(conn: sqlite3.Connection, prospect_id: int) -> JobProspect | None:
    """Get a prospect by its ID."""
    cursor = conn.execute("SELECT * FROM job_prospects WHERE id = ?", (prospect_id,))
    row = cursor.fetchone()
    if row is None:
        return None
    return _row_to_prospect(row)


def get_prospect_by_url(conn: sqlite3.Connection, url: str) -> JobProspect | None:
    """Get a prospect by its URL."""
    cursor = conn.execute("SELECT * FROM job_prospects WHERE url = ?", (url,))
    row = cursor.fetchone()
    if row is None:
        return None
    return _row_to_prospect(row)


def list_prospects(
    conn: sqlite3.Connection, status: ProspectStatus | None = None
) -> list[JobProspect]:
    """List all prospects, optionally filtered by status."""
    if status is not None:
        cursor = conn.execute(
            "SELECT * FROM job_prospects WHERE status = ? ORDER BY quick_score DESC",
            (status.value,),
        )
    else:
        cursor = conn.execute(
            "SELECT * FROM job_prospects ORDER BY quick_score DESC"
        )

    return [_row_to_prospect(row) for row in cursor.fetchall()]


def update_prospect(
    conn: sqlite3.Connection, prospect_id: int, update: ProspectUpdate
) -> JobProspect | None:
    """Update a prospect's status."""
    existing = get_prospect(conn, prospect_id)
    if existing is None:
        return None

    updates = []
    values = []

    if update.status is not None:
        updates.append("status = ?")
        values.append(update.status.value)

    if update.job_id is not None:
        updates.append("job_id = ?")
        values.append(update.job_id)

    if not updates:
        return existing

    values.append(prospect_id)

    conn.execute(
        f"UPDATE job_prospects SET {', '.join(updates)} WHERE id = ?",
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


def track_prospect(conn: sqlite3.Connection, prospect_id: int) -> Job | None:
    """Move a prospect to the jobs tracker.

    Creates a new job from the prospect and marks the prospect as tracked.
    """
    prospect = get_prospect(conn, prospect_id)
    if prospect is None:
        return None

    job = add_job(
        conn,
        JobCreate(
            url=prospect.url,
            title=prospect.title,
            company=prospect.company,
            location=prospect.location,
            notes=f"Quick score: {prospect.quick_score}",
        ),
    )

    update_prospect(
        conn,
        prospect_id,
        ProspectUpdate(status=ProspectStatus.TRACKED, job_id=job.id),
    )

    return job


def count_prospects_by_status(conn: sqlite3.Connection) -> dict[str, int]:
    """Get counts of prospects by status."""
    cursor = conn.execute(
        "SELECT status, COUNT(*) as count FROM job_prospects GROUP BY status"
    )
    return {row["status"]: row["count"] for row in cursor.fetchall()}


def prospect_exists_by_external_id(
    conn: sqlite3.Connection, source: str, external_id: str
) -> bool:
    """Check if a prospect with this external_id already exists for this source."""
    cursor = conn.execute(
        "SELECT 1 FROM job_prospects WHERE source = ? AND external_id = ?",
        (source, external_id),
    )
    return cursor.fetchone() is not None


def get_known_external_ids(conn: sqlite3.Connection, source: str) -> set[str]:
    """Get all known external IDs for a source (for batch checking)."""
    cursor = conn.execute(
        "SELECT external_id FROM job_prospects WHERE source = ? AND external_id IS NOT NULL",
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
        conn.execute("SELECT * FROM scrape_history WHERE id = ?", (cursor.lastrowid,)).fetchone()
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
