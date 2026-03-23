import asyncio
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from granthunt.application import generate_loi
from granthunt.config import load_profile
from granthunt.db import (
    add_grant,
    add_prospect,
    count_prospects_by_status,
    delete_grant,
    dismiss_prospect,
    get_grant,
    get_last_scrape,
    get_prospect,
    init_db,
    list_grants,
    list_prospects,
    list_scrape_history,
    track_prospect,
    update_grant,
)
from granthunt.matcher import score_grant
from granthunt.models import (
    GrantCreate,
    GrantStatus,
    GrantUpdate,
    ProspectCreate,
    ProspectStatus,
)
from granthunt.research import research_organization
from granthunt.scraper import fetch_grant_posting

app = typer.Typer(help="Grant search and application tracking CLI")
console = Console()

STATUS_COLORS = {
    GrantStatus.DISCOVERED: "blue",
    GrantStatus.EVALUATING: "cyan",
    GrantStatus.PREPARING: "yellow",
    GrantStatus.SUBMITTED: "magenta",
    GrantStatus.UNDER_REVIEW: "green",
    GrantStatus.APPROVED: "bright_green",
    GrantStatus.REJECTED: "red",
    GrantStatus.WITHDRAWN: "dim",
}

PROSPECT_COLORS = {
    ProspectStatus.PENDING: "yellow",
    ProspectStatus.DISMISSED: "dim",
    ProspectStatus.TRACKED: "green",
}


@app.command()
def add(
    url: str,
    title: Annotated[str, typer.Option("--title", "-t", help="Grant title")],
    organization: Annotated[
        str, typer.Option("--organization", "-o", help="Granting organization name")
    ],
    deadline: Annotated[
        str | None,
        typer.Option("--deadline", "-d", help="Application deadline (YYYY-MM-DD)"),
    ] = None,
    amount_min: Annotated[
        float | None,
        typer.Option("--amount-min", help="Minimum grant amount"),
    ] = None,
    amount_max: Annotated[
        float | None,
        typer.Option("--amount-max", help="Maximum grant amount"),
    ] = None,
    grant_type: Annotated[
        str | None,
        typer.Option("--grant-type", "-g", help="Grant type (e.g. R&D, Commercialization)"),
    ] = None,
    location: Annotated[
        str | None, typer.Option("--location", "-l", help="Grant location/eligibility region")
    ] = None,
    notes: Annotated[
        str | None, typer.Option("--notes", "-n", help="Notes about this grant")
    ] = None,
) -> None:
    """Add a new grant to the tracker."""
    deadline_dt = None
    if deadline:
        try:
            deadline_dt = datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            console.print(f"[red]Invalid deadline format:[/red] {deadline} (expected YYYY-MM-DD)")
            raise typer.Exit(1)

    conn = init_db()
    grant_data = GrantCreate(
        url=url,
        title=title,
        organization=organization,
        deadline=deadline_dt,
        amount_min=amount_min,
        amount_max=amount_max,
        grant_type=grant_type,
        location=location,
        notes=notes,
    )
    grant = add_grant(conn, grant_data)
    conn.close()

    console.print(
        f"[green]Added grant:[/green] {grant.title} from {grant.organization} (ID: {grant.id})"
    )


