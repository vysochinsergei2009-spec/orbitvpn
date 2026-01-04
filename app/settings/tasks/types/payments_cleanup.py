import logging
from app.repo.db import get_session
from app.repo.payments import PaymentRepository
from app.utils.redis import get_redis

LOG = logging.getLogger(__name__)


async def cleanup_expired_payments(cleanup_days: int = 7) -> None:
    try:
        async with get_session() as session:
            redis_client = await get_redis()
            payment_repo = PaymentRepository(session, redis_client)

            expired_count = await payment_repo.expire_old_payments()
            if expired_count > 0:
                LOG.info(f"Marked {expired_count} payments as expired")

            deleted_count = await payment_repo.cleanup_old_payments(days=cleanup_days)
            if deleted_count > 0:
                LOG.info(f"Cleaned up {deleted_count} old expired/cancelled payments")

    except Exception as e:
        LOG.error(f"Payment cleanup error: {type(e).__name__}: {e}")