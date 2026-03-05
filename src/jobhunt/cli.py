import asyncio
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from jobhunt.config import load_profile
from jobhunt.cover_letter import generate_cover_letter
from jobhunt.db import (
    add_job,
    add_prospect,
    count_prospects_by_status,
    delete_job,
    dismiss_prospect,
    get_job,
    get_prospect,
    init_db,
    list_jobs,
    list_prospects,
    track_prospect,
    update_job,
)
from jobhunt.matcher import score_job
from jobhunt.models import JobCreate, JobStatus, JobUpdate, ProspectCreate, ProspectStatus
from jobhunt.research import research_company
from jobhunt.scraper import fetch_job_posting

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

PROSPECT_COLORS = {
    ProspectStatus.PENDING: "yellow",
    ProspectStatus.DISMISSED: "dim",
    ProspectStatus.TRACKED: "green",
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


@app.command()
def match(
    url: str,
    add_to_tracker: Annotated[
        bool,
        typer.Option("--add", "-a", help="Add to tracker after matching"),
    ] = False,
) -> None:
    """Analyze a job posting and score it against your profile."""
    console.print("[dim]Fetching job posting...[/dim]")

    try:
        job_data = asyncio.run(fetch_job_posting(url))
    except Exception as e:
        console.print(f"[red]Error fetching job:[/red] {e}")
        raise typer.Exit(1) from None

    console.print("[dim]Analyzing match...[/dim]")

    try:
        profile = load_profile()
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None

    result = score_job(job_data, profile)

    if result.overall_score >= 70:
        score_color = "green"
    elif result.overall_score >= 50:
        score_color = "yellow"
    else:
        score_color = "red"

    remote_str = job_data.remote if job_data.remote is not None else "Unknown"
    content = f"""[bold]Title:[/bold] {job_data.title}
[bold]Company:[/bold] {job_data.company}
[bold]Location:[/bold] {job_data.location}
[bold]Remote:[/bold] {remote_str}
[bold]Salary:[/bold] {job_data.salary or 'Not specified'}

[bold]Overall Score:[/bold] [{score_color}]{result.overall_score}/100[/{score_color}]
[bold]Recommendation:[/bold] [{score_color}]{result.recommendation}[/{score_color}]

[bold]Breakdown:[/bold]"""

    for category, score in result.breakdown.items():
        cat_color = "green" if score >= 70 else ("yellow" if score >= 50 else "red")
        content += f"\n  {category}: [{cat_color}]{score}%[/{cat_color}]"

    if result.highlights:
        content += "\n\n[bold green]Highlights:[/bold green]"
        for hl in result.highlights:
            content += f"\n  [green]+[/green] {hl}"

    if result.red_flags:
        content += "\n\n[bold red]Red Flags:[/bold red]"
        for rf in result.red_flags:
            content += f"\n  [red]![/red] {rf}"

    panel = Panel(content, title="Job Match Analysis", expand=False)
    console.print(panel)

    should_add = add_to_tracker
    if not should_add and result.overall_score >= 50:
        should_add = typer.confirm("\nAdd this job to your tracker?")

    if should_add:
        conn = init_db()
        job_create = JobCreate(
            url=url,
            title=job_data.title,
            company=job_data.company,
            location=job_data.location,
            notes=f"Score: {result.overall_score}/100 - {result.recommendation}",
        )
        job = add_job(conn, job_create)
        update_job(conn, job.id, JobUpdate(score=result.overall_score))
        conn.close()
        console.print(
            f"[green]Added to tracker:[/green] {job.title} at {job.company} (ID: {job.id})"
        )


@app.command()
def research(job_id: int) -> None:
    """Research a company from a tracked job."""
    conn = init_db()
    job = get_job(conn, job_id)
    conn.close()

    if job is None:
        console.print(f"[red]Job not found:[/red] ID {job_id}")
        raise typer.Exit(1)

    console.print(f"[dim]Researching {job.company}...[/dim]")

    try:
        result = asyncio.run(research_company(job.company))
    except Exception as e:
        console.print(f"[red]Error researching company:[/red] {e}")
        raise typer.Exit(1) from None

    # Build output
    content = f"""[bold]Company:[/bold] {result.name}
[bold]Website:[/bold] {result.website or 'Not found'}
[bold]Industry:[/bold] {result.industry or 'Unknown'}
[bold]Size:[/bold] {result.size or 'Unknown'}

[bold]Description:[/bold]
{result.description or 'No description available'}"""

    if result.tech_stack:
        content += "\n\n[bold cyan]Tech Stack:[/bold cyan]"
        for tech in result.tech_stack:
            content += f"\n  - {tech}"

    if result.culture_signals:
        content += "\n\n[bold green]Culture Signals:[/bold green]"
        for signal in result.culture_signals:
            content += f"\n  + {signal}"

    if result.interview_prep:
        content += "\n\n[bold yellow]Interview Questions to Ask:[/bold yellow]"
        for i, question in enumerate(result.interview_prep, 1):
            content += f"\n  {i}. {question}"

    panel = Panel(content, title=f"Company Research: {job.company}", expand=False)
    console.print(panel)


@app.command("cover-letter")
def cover_letter_cmd(
    job_id: int,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Save to file instead of displaying"),
    ] = None,
    research: Annotated[
        Path | None,
        typer.Option("--research", "-r", help="Path to research.md for personalization"),
    ] = None,
) -> None:
    """Generate a cover letter for a tracked job."""
    conn = init_db()
    job = get_job(conn, job_id)
    conn.close()

    if job is None:
        console.print(f"[red]Job not found:[/red] ID {job_id}")
        raise typer.Exit(1)

    console.print(
        f"[dim]Generating cover letter for {job.title} at {job.company}...[/dim]"
    )

    # Auto-detect research file if not provided
    if research is None:
        # Check applications folder for research.md
        possible_research = list(Path("applications").glob(f"{job_id}-*/research.md"))
        if possible_research:
            research = possible_research[0]
            console.print(f"[dim]Using research from: {research}[/dim]")

    try:
        letter = generate_cover_letter(job, output, research)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Error generating cover letter:[/red] {e}")
        raise typer.Exit(1) from None

    if output:
        console.print(f"[green]Cover letter saved to:[/green] {output}")
    else:
        console.print()
        console.print(Panel(letter, title="Cover Letter Draft", expand=False))
        console.print()
        console.print("[dim]Tip: Use --output FILE to save to a file[/dim]")


