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
                LOG.error("Failed to get Marzban access token. Aborting cleanup.")
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