@app.command("list")
def list_cmd(
    status: Annotated[
        str | None,
        typer.Option(
            "--status",
            "-s",
            help="Filter by status (DISCOVERED, EVALUATING, PREPARING, etc.)",
        ),
    ] = None,
    all_grants: Annotated[
        bool,
        typer.Option(
            "--all", "-a", help="Show all grants including REJECTED and WITHDRAWN"
        ),
    ] = False,
) -> None:
    """List grants in your pipeline."""
    conn = init_db()

    if status:
        try:
            status_enum = GrantStatus(status.upper())
        except ValueError:
            console.print(f"[red]Invalid status:[/red] {status}")
            console.print(f"Valid statuses: {', '.join(s.value for s in GrantStatus)}")
            raise typer.Exit(1)
        grants = list_grants(conn, status_enum)
    else:
        grants = list_grants(conn)
        if not all_grants:
            grants = [
                g
                for g in grants
                if g.status not in (GrantStatus.REJECTED, GrantStatus.WITHDRAWN)
            ]

    conn.close()

    if not grants:
        console.print("[dim]No grants found.[/dim]")
        return

    table = Table(title="Grant Pipeline")
    table.add_column("ID", style="dim", width=4)
    table.add_column("Title", width=25)
    table.add_column("Organization", width=20)
    table.add_column("Status", width=13)
    table.add_column("Deadline", width=12)
    table.add_column("Score", width=6)
    table.add_column("Updated", width=12)

    for grant in grants:
        status_color = STATUS_COLORS.get(grant.status, "white")
        score_str = f"{grant.score:.1f}" if grant.score is not None else "-"
        date_str = grant.date_updated.strftime("%Y-%m-%d")
        deadline_str = grant.deadline.strftime("%Y-%m-%d") if grant.deadline else "-"

        table.add_row(
            str(grant.id),
            grant.title,
            grant.organization,
            f"[{status_color}]{grant.status.value}[/{status_color}]",
            deadline_str,
            score_str,
            date_str,
        )

    console.print(table)


@app.command()
def show(grant_id: int) -> None:
    """Show details for a specific grant."""
    conn = init_db()
    grant = get_grant(conn, grant_id)
    conn.close()

    if grant is None:
        console.print(f"[red]Grant not found:[/red] ID {grant_id}")
        raise typer.Exit(1)

    status_color = STATUS_COLORS.get(grant.status, "white")

    amount_parts = []
    if grant.amount_min is not None:
        amount_parts.append(f"${grant.amount_min:,.0f}")
    if grant.amount_max is not None:
        amount_parts.append(f"${grant.amount_max:,.0f}")
    amount_str = " – ".join(amount_parts) if amount_parts else "Not specified"

    content = f"""[bold]Title:[/bold] {grant.title}
[bold]Organization:[/bold] {grant.organization}
[bold]Grant Type:[/bold] {grant.grant_type or "Not specified"}
[bold]Location:[/bold] {grant.location or "Not specified"}
[bold]Deadline:[/bold] {grant.deadline.strftime("%Y-%m-%d") if grant.deadline else "Not specified"}
[bold]Amount Range:[/bold] {amount_str}
[bold]Status:[/bold] [{status_color}]{grant.status.value}[/{status_color}]
[bold]Score:[/bold] {grant.score if grant.score is not None else "Not scored"}
[bold]URL:[/bold] {grant.url}
[bold]Added:[/bold] {grant.date_added.strftime("%Y-%m-%d %H:%M")}
[bold]Updated:[/bold] {grant.date_updated.strftime("%Y-%m-%d %H:%M")}

[bold]Notes:[/bold]
{grant.notes or "No notes"}"""

    panel = Panel(content, title=f"Grant #{grant.id}", expand=False)
    console.print(panel)


