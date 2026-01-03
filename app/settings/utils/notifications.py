import asyncio
import logging
import random
from datetime import datetime, timedelta
from sqlalchemy import select
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from app.db.db import get_session
from app.db.models import User
from app.utils.redis import get_redis
from app.settings.locales import get_translator
from app.keys.keyboards import balance_button_kb, get_renewal_notification_keyboard

LOG = logging.getLogger(__name__)


class SubscriptionNotificationTask:
    def __init__(self, bot: Bot, check_interval_seconds: int = 3600 * 3):
        """
        Args:
            bot: Aiogram Bot instance for sending messages
            check_interval_seconds: How often to check (default: 3 hours)
        """
        self.bot = bot
        self.check_interval = check_interval_seconds
        self.task: asyncio.Task = None
        self._running = False

    def _get_random_message(self, lang: str, days: int | str, user_balance: float = 0) -> str:
        from config import PLANS
        t = get_translator(lang)

        if days == 3:
            variants = [
                t('sub_expiry_3days_1'),
                t('sub_expiry_3days_2'),
                t('sub_expiry_3days_3'),
            ]
        elif days == 1:
            monthly_price = PLANS['sub_1m']['price']
            needed = max(0, monthly_price - user_balance)

            variants = [
                t('sub_expiry_1day_1'),
                t('sub_expiry_1day_2'),
                t('sub_expiry_1day_3'),
            ]

            message = random.choice(variants)

            if needed > 0:
                message += f"\n\n{t('quick_renewal_info', price=monthly_price, needed=int(needed))}"
            else:
                message += f"\n\n{t('quick_renewal_ready', price=monthly_price)}"

            return message

        elif days == 'expired':
            variants = [
                t('sub_expired_1'),
                t('sub_expired_2'),
                t('sub_expired_3'),
            ]
        else:
            return ""

        return random.choice(variants)

    async def _send_notification(self, tg_id: int, lang: str, days: int | str, user_balance: float = 0) -> bool:
        try:
            message = self._get_random_message(lang, days, user_balance)
            if not message:
                return False

            t = get_translator(lang)
            keyboard = get_renewal_notification_keyboard(t)

            await self.bot.send_message(
                chat_id=tg_id,
                text=message,
                reply_markup=keyboard
            )

            LOG.info(f"Sent {days}-day expiry notification to user {tg_id}")
            return True

        except TelegramForbiddenError:
            LOG.warning(f"User {tg_id} blocked the bot")
            return False
        except TelegramBadRequest as e:
            LOG.warning(f"Bad request sending notification to {tg_id}: {e}")
            return False
        except Exception as e:
            LOG.error(f"Error sending notification to {tg_id}: {type(e).__name__}: {e}")
            return False

    async def _check_and_notify_user(self, user: User, redis):
        if not user.notifications:
            return

        if not user.subscription_end:
            return

        now = datetime.utcnow()
        time_left = user.subscription_end - now
        days_left = time_left.total_seconds() / 86400

        sub_end_date = user.subscription_end.strftime('%Y%m%d')

        if -1 <= days_left <= 0:
            notification_type = 'expired'
            days = 'expired'
            ttl = 86400 * 7
        elif 0 < days_left <= 1:
            notification_type = '1d'
            days = 1
            ttl = 86400 * 2
        elif 1 < days_left <= 3:
            notification_type = '3d'
            days = 3
            ttl = 86400 * 4
        else:
            return

        redis_key = f"notif:{notification_type}:{user.tg_id}:{sub_end_date}"

        try:
            already_sent = await redis.get(redis_key)
            if already_sent:
                return
        except Exception as e:
            LOG.warning(f"Redis error checking notification for {user.tg_id}: {e}")
            return

        success = await self._send_notification(user.tg_id, user.lang, days, float(user.balance))

        if success:
            try:
                await redis.setex(redis_key, ttl, "1")
            except Exception as e:
                LOG.warning(f"Redis error marking notification sent for {user.tg_id}: {e}")

    async def run_once(self):
        """Run a single notification check cycle"""
        try:
            redis = await get_redis()

            async with get_session() as session:
                now = datetime.utcnow()
                future_threshold = now + timedelta(days=3)
                past_threshold = now - timedelta(days=1)

                result = await session.execute(
                    select(User).where(
                        User.subscription_end.isnot(None),
                        User.subscription_end >= past_threshold,
                        User.subscription_end <= future_threshold
                    )
                )
                users = result.scalars().all()

                LOG.info(f"Checking {len(users)} users for expiring/expired subscriptions")

                for user in users:
                    await self._check_and_notify_user(user, redis)

                LOG.info("Subscription notification check completed")

        except Exception as e:
            LOG.error(f"Subscription notification check error: {type(e).__name__}: {e}")

    async def run_loop(self):
        """Continuously run notification checks"""
        self._running = True
        LOG.info(f"Subscription notification task started (interval: {self.check_interval}s)")

        while self._running:
            try:
                await self.run_once()
            except Exception as e:
                LOG.error(f"Error in subscription notification loop: {type(e).__name__}: {e}")

            await asyncio.sleep(self.check_interval)

        LOG.info("Subscription notification task stopped")

    def start(self):
        """Start the background notification task"""
        if self.task is None or self.task.done():
            self.task = asyncio.create_task(self.run_loop())
            LOG.info("Subscription notification task created")
        else:
            LOG.warning("Subscription notification task already running")

    def stop(self):
        """Stop the background notification task"""
        self._running = False
        if self.task and not self.task.done():
            self.task.cancel()
            LOG.info("Subscription notification task cancelled")
