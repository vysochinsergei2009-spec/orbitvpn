from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.keys import set_kb, language_kb, notifications_kb
from app.db.user import UserRepository
from .helpers import safe_answer_callback

router = Router()


@router.callback_query(F.data == 'settings')
async def settings_callback(callback: CallbackQuery, t):
    await safe_answer_callback(callback)
    await callback.message.edit_text(t("settings_text"), reply_markup=set_kb(t))


@router.callback_query(F.data == 'change_lang')
async def change_lang_callback(callback: CallbackQuery, t):
    await safe_answer_callback(callback)
    await callback.message.edit_text(
        t("choose_language"),
        reply_markup=language_kb(t)
    )


@router.callback_query(F.data.startswith("set_lang:"))
async def set_lang_callback(callback: CallbackQuery, t, user_repo: UserRepository):
    lang = callback.data.split(":")[1]
    tg_id = callback.from_user.id

    await user_repo.set_lang(tg_id, lang)
    
    await safe_answer_callback(callback, t("language_updated"), show_alert=True)

    from app.settings.locales import get_translator
    new_t = get_translator(lang)
    await callback.message.edit_text(
        new_t("settings_text"),
        reply_markup=set_kb(new_t)
    )


@router.callback_query(F.data == 'notifications_settings')
async def notifications_settings_callback(callback: CallbackQuery, t, user_repo: UserRepository):
    tg_id = callback.from_user.id
    notifications_enabled = await user_repo.get_notifications(tg_id)

    status = t('notifications_enabled') if notifications_enabled else t('notifications_disabled')

    await safe_answer_callback(callback)
    await callback.message.edit_text(
        t('notifications_text', status=status),
        reply_markup=notifications_kb(t)
    )


@router.callback_query(F.data == 'toggle_notifications')
async def toggle_notifications_callback(callback: CallbackQuery, t, user_repo: UserRepository):
    tg_id = callback.from_user.id
    new_state = await user_repo.toggle_notifications(tg_id)

    status = t('notifications_enabled') if new_state else t('notifications_disabled')

    await safe_answer_callback(callback, t('notifications_updated'), show_alert=True)
    await callback.message.edit_text(
        t('notifications_text', status=status),
        reply_markup=notifications_kb(t)
    )
