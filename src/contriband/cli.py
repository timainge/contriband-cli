"""CLI entry point for contriband."""

from datetime import date as date_type
from pathlib import Path

import typer
from rich.console import Console

from contriband.config import Config, ConfigError, load_config
from contriband.git import apply_plan, get_dry_run_summary
from contriband.planner import (
    PlanLoadError,
    create_plan,
    export_plan_csv,
    export_plan_json,
    load_plan,
)
from contriband.render import render_template
from contriband.templates import TemplateError, load_template


def get_config() -> Config:
    """Load config, handling errors gracefully."""
    try:
        return load_config()
    except ConfigError as e:
        console.print(f"[yellow]Warning:[/yellow] {e}")
        return Config()

app = typer.Typer(
    name="contriband",
    help="Paint GitHub contribution grids with art.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def init(
    path: str = typer.Argument(".", help="Directory to initialize"),
) -> None:
    """Initialize a new contriband project."""
    console.print(f"[yellow]init[/yellow] not yet implemented: {path}")


@app.command()
def preview(
    template_path: str = typer.Argument(..., help="Template file to preview"),
    no_labels: bool = typer.Option(False, "--no-labels", help="Hide weekday labels"),
) -> None:
    """Preview a template in the terminal."""
    try:
        template = load_template(Path(template_path))
    except TemplateError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    render_template(template, show_labels=not no_labels, console=console)


@app.command()
def plan(
    template_path: str = typer.Argument(..., help="Template file to plan"),
    start_date: str = typer.Option(..., "--start-date", "-s", help="Start date (YYYY-MM-DD)"),
    week_start: str | None = typer.Option(None, "--week-start", "-w", help="Week start day"),
    output_dir: str = typer.Option("outputs", "--output", "-o", help="Output directory"),
) -> None:
    """Generate a commit plan from a template."""
    # Load config
    config = get_config()

    # Load template
    try:
        template = load_template(Path(template_path))
    except TemplateError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Parse start date
    try:
        parsed_date = date_type.fromisoformat(start_date)
    except ValueError:
        console.print(f"[red]Error:[/red] Invalid date format: {start_date}. Use YYYY-MM-DD.")
        raise typer.Exit(1)

    # Use CLI value or fall back to config
    effective_week_start = (week_start or config.week_start).upper()

    # Validate week start
    if effective_week_start not in ("SUNDAY", "MONDAY"):
        console.print(
            f"[red]Error:[/red] week_start must be SUNDAY or MONDAY, got {effective_week_start}"
        )
        raise typer.Exit(1)

    # Create plan
    commit_plan = create_plan(
        template, parsed_date, week_start=effective_week_start, level_mapping=config.level_mapping
    )

    # Export to files
    output_path = Path(output_dir)
    json_path = output_path / "plan.json"
    csv_path = output_path / "plan.csv"

    export_plan_json(commit_plan, json_path)
    export_plan_csv(commit_plan, csv_path)

    # Print summary
    console.print(f"[bold]Plan created for:[/bold] {template.name}")
    console.print(f"  Date range: {commit_plan.start_date} to {commit_plan.end_date}")
    console.print(f"  Total commits: [green]{commit_plan.total_commits}[/green]")
    console.print(f"  Days with commits: {commit_plan.total_days}")
    console.print()
    console.print(f"  Exported: [cyan]{json_path}[/cyan]")
    console.print(f"  Exported: [cyan]{csv_path}[/cyan]")


LARGE_PLAN_THRESHOLD = 100


