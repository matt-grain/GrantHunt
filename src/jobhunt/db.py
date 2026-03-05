import sqlite3
from datetime import datetime
from pathlib import Path

from jobhunt.models import Job, JobCreate, JobStatus, JobUpdate


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

    conn = sqlite3.connect(path)
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
