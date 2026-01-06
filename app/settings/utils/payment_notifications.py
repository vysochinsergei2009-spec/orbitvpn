from decimal import Decimal
from aiogram import Bot
from app.settings.locales import get_translator
from app.keys.keyboards import payment_success_actions


async def send_payment_notification(
    bot: Bot,
    tg_id: int,
    amount: Decimal,
    lang: str = "ru",
    has_active_subscription: bool = False
) -> None:
    try:
        t = get_translator(lang)
        text = t('payment_success', amount=float(amount))
        keyboard = payment_success_actions(t, has_active_subscription)
        
        await bot.send_message(
            chat_id=tg_id,
            text=text,
            reply_markup=keyboard
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to send payment notification to {tg_id}: {e}")
