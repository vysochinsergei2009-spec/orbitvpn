"""Utility functions for routers"""

from aiogram.types import CallbackQuery, Message
from app.utils.logging import get_logger

LOG = get_logger(__name__)


async def safe_answer_callback(callback: CallbackQuery):
    """Safely answer callback query to prevent telegram errors"""
    try:
        await callback.answer()
    except Exception:
        pass


async def safe_delete_message(message: Message):
    """Safely delete message without raising errors"""
    try:
        await message.delete()
    except Exception as e:
        LOG.warning(f"Could not delete message: {e}")


async def safe_edit_text(message: Message, text: str, **kwargs):
    """Safely edit message text"""
    try:
        await message.edit_text(text, **kwargs)
    except Exception as e:
        LOG.warning(f"Could not edit message: {e}")