@app.command()
def prospects(
    status: Annotated[
        str | None,
        typer.Option("--status", "-s", help="Filter by status (PENDING, DISMISSED, TRACKED)"),
    ] = None,
    pending_only: Annotated[
        bool,
        typer.Option("--pending", "-p", help="Show only pending prospects"),
    ] = False,
) -> None:
    """List discovered job prospects awaiting review."""
    conn = init_db()

    if pending_only:
        status_filter = ProspectStatus.PENDING
    elif status:
        try:
            status_filter = ProspectStatus(status.upper())
        except ValueError:
            console.print(f"[red]Invalid status:[/red] {status}")
            console.print(f"Valid: {', '.join(s.value for s in ProspectStatus)}")
            raise typer.Exit(1)
    else:
        status_filter = None

    prospects_list = list_prospects(conn, status_filter)
    counts = count_prospects_by_status(conn)
    conn.close()

    if not prospects_list:
        console.print("[dim]No prospects found.[/dim]")
        return

    pending_count = counts.get("PENDING", 0)
    console.print(f"\n[bold]Job Prospects[/bold] ({pending_count} pending review)\n")

    table = Table()
    table.add_column("ID", style="dim", width=4)
    table.add_column("Score", width=6, justify="right")
    table.add_column("Title", width=30)
    table.add_column("Company", width=20)
    table.add_column("Location", width=15)
    table.add_column("Status", width=10)

    for p in prospects_list:
        score_str = f"{p.quick_score:.0f}" if p.quick_score else "-"
        score_color = "green" if (p.quick_score or 0) >= 80 else ("yellow" if (p.quick_score or 0) >= 60 else "white")
        status_color = PROSPECT_COLORS.get(p.status, "white")

        table.add_row(
            str(p.id),
            f"[{score_color}]{score_str}[/{score_color}]",
            p.title[:30],
            p.company[:20],
            (p.location or "-")[:15],
            f"[{status_color}]{p.status.value}[/{status_color}]",
        )

    console.print(table)
    console.print("\n[dim]Use 'jobhunt track <ID>' or 'jobhunt dismiss <ID>' to process[/dim]")


