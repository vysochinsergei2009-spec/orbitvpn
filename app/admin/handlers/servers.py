"""Admin server management handlers"""

from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.admin.keyboards import admin_servers_kb, admin_clear_configs_confirm_kb
from app.core.handlers.utils import safe_answer_callback
from app.utils.config_cleanup import cleanup_expired_configs
# No longer needed from app.repo.db import get_session
# No longer needed from app.repo.models import MarzbanInstance
from app.repo.marzban_client import MarzbanClient
from app.utils.logging import get_logger
from config import ADMIN_TG_IDS

LOG = get_logger(__name__)

router = Router()


@router.callback_query(F.data == 'admin_servers')
async def admin_servers(callback: CallbackQuery, t):
    """Show server status and management options"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id not in ADMIN_TG_IDS:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    client = MarzbanClient()
    instance = client._instance  # Get the single, env-configured instance

    total_instances = 1
    active_instances = 1 if instance.is_active else 0
    inactive_instances = 1 - active_instances

    servers_text = t('admin_servers_stats',
                     total=total_instances,
                     active=active_instances,
                     inactive=inactive_instances)

    # Display the single instance details
    status = t('admin_instance_active') if instance.is_active else t('admin_instance_inactive')
    excluded_count = len(instance.excluded_node_names) if instance.excluded_node_names else 0

    # Try to get node count from Marzban API
    node_count = "N/A"
    if instance.is_active:
        try:
            api = client._get_or_create_api(instance)
            nodes = await api.get_nodes()
            node_count = len(nodes)
        except Exception as e:
            LOG.debug(f"Failed to get nodes for instance {instance.id}: {e}")

    servers_text += t('admin_instance_item',
                      name=instance.name,
                      id=instance.id,
                      url=instance.base_url,
                      priority=instance.priority,
                      status=status,
                      nodes=node_count,
                      excluded=excluded_count)

    await callback.message.edit_text(
        servers_text,
        reply_markup=admin_servers_kb(t)
    )


@router.callback_query(F.data == 'admin_clear_configs')
async def admin_clear_configs(callback: CallbackQuery, t):
    """Show confirmation for clearing expired configs"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id not in ADMIN_TG_IDS:
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

    if tg_id not in ADMIN_TG_IDS:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    # Show "processing" message
    await callback.message.edit_text(t('admin_cleanup_started'))

    # Run cleanup
    stats = await cleanup_expired_configs(days_threshold=3)

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
