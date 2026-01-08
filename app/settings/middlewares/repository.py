from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.db.db import get_session
from app.db.cache import get_redis
from app.db.user import UserRepository
from app.db.payments import PaymentRepository
from app.settings.log import get_logger

LOG = get_logger(__name__)


class RepositoryMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with get_session() as session:
            try:
                redis_client = await get_redis()
                
                data['user_repo'] = UserRepository(session, redis_client)
                data['payment_repo'] = PaymentRepository(session, redis_client)
                data['session'] = session
                
                return await handler(event, data)
                
            except Exception as e:
                LOG.error(f"Repository middleware error: {e}")
                raise