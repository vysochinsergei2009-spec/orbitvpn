import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy import select, update, func
from app.db.db import get_session
from app.db.models import User, Config
from app.api import ClientApiManager
from app.models.server import Server, ServerTypes
from config import MARZBAN_BASE_URL, MARZBAN_USERNAME, MARZBAN_PASSWORD
from app.utils.redis import get_redis

LOG = logging.getLogger(__name__)


async def cleanup_expired_configs(days_threshold: int = 14) -> dict:
    stats = {
        'total_checked': 0,
        'deleted': 0,
        'failed': 0,
        'skipped': 0
    }

    try:
        async with get_session() as session:
            redis = await get_redis()
            
            server = Server(
                id="default_marzban",
                name="Default Marzban",
                types=ServerTypes.MARZBAN,
                data={
                    "host": MARZBAN_BASE_URL,
                    "username": MARZBAN_USERNAME,
                    "password": MARZBAN_PASSWORD,
                },
            )
            from app.api.clients.marzban import MarzbanApiManager
            api = MarzbanApiManager(host=server.data["host"])
            token = await api.get_token(
                username=server.data["username"], password=server.data["password"]
            )
            server.access = token.access_token if token else None

            if not server.access:
                LOG.error("Failed to get access token for Marzban server. Aborting cleanup.")
                return stats

            api_manager = ClientApiManager()

            now = datetime.utcnow()
            threshold_date = now - timedelta(days=days_threshold)

            LOG.info(f"Starting expired config cleanup (threshold: {days_threshold} days, cutoff: {threshold_date})")

            result = await session.execute(
                select(Config, User.subscription_end)
                .join(User, Config.tg_id == User.tg_id)
                .where(
                    Config.deleted == False,
                    User.subscription_end.isnot(None),
                    User.subscription_end < threshold_date
                )
            )
            configs_to_delete = result.all()

            stats['total_checked'] = len(configs_to_delete)
            LOG.info(f"Found {stats['total_checked']} expired configs to clean up")

            for config, subscription_end in configs_to_delete:
                try:
                    tg_id = config.tg_id
                    username = config.username
                    config_id = config.id
                    
                    if not username:
                        LOG.warning(f"Config {config_id} has no username, skipping")
                        stats['skipped'] += 1
                        continue

                    LOG.info(f"Cleaning up config {config_id} (user: {tg_id}, username: {username}, expired: {subscription_end})")

                    try:
                        await api_manager.remove_user(server, username)
                        LOG.info(f"Deleted Marzban user {username}")
                    except Exception as e:
                        LOG.warning(f"Failed to delete Marzban user {username}: {e} (continuing with DB cleanup)")

                    config.deleted = True

                    await session.execute(
                        update(User)
                        .where(User.tg_id == tg_id)
                        .values(configs=func.greatest(User.configs - 1, 0))
                    )

                    await session.commit()

                    try:
                        await redis.delete(f"user:{tg_id}:configs")
                    except Exception as e:
                        LOG.warning(f"Failed to invalidate cache for user {tg_id}: {e}")

                    stats['deleted'] += 1
                    LOG.info(f"Successfully cleaned up config {config_id}")

                except Exception as e:
                    LOG.error(f"Error cleaning up config {config.id}: {type(e).__name__}: {e}")
                    stats['failed'] += 1
                    await session.rollback()

            LOG.info(f"Config cleanup completed: {stats}")
            return stats

    except Exception as e:
        LOG.error(f"Fatal error in cleanup_expired_configs: {type(e).__name__}: {e}")
        stats['failed'] = stats['total_checked']
        return stats


class ConfigCleanupTask:
    """
    Background task that periodically cleans up expired configs.

    Runs once per week by default and removes configs for users
    whose subscriptions expired more than 14 days ago.
    """

    def __init__(self, check_interval_seconds: int = 86400 * 7, days_threshold: int = 14):
        """
        Args:
            check_interval_seconds: How often to run cleanup (default: 7 days)
            days_threshold: Days after expiry to keep configs (default: 14)
        """
        self.check_interval = check_interval_seconds
        self.days_threshold = days_threshold
        self.task: asyncio.Task = None
        self._running = False

    async def run_once(self):
        """Run a single cleanup cycle"""
        try:
            stats = await cleanup_expired_configs(self.days_threshold)
            LOG.info(f"Expired config cleanup stats: {stats}")
        except Exception as e:
            LOG.error(f"Config cleanup error: {type(e).__name__}: {e}")

    async def run_loop(self):
        """Continuously run cleanup checks"""
        self._running = True
        LOG.info(f"Config cleanup task started (interval: {self.check_interval}s, threshold: {self.days_threshold} days)")

        while self._running:
            try:
                await self.run_once()
            except Exception as e:
                LOG.error(f"Error in config cleanup loop: {type(e).__name__}: {e}")

            await asyncio.sleep(self.check_interval)

        LOG.info("Config cleanup task stopped")

    def start(self):
        """Start the background cleanup task"""
        if self.task is None or self.task.done():
            self.task = asyncio.create_task(self.run_loop())
            LOG.info("Config cleanup task created")
        else:
            LOG.warning("Config cleanup task already running")

    def stop(self):
        """Stop the background cleanup task"""
        self._running = False
        if self.task and not self.task.done():
            self.task.cancel()
            LOG.info("Config cleanup task cancelled")