@app.command()
def apply(
    plan_file: str = typer.Argument(..., help="Plan file to apply"),
    repo: str | None = typer.Option(None, "--repo", "-r", help="Target git repository path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be done"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation for large plans"),
    allow_dirty: bool = typer.Option(
        False, "--allow-dirty", help="Allow applying to dirty working tree"
    ),
) -> None:
    """Apply a commit plan to a repository."""
    # Load config
    config = get_config()

    # Load plan
    try:
        commit_plan = load_plan(Path(plan_file))
    except PlanLoadError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Use CLI value or fall back to config
    effective_repo = repo or (str(config.repo_path) if config.repo_path else None)
    if effective_repo is None:
        console.print("[red]Error:[/red] --repo is required (or set repo.path in config)")
        raise typer.Exit(1)

    repo_path = Path(effective_repo)

    if dry_run:
        # Show dry-run summary
        summary = get_dry_run_summary(commit_plan, repo_path)
        console.print(summary)
        return

    # Confirmation for large plans
    total = commit_plan.total_commits
    if total > LARGE_PLAN_THRESHOLD and not yes:
        console.print(
            f"[yellow]Warning:[/yellow] This plan will create [bold]{total}[/bold] commits."
        )
        confirmed = typer.confirm("Do you want to continue?")
        if not confirmed:
            console.print("Aborted.")
            raise typer.Exit(0)

    # Apply the plan
    result = apply_plan(commit_plan, repo_path, dry_run=False, allow_dirty=allow_dirty)

    if not result.success:
        for error in result.errors:
            console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(1)

    console.print(f"[green]Created {result.commits_created} commits[/green]")


@app.command()
def text(
    message: str = typer.Argument(..., help="Text to render"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    preview_flag: bool = typer.Option(False, "--preview", "-p", help="Preview in terminal"),
    spacing: int = typer.Option(1, "--spacing", "-s", help="Spacing between characters"),
) -> None:
    """Generate a template from text."""
    from contriband.fonts import FontError, render_text, template_to_txt

    # Validate input
    if not message.strip():
        console.print("[red]Error:[/red] Text cannot be empty")
        raise typer.Exit(1)

    # Default behavior: preview if no output specified
    if not output and not preview_flag:
        preview_flag = True

    # Render text to template
    try:
        template = render_text(message, spacing=spacing)
    except FontError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Preview in terminal
    if preview_flag:
        console.print(f"[bold]Preview:[/bold] {message}")
        console.print()
        render_template(template, show_labels=True, console=console)
        console.print()

    # Save to file
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        txt_content = template_to_txt(template)
        output_path.write_text(txt_content + "\n")
        console.print(f"[green]Saved:[/green] {output_path}")


@app.command(name="export")
def export_svg(
    template_path: str = typer.Argument(..., help="Template file to export"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output SVG file path"),
    cell_size: int = typer.Option(12, "--cell-size", "-c", help="Cell size in pixels"),
) -> None:
    """Export a template to SVG."""
    from contriband.render import render_template_svg

    # Load template
    try:
        template = load_template(Path(template_path))
    except TemplateError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Render to SVG
    svg_content = render_template_svg(template, cell_size=cell_size)

    # Output
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(svg_content)
        console.print(f"[green]Saved:[/green] {output_path}")
    else:
        # Output to stdout (plain print, not Rich)
        print(svg_content)


@app.command(name="config")
def show_config(
    path: str | None = typer.Option(None, "--path", "-p", help="Path to config file"),
) -> None:
    """Show current configuration."""
    from contriband.config import find_config

    # Find or use explicit config
    config_path = Path(path) if path else find_config()

    if config_path is None:
        console.print("[dim]No config file found[/dim]")
        console.print()
        console.print("Searched locations:")
        console.print("  1. ./contriband.toml")
        console.print("  2. ~/.config/contriband/config.toml")
        console.print()
        console.print("[dim]Using default settings[/dim]")
        cfg = Config()
    else:
        console.print(f"[bold]Config file:[/bold] {config_path}")
        console.print()
        try:
            cfg = load_config(config_path)
        except ConfigError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    # Show current settings
    console.print("[bold]Current settings:[/bold]")
    console.print(f"  repo.path: {cfg.repo_path or '[dim]not set[/dim]'}")
    console.print(f"  repo.branch: {cfg.branch}")
    console.print(f"  author.name: {cfg.author_name or '[dim]not set[/dim]'}")
    console.print(f"  author.email: {cfg.author_email or '[dim]not set[/dim]'}")
    console.print(f"  author.timezone: {cfg.timezone}")
    console.print(f"  levels.mapping: {cfg.level_mapping}")
    console.print(f"  render.week_start: {cfg.week_start}")
    console.print(f"  render.legend: {cfg.legend}")


@app.command()
def status() -> None:
    """Show current project status."""
    console.print("[yellow]status[/yellow] not yet implemented")


if __name__ == "__main__":
    app()
