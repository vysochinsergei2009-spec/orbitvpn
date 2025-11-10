"""Telegram Alert Notifier"""
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from manager.core.models import Alert, AlertLevel
from manager.utils.logger import get_logger

LOG = get_logger(__name__)


class TelegramNotifier:
    """Sends alerts via Telegram"""

    def __init__(self, bot_token: str, admin_chat_ids: List[int]):
        self.bot_token = bot_token
        self.admin_chat_ids = admin_chat_ids

    async def send_alert(self, alert: Alert):
        """Send alert to admin chats."""
        try:
            # Import aiogram
            from aiogram import Bot
            from aiogram.client.default import DefaultBotProperties
            from aiogram.enums import ParseMode

            bot = Bot(
                token=self.bot_token,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )

            # Format message
            emoji = self._get_emoji(alert.level)
            message = self._format_message(alert, emoji)

            # Send to all admins
            for chat_id in self.admin_chat_ids:
                try:
                    await bot.send_message(chat_id, message)
                except Exception as e:
                    LOG.error(f"Failed to send alert to {chat_id}: {e}")

            await bot.session.close()

        except Exception as e:
            LOG.error(f"Failed to send Telegram alert: {e}")

    def _get_emoji(self, level: AlertLevel) -> str:
        """Get emoji for alert level."""
        emojis = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.ERROR: "❌",
            AlertLevel.CRITICAL: "🚨"
        }
        return emojis.get(level, "📢")

    def _format_message(self, alert: Alert, emoji: str) -> str:
        """Format alert message for Telegram."""
        message = f"{emoji} <b>OrbitVPN Alert</b>\n\n"
        message += f"<b>Level:</b> {alert.level.value.upper()}\n"
        message += f"<b>Service:</b> {alert.service}\n"
        message += f"<b>Message:</b> {alert.message}\n"
        message += f"<b>Time:</b> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"

        if alert.details:
            message += f"\n<b>Details:</b>\n"
            for key, value in alert.details.items():
                message += f"  • {key}: {value}\n"

        return message
