from datetime import datetime
from typing import Callable, Optional

from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from app.repo.user import UserRepository
from app.repo.payments import PaymentRepository
from app.utils.logging import get_logger
from app.utils.redis import get_redis

LOG = get_logger(__name__)


async def safe_answer_callback(callback: CallbackQuery, text: str = None, show_alert: bool = False):
    try:
        await callback.answer(text=text, show_alert=show_alert)
    except TelegramBadRequest as e:
        if "query is too old" in str(e).lower() or "query id is invalid" in str(e).lower():
            LOG.debug(f"Callback query expired for user {callback.from_user.id}, ignoring")
        else:
            raise


async def get_repositories(session):
    """Get repository instances with Redis client."""
    redis_client = await get_redis()
    return (
        UserRepository(session, redis_client),
        PaymentRepository(session, redis_client)
    )


def extract_referrer_id(text: str) -> Optional[int]:
    parts = text.split()
    if len(parts) > 1 and parts[1].startswith("ref_"):
        try:
            return int(parts[1].split("_")[1])
        except (IndexError, ValueError):
            pass
    return None


def format_expire_date(timestamp: float, format_str: str = '%Y.%m.%d') -> str:
    return datetime.fromtimestamp(timestamp).strftime(format_str)


async def get_user_balance(user_repo: UserRepository, tg_id: int) -> float:
    return float(await user_repo.get_balance(tg_id))


async def update_configs_view(
    callback: CallbackQuery,
    t: Callable,
    user_repo: UserRepository,
    tg_id: int,
    custom_text: Optional[str] = None
):
    from app.core.keyboards import myvpn_kb

    configs = await user_repo.get_configs(tg_id)
    has_active_sub = await user_repo.has_active_subscription(tg_id)

    if custom_text:
        text = custom_text
    elif has_active_sub:
        sub_end = await user_repo.get_subscription_end(tg_id)
        expire_date = format_expire_date(sub_end)
        text = t("your_configs_with_sub", expire_date=expire_date) if configs else t("no_configs_has_sub", expire_date=expire_date)
    else:
        text = t("your_configs") if configs else t("no_configs")

    await callback.message.edit_text(text, reply_markup=myvpn_kb(t, configs, has_active_sub))
