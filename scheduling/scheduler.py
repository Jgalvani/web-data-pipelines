from __future__ import annotations

import asyncio
from typing import Any

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from config.logging_config import get_logger
from config.settings import settings

log = get_logger(__name__)

DB_PATH = settings.output_dir / "scheduler.db"


def _get_jobstore() -> SQLAlchemyJobStore:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return SQLAlchemyJobStore(url=f"sqlite:///{DB_PATH}")


def _run_pipeline(portal_name: str, **kwargs: Any) -> None:
    """Sync wrapper to run an async pipeline from APScheduler."""
    from main import PORTAL_REGISTRY

    pipeline_cls = PORTAL_REGISTRY[portal_name]
    pipeline = pipeline_cls(**kwargs)
    metadata = asyncio.run(pipeline.run())
    log.info(
        "scheduled_run_complete",
        portal=portal_name,
        items=metadata.items_collected,
        status=metadata.status,
    )


def register_job(
    portal_name: str,
    cron: str = "0 6 * * *",
    max_pages: int | None = None,
) -> str:
    """Register a job (non-blocking). Returns the job ID."""
    job_id = f"{portal_name}_cron"

    parts = cron.split()
    trigger = CronTrigger(
        minute=parts[0],
        hour=parts[1],
        day=parts[2],
        month=parts[3],
        day_of_week=parts[4],
    )

    kwargs: dict[str, Any] = {}
    if max_pages is not None:
        kwargs["max_pages"] = max_pages

    # Use a temporary BackgroundScheduler to persist the job, then shut down
    scheduler = BackgroundScheduler(
        jobstores={"default": _get_jobstore()},
    )
    scheduler.start(paused=True)
    scheduler.add_job(
        _run_pipeline,
        trigger=trigger,
        args=[portal_name],
        kwargs=kwargs,
        id=job_id,
        name=f"Pipeline: {portal_name}",
        replace_existing=True,
    )
    scheduler.shutdown(wait=False)

    log.info("job_registered", job_id=job_id, portal=portal_name, cron=cron)
    return job_id


def start_scheduler() -> None:
    """Start the blocking scheduler with all persisted jobs."""
    jobs = list_jobs()
    if not jobs:
        log.warning("no_jobs_registered")
        return

    scheduler = BlockingScheduler(
        jobstores={"default": _get_jobstore()},
    )

    log.info("scheduler_started", total_jobs=len(jobs))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("scheduler_stopped")


def list_jobs() -> list[dict]:
    """List all persisted jobs."""
    store = _get_jobstore()
    store.start(None, "default")
    try:
        return [
            {
                "id": job.id,
                "name": job.name,
                "trigger": str(job.trigger),
                "next_run": str(job.next_run_time) if job.next_run_time else "paused",
            }
            for job in store.get_all_jobs()
        ]
    finally:
        store.shutdown()


def update_job(job_id: str, cron: str) -> bool:
    """Update the cron expression of a persisted job. Returns True if found."""
    parts = cron.split()
    trigger = CronTrigger(
        minute=parts[0],
        hour=parts[1],
        day=parts[2],
        month=parts[3],
        day_of_week=parts[4],
    )

    scheduler = BackgroundScheduler(
        jobstores={"default": _get_jobstore()},
    )
    scheduler.start(paused=True)
    try:
        scheduler.reschedule_job(job_id, trigger=trigger)
        scheduler.shutdown(wait=False)
        log.info("job_updated", job_id=job_id, cron=cron)
        return True
    except Exception:
        scheduler.shutdown(wait=False)
        log.warning("job_not_found", job_id=job_id)
        return False


def remove_job(job_id: str) -> bool:
    """Remove a persisted job by ID. Returns True if found and removed."""
    store = _get_jobstore()
    store.start(None, "default")
    try:
        store.remove_job(job_id)
        log.info("job_removed", job_id=job_id)
        return True
    except Exception:
        log.warning("job_not_found", job_id=job_id)
        return False
    finally:
        store.shutdown()