@app.command()
def update(
    grant_id: int,
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
    deadline: Annotated[
        str | None,
        typer.Option("--deadline", "-d", help="Application deadline (YYYY-MM-DD)"),
    ] = None,
) -> None:
    """Update a grant's status, notes, score, or deadline."""
    if status is None and notes is None and score is None and deadline is None:
        console.print(
            "[yellow]Nothing to update. Use --status, --notes, --score, or --deadline.[/yellow]"
        )
        raise typer.Exit(1)

    conn = init_db()

    status_enum = None
    if status:
        try:
            status_enum = GrantStatus(status.upper())
        except ValueError:
            console.print(f"[red]Invalid status:[/red] {status}")
            console.print(f"Valid statuses: {', '.join(s.value for s in GrantStatus)}")
            conn.close()
            raise typer.Exit(1)

    deadline_dt = None
    if deadline:
        try:
            deadline_dt = datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            console.print(f"[red]Invalid deadline format:[/red] {deadline} (expected YYYY-MM-DD)")
            conn.close()
            raise typer.Exit(1)

    grant_update = GrantUpdate(
        status=status_enum, notes=notes, score=score, deadline=deadline_dt
    )
    grant = update_grant(conn, grant_id, grant_update)
    conn.close()

    if grant is None:
        console.print(f"[red]Grant not found:[/red] ID {grant_id}")
        raise typer.Exit(1)

    console.print(
        f"[green]Updated grant {grant_id}:[/green] {grant.title} from {grant.organization}"
    )
    if status:
        console.print(f"  Status: {grant.status.value}")
    if notes:
        console.print(f"  Notes: {notes[:50]}{'...' if len(notes) > 50 else ''}")
    if score is not None:
        console.print(f"  Score: {score}")
    if deadline:
        console.print(f"  Deadline: {deadline}")


@app.command()
def delete(grant_id: int) -> None:
    """Delete a grant from the tracker."""
    conn = init_db()
    grant = get_grant(conn, grant_id)

    if grant is None:
        console.print(f"[red]Grant not found:[/red] ID {grant_id}")
        conn.close()
        raise typer.Exit(1)

    if not typer.confirm(f"Delete '{grant.title}' from {grant.organization}?"):
        console.print("[dim]Cancelled.[/dim]")
        conn.close()
        raise typer.Exit(0)

    delete_grant(conn, grant_id)
    conn.close()
    console.print(f"[green]Deleted grant {grant_id}.[/green]")


@app.command()
def stats() -> None:
    """Show pipeline statistics."""
    conn = init_db()
    grants = list_grants(conn)
    conn.close()

    if not grants:
        console.print("[dim]No grants in pipeline.[/dim]")
        return

    status_counts: dict[GrantStatus, int] = {}
    for grant in grants:
        status_counts[grant.status] = status_counts.get(grant.status, 0) + 1

    table = Table(title="Grant Pipeline Statistics")
    table.add_column("Status", width=15)
    table.add_column("Count", width=8, justify="right")

    for status in GrantStatus:
        count = status_counts.get(status, 0)
        if count > 0:
            color = STATUS_COLORS.get(status, "white")
            table.add_row(f"[{color}]{status.value}[/{color}]", str(count))

    table.add_row("[bold]Total[/bold]", f"[bold]{len(grants)}[/bold]")

    console.print(table)


