import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot

from .types.ton_monitoring import check_ton_transactions
from .types.config_cleanup import cleanup_expired_configs
from .types.sub_notifications import check_expiring_subscriptions
from .types.auto_renewal import check_auto_renewals

LOG = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def start(bot: Bot) -> None:
    LOG.info("Starting background task scheduler")
    
    scheduler.add_job(
        check_ton_transactions,
        id="ton_transactions",
        replace_existing=True,
        max_instances=1,
    )
    
    scheduler.add_job(
        cleanup_expired_configs,
        trigger=CronTrigger(day_of_week='sun', hour=3, minute=0),
        id="config_cleanup",
        replace_existing=True,
        max_instances=1,
    )
    
    scheduler.add_job(
        check_expiring_subscriptions,
        trigger=IntervalTrigger(hours=3),
        id="sub_notifications",
        replace_existing=True,
        max_instances=1,
        kwargs={"bot": bot}
    )
    
    scheduler.add_job(
        check_auto_renewals,
        trigger=IntervalTrigger(hours=6),
        id="auto_renewal",
        replace_existing=True,
        max_instances=1,
        kwargs={"bot": bot}
    )
    
    scheduler.start()
    LOG.info("Background task scheduler started successfully")


async def stop() -> None:
    LOG.info("Stopping background task scheduler")
    scheduler.shutdown(wait=True)
    LOG.info("Background task scheduler stopped")