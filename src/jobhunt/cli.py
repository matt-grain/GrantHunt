from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from jobhunt.db import (
    add_job,
    delete_job,
    get_job,
    init_db,
    list_jobs,
    update_job,
)
from jobhunt.models import JobCreate, JobStatus, JobUpdate

app = typer.Typer(help="Job search automation CLI")
console = Console()

STATUS_COLORS = {
    JobStatus.NEW: "blue",
    JobStatus.INTERESTED: "cyan",
    JobStatus.APPLIED: "yellow",
    JobStatus.INTERVIEWING: "green",
    JobStatus.OFFER: "bright_green",
    JobStatus.REJECTED: "red",
    JobStatus.WITHDRAWN: "dim",
}


@app.command()
def add(
    url: str,
    title: Annotated[str, typer.Option("--title", "-t", help="Job title")],
    company: Annotated[str, typer.Option("--company", "-c", help="Company name")],
    location: Annotated[
        str | None, typer.Option("--location", "-l", help="Job location")
    ] = None,
    notes: Annotated[
        str | None, typer.Option("--notes", "-n", help="Notes about this job")
    ] = None,
) -> None:
    """Add a new job to the tracker."""
    conn = init_db()
    job_data = JobCreate(
        url=url,
        title=title,
        company=company,
        location=location,
        notes=notes,
    )
    job = add_job(conn, job_data)
    conn.close()

    console.print(f"[green]Added job:[/green] {job.title} at {job.company} (ID: {job.id})")


@app.command("list")
def list_cmd(
    status: Annotated[
        str | None,
        typer.Option("--status", "-s", help="Filter by status (NEW, INTERESTED, APPLIED, etc.)"),
    ] = None,
    all_jobs: Annotated[
        bool,
        typer.Option("--all", "-a", help="Show all jobs including REJECTED and WITHDRAWN"),
    ] = False,
) -> None:
    """List jobs in your pipeline."""
    conn = init_db()

    if status:
        try:
            status_enum = JobStatus(status.upper())
        except ValueError:
            console.print(f"[red]Invalid status:[/red] {status}")
            console.print(f"Valid statuses: {', '.join(s.value for s in JobStatus)}")
            raise typer.Exit(1)
        jobs = list_jobs(conn, status_enum)
    else:
        jobs = list_jobs(conn)
        if not all_jobs:
            jobs = [
                j for j in jobs
                if j.status not in (JobStatus.REJECTED, JobStatus.WITHDRAWN)
            ]

    conn.close()

    if not jobs:
        console.print("[dim]No jobs found.[/dim]")
        return

    table = Table(title="Job Pipeline")
    table.add_column("ID", style="dim", width=4)
    table.add_column("Title", width=25)
    table.add_column("Company", width=20)
    table.add_column("Status", width=12)
    table.add_column("Score", width=6)
    table.add_column("Updated", width=12)

    for job in jobs:
        status_color = STATUS_COLORS.get(job.status, "white")
        score_str = f"{job.score:.1f}" if job.score is not None else "-"
        date_str = job.date_updated.strftime("%Y-%m-%d")

        table.add_row(
            str(job.id),
            job.title,
            job.company,
            f"[{status_color}]{job.status.value}[/{status_color}]",
            score_str,
            date_str,
        )

    console.print(table)


@app.command()
def show(job_id: int) -> None:
    """Show details for a specific job."""
    conn = init_db()
    job = get_job(conn, job_id)
    conn.close()

    if job is None:
        console.print(f"[red]Job not found:[/red] ID {job_id}")
        raise typer.Exit(1)

    status_color = STATUS_COLORS.get(job.status, "white")

    content = f"""[bold]Title:[/bold] {job.title}
[bold]Company:[/bold] {job.company}
[bold]Location:[/bold] {job.location or 'Not specified'}
[bold]Status:[/bold] [{status_color}]{job.status.value}[/{status_color}]
[bold]Score:[/bold] {job.score if job.score is not None else 'Not scored'}
[bold]URL:[/bold] {job.url}
[bold]Added:[/bold] {job.date_added.strftime('%Y-%m-%d %H:%M')}
[bold]Updated:[/bold] {job.date_updated.strftime('%Y-%m-%d %H:%M')}

[bold]Notes:[/bold]
{job.notes or 'No notes'}"""

    panel = Panel(content, title=f"Job #{job.id}", expand=False)
    console.print(panel)


@app.command()
def update(
    job_id: int,
    status: Annotated[
        str | None,
        typer.Option("--status", "-s", help="New status"),
    ] = None,
    notes: Annotated[
        str | None,
        typer.Option("--notes", "-n", help="Notes to add/update"),
    ] = None,
    score: Annotated[
        float | None,
        typer.Option("--score", help="Match score (0-100)"),
    ] = None,
) -> None:
    """Update a job's status, notes, or score."""
    if status is None and notes is None and score is None:
        console.print("[yellow]Nothing to update. Use --status, --notes, or --score.[/yellow]")
        raise typer.Exit(1)

    conn = init_db()

    status_enum = None
    if status:
        try:
            status_enum = JobStatus(status.upper())
        except ValueError:
            console.print(f"[red]Invalid status:[/red] {status}")
            console.print(f"Valid statuses: {', '.join(s.value for s in JobStatus)}")
            conn.close()
            raise typer.Exit(1)

    job_update = JobUpdate(status=status_enum, notes=notes, score=score)
    job = update_job(conn, job_id, job_update)
    conn.close()

    if job is None:
        console.print(f"[red]Job not found:[/red] ID {job_id}")
        raise typer.Exit(1)

    console.print(f"[green]Updated job {job_id}:[/green] {job.title} at {job.company}")
    if status:
        console.print(f"  Status: {job.status.value}")
    if notes:
        console.print(f"  Notes: {notes[:50]}{'...' if len(notes) > 50 else ''}")
    if score is not None:
        console.print(f"  Score: {score}")


@app.command()
def delete(job_id: int) -> None:
    """Delete a job from the tracker."""
    conn = init_db()
    job = get_job(conn, job_id)

    if job is None:
        console.print(f"[red]Job not found:[/red] ID {job_id}")
        conn.close()
        raise typer.Exit(1)

    if not typer.confirm(f"Delete '{job.title}' at {job.company}?"):
        console.print("[dim]Cancelled.[/dim]")
        conn.close()
        raise typer.Exit(0)

    delete_job(conn, job_id)
    conn.close()
    console.print(f"[green]Deleted job {job_id}.[/green]")


@app.command()
def stats() -> None:
    """Show pipeline statistics."""
    conn = init_db()
    jobs = list_jobs(conn)
    conn.close()

    if not jobs:
        console.print("[dim]No jobs in pipeline.[/dim]")
        return

    status_counts: dict[JobStatus, int] = {}
    for job in jobs:
        status_counts[job.status] = status_counts.get(job.status, 0) + 1

    table = Table(title="Pipeline Statistics")
    table.add_column("Status", width=15)
    table.add_column("Count", width=8, justify="right")

    for status in JobStatus:
        count = status_counts.get(status, 0)
        if count > 0:
            color = STATUS_COLORS.get(status, "white")
            table.add_row(f"[{color}]{status.value}[/{color}]", str(count))

    table.add_row("[bold]Total[/bold]", f"[bold]{len(jobs)}[/bold]")

    console.print(table)


if __name__ == "__main__":
    app()
