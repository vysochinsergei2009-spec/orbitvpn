"""Admin server management handlers"""

from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.admin.keyboards import admin_servers_kb, admin_clear_configs_confirm_kb
from app.utils.config_cleanup import cleanup_expired_configs
from config import ADMIN_TG_ID


async def safe_answer_callback(callback: CallbackQuery):
    """Safely answer callback query to prevent telegram errors"""
    try:
        await callback.answer()
    except Exception:
        pass

router = Router()


@router.callback_query(F.data == 'admin_servers')
async def admin_servers(callback: CallbackQuery, t):
    """Show server status and management options"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    # TODO: Implement server status
    servers_text = t('admin_servers_placeholder')

    await callback.message.edit_text(
        servers_text,
        reply_markup=admin_servers_kb(t)
    )


@router.callback_query(F.data == 'admin_clear_configs')
async def admin_clear_configs(callback: CallbackQuery, t):
    """Show confirmation for clearing expired configs"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    await callback.message.edit_text(
        t('admin_clear_configs_confirm'),
        reply_markup=admin_clear_configs_confirm_kb(t)
    )


@router.callback_query(F.data == 'admin_clear_configs_execute')
async def admin_clear_configs_execute(callback: CallbackQuery, t):
    """Execute the cleanup of expired configs"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    # Show "processing" message
    await callback.message.edit_text(t('admin_cleanup_started'))

    # Run cleanup
    stats = await cleanup_expired_configs(days_threshold=14)

    # Show results
    result_text = t('admin_cleanup_result',
                    total=stats['total_checked'],
                    deleted=stats['deleted'],
                    failed=stats['failed'],
                    skipped=stats['skipped'])

    await callback.message.edit_text(
        result_text,
        reply_markup=admin_servers_kb(t)
    )