@app.command()
def match(
    url: str,
    add_to_tracker: Annotated[
        bool,
        typer.Option("--add", "-a", help="Add to tracker after matching"),
    ] = False,
) -> None:
    """Analyze a grant posting and score it against your profile."""
    console.print("[dim]Fetching grant posting...[/dim]")

    try:
        grant_data = asyncio.run(fetch_grant_posting(url))
    except Exception as e:
        console.print(f"[red]Error fetching grant:[/red] {e}")
        raise typer.Exit(1) from None

    console.print("[dim]Analyzing match...[/dim]")

    try:
        profile = load_profile()
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None

    result = score_grant(grant_data, profile)

    if result.overall_score >= 70:
        score_color = "green"
    elif result.overall_score >= 50:
        score_color = "yellow"
    else:
        score_color = "red"

    amount_parts = []
    if grant_data.amount_min is not None:
        amount_parts.append(f"${grant_data.amount_min:,.0f}")
    if grant_data.amount_max is not None:
        amount_parts.append(f"${grant_data.amount_max:,.0f}")
    amount_str = " – ".join(amount_parts) if amount_parts else "Not specified"

    deadline_str = (
        grant_data.deadline.strftime("%Y-%m-%d")
        if grant_data.deadline is not None
        else "Not specified"
    )

    content = f"""[bold]Title:[/bold] {grant_data.title}
[bold]Organization:[/bold] {grant_data.organization}
[bold]Grant Type:[/bold] {grant_data.grant_type or "Not specified"}
[bold]Deadline:[/bold] {deadline_str}
[bold]Amount Range:[/bold] {amount_str}

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

    panel = Panel(content, title="Grant Match Analysis", expand=False)
    console.print(panel)

    should_add = add_to_tracker
    if not should_add and result.overall_score >= 50:
        should_add = typer.confirm("\nAdd this grant to your tracker?")

    if should_add:
        conn = init_db()
        grant_create = GrantCreate(
            url=url,
            title=grant_data.title,
            organization=grant_data.organization,
            location=grant_data.location,
            grant_type=grant_data.grant_type,
            deadline=grant_data.deadline,
            amount_min=grant_data.amount_min,
            amount_max=grant_data.amount_max,
            notes=f"Score: {result.overall_score}/100 - {result.recommendation}",
        )
        grant = add_grant(conn, grant_create)
        update_grant(conn, grant.id, GrantUpdate(score=result.overall_score))
        conn.close()
        console.print(
            f"[green]Added to tracker:[/green] {grant.title} from {grant.organization} (ID: {grant.id})"
        )


@app.command()
def research(grant_id: int) -> None:
    """Research an organization from a tracked grant."""
    conn = init_db()
    grant = get_grant(conn, grant_id)
    conn.close()

    if grant is None:
        console.print(f"[red]Grant not found:[/red] ID {grant_id}")
        raise typer.Exit(1)

    console.print(f"[dim]Researching {grant.organization}...[/dim]")

    try:
        result = asyncio.run(research_organization(grant.organization))
    except Exception as e:
        console.print(f"[red]Error researching organization:[/red] {e}")
        raise typer.Exit(1) from None

    content = f"""[bold]Organization:[/bold] {result.name}
[bold]Website:[/bold] {result.website or "Not found"}
[bold]Industry:[/bold] {result.industry or "Unknown"}
[bold]Size:[/bold] {result.size or "Unknown"}

