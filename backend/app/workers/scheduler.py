"""Background follow-up scheduler (APScheduler).

Periodically scans ``scheduled_followups`` (a non-RLS internal table) for due
rows across all tenants, then binds each row's tenant for the actual writes.
Started/stopped from the FastAPI lifespan.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.core.config import settings
from app.core.db import async_session_factory, tenant_session
from app.models.lead import Lead, ScheduledFollowup
from app.models.tenant import Tenant
from app.modules.crm.service import run_due_followup

logger = logging.getLogger("travelos.scheduler")
_scheduler: AsyncIOScheduler | None = None


async def process_due_followups() -> int:
    """Send/queue all followups whose run_at has passed. Returns count processed."""
    now = datetime.now(timezone.utc)
    async with async_session_factory() as scan:
        result = await scan.execute(
            select(ScheduledFollowup.id, ScheduledFollowup.tenant_id, ScheduledFollowup.lead_id)
            .where(ScheduledFollowup.run_at <= now, ScheduledFollowup.status == "scheduled")
            .limit(100)
        )
        due = result.all()

    processed = 0
    for followup_id, tenant_id, lead_id in due:
        try:
            async with tenant_session(tenant_id) as s:
                followup = await s.get(ScheduledFollowup, followup_id)
                if followup is None or followup.status != "scheduled":
                    continue
                lead = await s.get(Lead, lead_id)
                tenant = await s.get(Tenant, tenant_id)
                if lead is None or tenant is None:
                    followup.status = "cancelled"
                    continue
                await run_due_followup(s, tenant, lead, followup)
                processed += 1
        except Exception:  # one bad row shouldn't kill the run
            logger.exception("Failed processing followup %s", followup_id)
    if processed:
        logger.info("Processed %d due followup(s)", processed)
    return processed


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = AsyncIOScheduler(timezone="UTC")
    _scheduler.add_job(
        process_due_followups,
        "interval",
        seconds=settings.scheduler_interval_seconds,
        id="process_due_followups",
        max_instances=1,
        coalesce=True,
    )
    _scheduler.start()
    logger.info("Followup scheduler started (every %ss)", settings.scheduler_interval_seconds)


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
