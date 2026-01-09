import logging
import random
from datetime import datetime, timedelta
from sqlalchemy import select
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from app.db.db import get_session
from app.models.db import User
from app.db.cache import get_redis
from app.settings.locales import get_translator
from app.keys import renewal_notification_kb
from app.db.cache import set_cache

from app.settings.config import env

LOG = logging.getLogger(__name__)


async def check_expiring_subscriptions(bot: Bot):
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
                await _check_and_notify_user(user, redis, bot)

            LOG.info("Subscription notification check completed")

    except Exception as e:
        LOG.error(f"Subscription notification check error: {type(e).__name__}: {e}")


async def _check_and_notify_user(user: User, redis, bot: Bot):
    if not user.subscription_end:
        return

    now = datetime.utcnow()
    time_left = user.subscription_end - now
    days_left = time_left.total_seconds() / 86400

    if -1 <= days_left <= 0:
        notification_type = 'expired'
        days = 'expired'
        ttl = 86400 * 30
    elif 0 < days_left <= 1:
        notification_type = '1d'
        days = 1
        ttl = 86400 * 7
    elif 1 < days_left <= 3:
        notification_type = '3d'
        days = 3
        ttl = 86400 * 7
    else:
        return

    redis_key = f"notif:{notification_type}:{user.tg_id}"

    try:
        already_sent = await redis.get(redis_key)
        if already_sent:
            return
    except Exception as e:
        LOG.warning(f"Redis error checking notification for {user.tg_id}: {e}")
        return

    success = await _send_notification(user.tg_id, user.lang, days, float(user.balance), bot)

    if success:
        await set_cache(redis_key, "1", ttl)


async def _send_notification(tg_id: int, lang: str, days: int | str, user_balance: float, bot: Bot) -> bool:
    try:
        message = _get_message(lang, days, user_balance)
        if not message:
            return False

        t = get_translator(lang)
        keyboard = renewal_notification_kb(t)

        await bot.send_message(
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


def _get_message(lang: str, days: int | str, user_balance: float = 0) -> str:
    t = get_translator(lang)

    if days == 3:
        return t('sub_expiry_3days')

    if days == 1:
        monthly_price = env.plans['sub_1m']['price']
        needed = max(0, monthly_price - user_balance)

        message = t('sub_expiry_1day')

        if needed > 0:
            message += f"\n\n{t('quick_renewal_info', price=monthly_price, needed=int(needed))}"
        else:
            message += f"\n\n{t('quick_renewal_ready', price=monthly_price)}"

        return message

    if days == 'expired':
        return t('sub_expired')

    return ""