[bold]Description:[/bold]
{result.description or "No description available"}"""

    if result.programs:
        content += "\n\n[bold cyan]Grant Programs:[/bold cyan]"
        for program in result.programs:
            content += f"\n  - {program}"

    if result.funding_signals:
        content += "\n\n[bold green]Funding Signals:[/bold green]"
        for signal in result.funding_signals:
            content += f"\n  + {signal}"

    if result.application_tips:
        content += "\n\n[bold yellow]Application Tips:[/bold yellow]"
        for i, tip in enumerate(result.application_tips, 1):
            content += f"\n  {i}. {tip}"

    panel = Panel(
        content, title=f"Organization Research: {grant.organization}", expand=False
    )
    console.print(panel)


@app.command("apply")
def apply_cmd(
    grant_id: int,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Save to file instead of displaying"),
    ] = None,
    research_file: Annotated[
        Path | None,
        typer.Option(
            "--research", "-r", help="Path to research.md for personalization"
        ),
    ] = None,
) -> None:
    """Generate a Letter of Intent (LOI) for a tracked grant."""
    conn = init_db()
    grant = get_grant(conn, grant_id)
    conn.close()

    if grant is None:
        console.print(f"[red]Grant not found:[/red] ID {grant_id}")
        raise typer.Exit(1)

    console.print(
        f"[dim]Generating LOI for {grant.title} from {grant.organization}...[/dim]"
    )

    # Auto-detect research file if not provided
    if research_file is None:
        possible_research = list(Path("applications").glob(f"{grant_id}-*/research.md"))
        if possible_research:
            research_file = possible_research[0]
            console.print(f"[dim]Using research from: {research_file}[/dim]")

    try:
        loi = generate_loi(grant, output, research_file)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Error generating LOI:[/red] {e}")
        raise typer.Exit(1) from None

    if output:
        console.print(f"[green]LOI saved to:[/green] {output}")
    else:
        console.print()
        console.print(Panel(loi, title="Letter of Intent Draft", expand=False))
        console.print()
        console.print("[dim]Tip: Use --output FILE to save to a file[/dim]")


@app.command()
def prospects(
    status: Annotated[
        str | None,
        typer.Option(
            "--status", "-s", help="Filter by status (PENDING, DISMISSED, TRACKED)"
        ),
    ] = None,
    pending_only: Annotated[
        bool,
        typer.Option("--pending", "-p", help="Show only pending prospects"),
    ] = False,
) -> None:
    """List discovered grant prospects awaiting review."""
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
    console.print(f"\n[bold]Grant Prospects[/bold] ({pending_count} pending review)\n")

    table = Table()
    table.add_column("ID", style="dim", width=4)
    table.add_column("Score", width=6, justify="right")
    table.add_column("Title", width=30)
    table.add_column("Organization", width=20)
    table.add_column("Amount Range", width=18)
    table.add_column("Location", width=15)
    table.add_column("Status", width=10)

    for p in prospects_list:
        score_str = f"{p.quick_score:.0f}" if p.quick_score else "-"
        score_color = (
            "green"
            if (p.quick_score or 0) >= 80
            else ("yellow" if (p.quick_score or 0) >= 60 else "white")
        )
        status_color = PROSPECT_COLORS.get(p.status, "white")

        table.add_row(
            str(p.id),
            f"[{score_color}]{score_str}[/{score_color}]",
            p.title[:30],
            p.organization[:20],
            (p.amount_range or "-")[:18],
            (p.location or "-")[:15],
            f"[{status_color}]{p.status.value}[/{status_color}]",
        )

    console.print(table)
    console.print(
        "\n[dim]Use 'granthunt track <ID>' or 'granthunt dismiss <ID>' to process[/dim]"
    )


@app.command("track")
def track_cmd(
    prospect_id: int,
) -> None:
    """Move a prospect to your grant tracker."""
    conn = init_db()
    prospect = get_prospect(conn, prospect_id)

    if prospect is None:
        console.print(f"[red]Prospect not found:[/red] ID {prospect_id}")
        conn.close()
        raise typer.Exit(1)

    if prospect.status == ProspectStatus.TRACKED:
        console.print(
            f"[yellow]Already tracked:[/yellow] {prospect.title} from {prospect.organization}"
        )
        conn.close()
        raise typer.Exit(0)

    grant = track_prospect(conn, prospect_id)
    conn.close()

    if grant:
        console.print(
            f"[green]Tracked:[/green] {grant.title} from {grant.organization} (Grant ID: {grant.id})"
        )
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
        console.print(
            f"[dim]Already dismissed:[/dim] {prospect.title} from {prospect.organization}"
        )
        conn.close()
        raise typer.Exit(0)

    dismiss_prospect(conn, prospect_id)
    conn.close()
    console.print(f"[dim]Dismissed:[/dim] {prospect.title} from {prospect.organization}")


@app.command("review")
def review_cmd() -> None:
    """Interactive review of pending grant prospects."""
    conn = init_db()
    pending = list_prospects(conn, ProspectStatus.PENDING)

    if not pending:
        console.print("[dim]No pending prospects to review.[/dim]")
        conn.close()
        return

    console.print(f"\n[bold]Review {len(pending)} Grant Prospects[/bold]")
    console.print("[dim]Commands: t=track, d=dismiss, s=skip, q=quit[/dim]\n")

    tracked = 0
    dismissed = 0

    for p in pending:
        score_str = f"{p.quick_score:.0f}" if p.quick_score else "?"
        score_color = (
            "green"
            if (p.quick_score or 0) >= 80
            else ("yellow" if (p.quick_score or 0) >= 60 else "white")
        )

        console.print(
            f"[{score_color}][{score_str}][/{score_color}] [bold]{p.title}[/bold]"
        )
        console.print(
            f"    {p.organization} · {p.location or 'Location unknown'}"
            + (f" · {p.amount_range}" if p.amount_range else "")
        )
        console.print(f"    [dim]{p.url}[/dim]")

        while True:
            action = typer.prompt("Action", default="s").lower().strip()

            if action == "t":
                grant = track_prospect(conn, p.id)
                if grant:
                    console.print(f"  [green]Tracked (Grant #{grant.id})[/green]\n")
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
                console.print(
                    f"\n[bold]Summary:[/bold] {tracked} tracked, {dismissed} dismissed"
                )
                conn.close()
                return
            else:
                console.print("  [red]Unknown action. Use t/d/s/q[/red]")

    conn.close()
    console.print(f"\n[bold]Done![/bold] {tracked} tracked, {dismissed} dismissed")


@app.command("add-prospect")
def add_prospect_cmd(
    url: str,
    title: Annotated[str, typer.Option("--title", "-t", help="Grant title")],
    organization: Annotated[
        str, typer.Option("--organization", "-o", help="Granting organization name")
    ],
    location: Annotated[
        str | None, typer.Option("--location", "-l", help="Grant location/eligibility region")
    ] = None,
    amount_range: Annotated[
        str | None, typer.Option("--amount-range", help="Amount range (e.g. '$10K–$50K')")
    ] = None,
    score: Annotated[
        float | None, typer.Option("--score", "-s", help="Quick score (0-100)")
    ] = None,
    source: Annotated[
        str, typer.Option("--source", help="Source (innovation_canada, nrc, etc.)")
    ] = "innovation_canada",
) -> None:
    """Add a grant prospect manually."""
    conn = init_db()
    prospect = add_prospect(
        conn,
        ProspectCreate(
            url=url,
            title=title,
            organization=organization,
            location=location,
            amount_range=amount_range,
            quick_score=score,
            source=source,
        ),
    )
    conn.close()

    console.print(
        f"[green]Added prospect:[/green] {prospect.title} from {prospect.organization} (ID: {prospect.id})"
    )


@app.command("scrape-history")
def scrape_history_cmd(
    source: Annotated[
        str | None,
        typer.Option(
            "--source", "-s", help="Filter by source (innovation_canada, nrc, etc.)"
        ),
    ] = None,
    limit: Annotated[
        int,
        typer.Option("--limit", "-n", help="Number of entries to show"),
    ] = 10,
) -> None:
    """Show scrape history for grant sources."""
    conn = init_db()
    history = list_scrape_history(conn, source, limit)

    if not history:
        console.print("[dim]No scrape history found.[/dim]")
        conn.close()
        return

    table = Table(title="Scrape History")
    table.add_column("Source", width=20)
    table.add_column("Query", width=25)
    table.add_column("Date", width=18)
    table.add_column("Found", width=6, justify="right")
    table.add_column("New", width=5, justify="right")

    for h in history:
        table.add_row(
            h.source,
            (h.query or "-")[:25],
            h.scraped_at.strftime("%Y-%m-%d %H:%M"),
            str(h.jobs_found),
            str(h.new_jobs),
        )

    console.print(table)

    # Show last scrape per source
    if not source:
        console.print("\n[bold]Last scrape per source:[/bold]")
        sources = set(h.source for h in history)
        for src in sorted(sources):
            last = get_last_scrape(conn, src)
            if last:
                ago = (datetime.now() - last.scraped_at).days
                console.print(f"  {src}: {ago}d ago ({last.new_jobs} new grants)")

    conn.close()


@app.command()
def serve(
    host: str = "127.0.0.1",
    port: int = 8888,
    reload: bool = False,
) -> None:
    """Start the GrantHunt web dashboard server."""
    import uvicorn

    console.print(
        f"[green]Starting GrantHunt dashboard at http://{host}:{port}[/green]"
    )
    uvicorn.run(
        "granthunt.web.app:create_app",
        host=host,
        port=port,
        reload=reload,
        factory=True,
    )


if __name__ == "__main__":
    app()
