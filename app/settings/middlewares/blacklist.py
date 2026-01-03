from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery
from app.db.db import UserRepository

class BlacklistMiddleware(BaseMiddleware):
    
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        user = None
        
        if event.message:
            user = event.message.from_user
        elif event.callback_query:
            user = event.callback_query.from_user
        elif event.inline_query:
            user = event.inline_query.from_user
        elif event.chosen_inline_result:
            user = event.chosen_inline_result.from_user
        
        if not user:
            return None
        
        session = data.get("session")
        user_repo = UserRepository(session)
        
        is_banned = await user_repo.is_user_banned(user.id)
        
        if is_banned:
            if isinstance(event.message, Message):
                await event.message.answer(
                    "🚫 <b>Access Denied</b>\n\n"
                    "Your account has been blocked.\n"
                    "Contact support for more information."
                )
            elif isinstance(event.callback_query, CallbackQuery):
                await event.callback_query.answer(
                    "🚫 Your account is blocked",
                    show_alert=True
                )
            return None
        
        return await handler(event, data)