@app.command("track")
def track_cmd(
    prospect_id: int,
) -> None:
    """Move a prospect to your job tracker."""
    conn = init_db()
    prospect = get_prospect(conn, prospect_id)

    if prospect is None:
        console.print(f"[red]Prospect not found:[/red] ID {prospect_id}")
        conn.close()
        raise typer.Exit(1)

    if prospect.status == ProspectStatus.TRACKED:
        console.print(f"[yellow]Already tracked:[/yellow] {prospect.title} at {prospect.company}")
        conn.close()
        raise typer.Exit(0)

    job = track_prospect(conn, prospect_id)
    conn.close()

    if job:
        console.print(f"[green]Tracked:[/green] {job.title} at {job.company} (Job ID: {job.id})")
    else:
        console.print("[red]Failed to track prospect[/red]")
        raise typer.Exit(1)


@app.command("dismiss")
def dismiss_cmd(
    prospect_id: int,
) -> None:
    """Dismiss a prospect (not interested)."""
    conn = init_db()
    prospect = get_prospect(conn, prospect_id)

    if prospect is None:
        console.print(f"[red]Prospect not found:[/red] ID {prospect_id}")
        conn.close()
        raise typer.Exit(1)

    if prospect.status == ProspectStatus.DISMISSED:
        console.print(f"[dim]Already dismissed:[/dim] {prospect.title} at {prospect.company}")
        conn.close()
        raise typer.Exit(0)

    dismiss_prospect(conn, prospect_id)
    conn.close()
    console.print(f"[dim]Dismissed:[/dim] {prospect.title} at {prospect.company}")


@app.command("review")
def review_cmd() -> None:
    """Interactive review of pending prospects."""
    conn = init_db()
    pending = list_prospects(conn, ProspectStatus.PENDING)

    if not pending:
        console.print("[dim]No pending prospects to review.[/dim]")
        conn.close()
        return

    console.print(f"\n[bold]Review {len(pending)} Prospects[/bold]")
    console.print("[dim]Commands: t=track, d=dismiss, s=skip, q=quit[/dim]\n")

    tracked = 0
    dismissed = 0

    for p in pending:
        score_str = f"{p.quick_score:.0f}" if p.quick_score else "?"
        score_color = "green" if (p.quick_score or 0) >= 80 else ("yellow" if (p.quick_score or 0) >= 60 else "white")

        console.print(f"[{score_color}][{score_str}][/{score_color}] [bold]{p.title}[/bold]")
        console.print(f"    {p.company} · {p.location or 'Location unknown'}")
        console.print(f"    [dim]{p.url}[/dim]")

        while True:
            action = typer.prompt("Action", default="s").lower().strip()

            if action == "t":
                job = track_prospect(conn, p.id)
                if job:
                    console.print(f"  [green]Tracked (Job #{job.id})[/green]\n")
                    tracked += 1
                break
            elif action == "d":
                dismiss_prospect(conn, p.id)
                console.print("  [dim]Dismissed[/dim]\n")
                dismissed += 1
                break
            elif action == "s":
                console.print("  [yellow]Skipped[/yellow]\n")
                break
            elif action == "q":
                console.print(f"\n[bold]Summary:[/bold] {tracked} tracked, {dismissed} dismissed")
                conn.close()
                return
            else:
                console.print("  [red]Unknown action. Use t/d/s/q[/red]")

    conn.close()
    console.print(f"\n[bold]Done![/bold] {tracked} tracked, {dismissed} dismissed")


@app.command("add-prospect")
def add_prospect_cmd(
    url: str,
    title: Annotated[str, typer.Option("--title", "-t", help="Job title")],
    company: Annotated[str, typer.Option("--company", "-c", help="Company name")],
    location: Annotated[
        str | None, typer.Option("--location", "-l", help="Job location")
    ] = None,
    score: Annotated[
        float | None, typer.Option("--score", "-s", help="Quick score (0-100)")
    ] = None,
    source: Annotated[
        str, typer.Option("--source", help="Source (linkedin, indeed, etc.)")
    ] = "linkedin",
) -> None:
    """Add a job prospect manually."""
    conn = init_db()
    prospect = add_prospect(
        conn,
        ProspectCreate(
            url=url,
            title=title,
            company=company,
            location=location,
            quick_score=score,
            source=source,
        ),
    )
    conn.close()

    console.print(
        f"[green]Added prospect:[/green] {prospect.title} at {prospect.company} (ID: {prospect.id})"
    )


if __name__ == "__main__":
    app()
