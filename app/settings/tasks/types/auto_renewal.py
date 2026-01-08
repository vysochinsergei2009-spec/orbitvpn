import logging
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import select
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from app.db.db import get_session
from app.models.db import User
from app.db.user import UserRepository
from app.db.cache import get_redis
from app.settings.locales import get_translator
from app.settings.config import env

LOG = logging.getLogger(__name__)


async def check_auto_renewals(bot: Bot):
    try:
        redis = await get_redis()

        async with get_session() as session:
            now = datetime.utcnow()
            threshold = now + timedelta(days=1)

            result = await session.execute(
                select(User).where(
                    User.subscription_end.isnot(None),
                    User.subscription_end <= threshold,
                    User.subscription_end >= now
                )
            )
            users = result.scalars().all()

            LOG.info(f"Checking {len(users)} users for auto-renewal eligibility")

            renewal_count = 0
            for user in users:
                monthly_price = Decimal(str(env.plans['sub_1m']['price']))
                if user.balance < monthly_price:
                    continue

                redis_key = f"auto_renewal:{user.tg_id}:{now.strftime('%Y%m%d')}"
                already_processed = await redis.get(redis_key)
                if already_processed:
                    continue

                success = await _attempt_auto_renewal(user, redis, bot)
                if success:
                    renewal_count += 1
                    await redis.setex(redis_key, 86400, "1")

            LOG.info(f"Auto-renewal check completed: {renewal_count} subscriptions renewed")

    except Exception as e:
        LOG.error(f"Auto-renewal check error: {type(e).__name__}: {e}")


async def _attempt_auto_renewal(user: User, redis, bot: Bot) -> bool:
    try:
        monthly_plan = env.plans['sub_1m']
        price = Decimal(str(monthly_plan['price']))
        days = monthly_plan['days']

        if user.balance < price:
            return False

        async with get_session() as session:
            user_repo = UserRepository(session, redis)

            success = await user_repo.buy_subscription(
                tg_id=user.tg_id,
                days=days,
                price=float(price)
            )

            if success:
                LOG.info(f"Auto-renewed subscription for user {user.tg_id}: {days} days for {price} RUB")

                try:
                    t = get_translator(user.lang)
                    new_balance = user.balance - price
                    sub_end = await user_repo.get_subscription_end(user.tg_id)
                    expire_date = datetime.fromtimestamp(sub_end).strftime('%Y.%m.%d')

                    message = t('auto_renewal_success',
                               days=days,
                               price=float(price),
                               balance=float(new_balance),
                               expire_date=expire_date)

                    await bot.send_message(chat_id=user.tg_id, text=message)
                except (TelegramForbiddenError, TelegramBadRequest) as e:
                    LOG.warning(f"Could not notify user {user.tg_id} about auto-renewal: {e}")

                return True
            else:
                return False

    except Exception as e:
        LOG.error(f"Error during auto-renewal for user {user.tg_id}: {type(e).__name__}: {e}")
        return False