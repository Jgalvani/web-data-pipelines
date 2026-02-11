from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import click
from rich.console import Console

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.logging_config import setup_logging
from config.settings import settings

console = Console()

# Portal registry — add new portals here
PORTAL_REGISTRY: dict[str, type] = {}


def _register_portals() -> None:
    from portals.books_toscrape.pipeline import BooksToscrapePipeline
    PORTAL_REGISTRY["books_toscrape"] = BooksToscrapePipeline


_register_portals()


@click.group()
def cli() -> None:
    """Web Data Pipelines — browser-driven data collection framework."""
    setup_logging()


@cli.command()
@click.argument("portal", type=click.Choice(list(PORTAL_REGISTRY.keys())))
@click.option("--max-pages", type=int, default=None, help="Max catalogue pages to scrape.")
@click.option("--no-headless", is_flag=True, default=False, help="Run browser in visible mode.")
@click.option("--output-dir", type=click.Path(), default=None, help="Override output directory.")
def run(portal: str, max_pages: int | None, no_headless: bool, output_dir: str | None) -> None:
    """Run a data collection pipeline for PORTAL."""
    pipeline_cls = PORTAL_REGISTRY[portal]

    kwargs: dict = {}
    if max_pages is not None:
        kwargs["max_pages"] = max_pages
    if no_headless:
        kwargs["headless"] = False
    if output_dir:
        from core.export.json_exporter import JsonExporter
        kwargs["exporters"] = [JsonExporter(output_dir=Path(output_dir))]

    pipeline = pipeline_cls(**kwargs)

    console.print(f"[bold green]Starting pipeline:[/] {portal}")
    metadata = asyncio.run(pipeline.run())

    console.print(f"\n[bold]Run complete:[/]")
    console.print(f"  Status:   {metadata.status}")
    console.print(f"  Items:    {metadata.items_collected}")
    console.print(f"  Errors:   {metadata.errors}")
    console.print(f"  Duration: {metadata.duration_seconds:.1f}s")


@cli.command()
def list_portals() -> None:
    """List available portals."""
    for name in PORTAL_REGISTRY:
        console.print(f"  - {name}")


@cli.command()
@click.option("--max-pages", type=int, default=None, help="Max catalogue pages per portal.")
def run_all(max_pages: int | None) -> None:
    """Run all registered portals concurrently."""

    async def _run_all() -> list:
        tasks = []
        for name, pipeline_cls in PORTAL_REGISTRY.items():
            kwargs: dict = {}
            if max_pages is not None:
                kwargs["max_pages"] = max_pages
            pipeline = pipeline_cls(**kwargs)
            tasks.append((name, pipeline.run()))

        console.print(f"[bold green]Running {len(tasks)} portal(s) concurrently:[/]")
        for name, _ in tasks:
            console.print(f"  - {name}")

        results = await asyncio.gather(*(task for _, task in tasks), return_exceptions=True)
        return list(zip([name for name, _ in tasks], results))

    results = asyncio.run(_run_all())

    console.print(f"\n[bold]Results:[/]")
    for name, result in results:
        if isinstance(result, Exception):
            console.print(f"  {name}: [bold red]FAILED[/] — {result}")
        else:
            console.print(
                f"  {name}: {result.status} — "
                f"{result.items_collected} items, "
                f"{result.errors} errors, "
                f"{result.duration_seconds:.1f}s"
            )


@cli.command()
@click.argument("portal", type=click.Choice(list(PORTAL_REGISTRY.keys())))
@click.option("--cron", default="0 6 * * *", help="Cron expression (default: daily at 06:00).")
@click.option("--max-pages", type=int, default=None)
def schedule(portal: str, cron: str, max_pages: int | None) -> None:
    """Register a portal to run on a cron schedule (non-blocking)."""
    from scheduling.scheduler import register_job

    job_id = register_job(portal, cron=cron, max_pages=max_pages)
    console.print(f"[bold green]Registered:[/] {job_id} ({cron})")
    console.print("Run [bold]start-scheduler[/] to activate all registered jobs.")


@cli.command()
def start_scheduler() -> None:
    """Start the scheduler and run all registered jobs (blocking)."""
    from scheduling.scheduler import start_scheduler as _start

    jobs = _list_jobs_helper()
    if not jobs:
        console.print("No jobs registered. Use [bold]schedule[/] first.")
        return

    console.print(f"[bold green]Starting scheduler[/] with {len(jobs)} job(s):")
    for job in jobs:
        console.print(f"  \\[{job['id']}] {job['name']} — {job['trigger']}")
    console.print("Press Ctrl+C to stop.\n")
    _start()


@cli.command()
def list_jobs() -> None:
    """List all registered cron jobs."""
    jobs = _list_jobs_helper()
    if not jobs:
        console.print("No scheduled jobs.")
        return
    for job in jobs:
        job_id = job["id"]
        console.print(f"  \\[{job_id}] {job['name']} — {job['trigger']} — next: {job['next_run']}")


@cli.command()
@click.argument("job_id")
@click.argument("cron")
def update_job(job_id: str, cron: str) -> None:
    """Update the cron expression of a job. E.g.: update-job books_toscrape_cron '30 8 * * *'"""
    from scheduling.scheduler import update_job as _update_job

    if _update_job(job_id, cron):
        console.print(f"[bold green]Updated:[/] {job_id} → {cron}")
    else:
        console.print(f"[bold red]Not found:[/] {job_id}")


@cli.command()
@click.argument("job_id")
def remove_job(job_id: str) -> None:
    """Remove a registered job by its ID."""
    from scheduling.scheduler import remove_job as _remove_job

    if _remove_job(job_id):
        console.print(f"[bold green]Removed:[/] {job_id}")
    else:
        console.print(f"[bold red]Not found:[/] {job_id}")


def _list_jobs_helper() -> list[dict]:
    from scheduling.scheduler import list_jobs as _list
    return _list()


if __name__ == "__main__":
    cli()
