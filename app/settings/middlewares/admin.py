from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from app.settings.config import env


class AdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id

        if user_id and env.is_admin(user_id):
            t = data.get('t')
            if t:
                access_denied_text = t('access_denied')
            else:
                access_denied_text = 'Access denied'

            if isinstance(event, CallbackQuery):
                await event.answer(access_denied_text, show_alert=True)
                return None

            if isinstance(event, Message):
                await event.answer(access_denied_text)
                return None

        return await handler(event, data)
