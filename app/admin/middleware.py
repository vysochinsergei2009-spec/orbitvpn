"""Admin middleware for access control"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from config import ADMIN_TG_ID


class AdminMiddleware(BaseMiddleware):
    """
    Middleware to restrict admin handlers to authorized users.

    Checks if user's Telegram ID matches ADMIN_TG_ID from config.
    If not authorized, returns access denied message and blocks handler execution.
    """

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """
        Check admin access before executing handler.

        Args:
            handler: The handler function to be called
            event: Telegram event (Message or CallbackQuery)
            data: Additional data passed to handler

        Returns:
            Handler result if authorized, None otherwise
        """
        user_id = event.from_user.id

        # Check if user is admin
        if user_id != ADMIN_TG_ID:
            # Get translator function from data
            t = data.get('t')
            if t:
                access_denied_text = t('access_denied')
            else:
                access_denied_text = 'Access denied'

            # Handle callback query
            if isinstance(event, CallbackQuery):
                await event.answer(access_denied_text, show_alert=True)
                return None

            # Handle message
            if isinstance(event, Message):
                await event.answer(access_denied_text)
                return None

        # User is admin, proceed with handler
        return await handler(event, data)
