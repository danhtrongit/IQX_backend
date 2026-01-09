"""Scheduler for background tasks like OHLC sync.

Usage:
    from app.infrastructure.scheduler import scheduler

    # Start scheduler (call in app startup)
    scheduler.start()

    # Stop scheduler (call in app shutdown)
    scheduler.shutdown()
"""
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.infrastructure.sync.ohlc_sync import ohlc_sync_service

logger = logging.getLogger(__name__)

# Create scheduler instance
scheduler = AsyncIOScheduler()


async def job_daily_ohlc_sync():
    """Daily OHLC sync job - runs after market close."""
    logger.info(f"[Scheduler] Starting daily OHLC sync at {datetime.now()}")
    try:
        stats = await ohlc_sync_service.daily_sync()
        logger.info(f"[Scheduler] Daily OHLC sync completed: {stats}")
    except Exception as e:
        logger.error(f"[Scheduler] Daily OHLC sync failed: {e}", exc_info=True)


async def job_full_ohlc_sync():
    """Full OHLC sync job - runs weekly on weekends."""
    logger.info(f"[Scheduler] Starting full OHLC sync at {datetime.now()}")
    try:
        stats = await ohlc_sync_service.full_sync(days=200)
        logger.info(f"[Scheduler] Full OHLC sync completed: {stats}")
    except Exception as e:
        logger.error(f"[Scheduler] Full OHLC sync failed: {e}", exc_info=True)


async def job_gap_check_and_fill():
    """Check for gaps and auto-fill missing data."""
    logger.info(f"[Scheduler] Starting gap check at {datetime.now()}")
    try:
        # First check status
        status = await ohlc_sync_service.get_sync_status()
        logger.info(f"[Scheduler] Sync status: {status}")

        # Detect gaps
        gaps = await ohlc_sync_service.detect_gaps(days_back=14)

        if gaps["missing_dates"] or gaps["incomplete_dates"]:
            logger.warning(f"[Scheduler] Gaps detected: {len(gaps['missing_dates'])} missing, "
                           f"{len(gaps['incomplete_dates'])} incomplete")
            # Auto-fill
            result = await ohlc_sync_service.fill_gaps(days_back=14)
            logger.info(f"[Scheduler] Gap fill completed: {result}")
        else:
            logger.info("[Scheduler] No gaps detected, data is complete")
    except Exception as e:
        logger.error(f"[Scheduler] Gap check failed: {e}", exc_info=True)


def setup_scheduler():
    """Setup all scheduled jobs."""

    # Daily sync at 16:00 VN time (after market close at 15:00)
    # Runs Monday to Friday
    scheduler.add_job(
        job_daily_ohlc_sync,
        trigger=CronTrigger(
            hour=16,
            minute=0,
            day_of_week="mon-fri",
            timezone="Asia/Ho_Chi_Minh"
        ),
        id="daily_ohlc_sync",
        name="Daily OHLC Sync",
        replace_existing=True,
    )

    # Full sync at 10:00 on Saturday (refresh all 200 days data)
    scheduler.add_job(
        job_full_ohlc_sync,
        trigger=CronTrigger(
            hour=10,
            minute=0,
            day_of_week="sat",
            timezone="Asia/Ho_Chi_Minh"
        ),
        id="weekly_full_ohlc_sync",
        name="Weekly Full OHLC Sync",
        replace_existing=True,
    )

    # Gap check at 17:00 daily (1 hour after daily sync, as backup)
    scheduler.add_job(
        job_gap_check_and_fill,
        trigger=CronTrigger(
            hour=17,
            minute=0,
            day_of_week="mon-fri",
            timezone="Asia/Ho_Chi_Minh"
        ),
        id="gap_check_and_fill",
        name="Gap Check & Auto-Fill",
        replace_existing=True,
    )

    logger.info("[Scheduler] Jobs configured:")
    for job in scheduler.get_jobs():
        logger.info(f"  - {job.id}: {job.name} | Next run: {job.next_run_time}")


def start_scheduler():
    """Start the scheduler."""
    if not scheduler.running:
        setup_scheduler()
        scheduler.start()
        logger.info("[Scheduler] Started")


def shutdown_scheduler():
    """Shutdown the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Shutdown")
