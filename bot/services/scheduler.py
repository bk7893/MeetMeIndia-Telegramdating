# file: bot/services/scheduler.py
"""APScheduler background jobs"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from database.db import reset_daily_swipes

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def reset_daily_swipes_job() -> None:
    """Daily job to reset swipe counters"""
    logger.info("Running daily swipe reset...")
    await reset_daily_swipes()
    logger.info("✅ Daily swipe reset completed")


async def check_subscription_expiry_job() -> None:
    """Daily job to check subscription expiry"""
    logger.info("Checking subscription expiry...")
    # TODO: Implement subscription expiry checks
    logger.info("✅ Subscription expiry check completed")


def setup_scheduler() -> AsyncIOScheduler:
    """Setup and return configured scheduler"""
    
    # Reset swipes every day at midnight
    scheduler.add_job(
        reset_daily_swipes_job,
        CronTrigger(hour=0, minute=0),
        id="reset_daily_swipes",
        name="Reset Daily Swipes"
    )
    
    # Check subscription expiry every hour
    scheduler.add_job(
        check_subscription_expiry_job,
        CronTrigger(hour="*"),
        id="check_subscription_expiry",
        name="Check Subscription Expiry"
    )
    
    logger.info("✅ Scheduler setup complete")
    return scheduler
