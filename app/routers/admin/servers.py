"""Admin server management handlers"""

from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.keys import admin_servers_kb, admin_clear_configs_confirm_kb, Pages, Actions, PageCB
from app.routers.utils import safe_answer_callback
from app.utils.config_cleanup import cleanup_expired_configs
from app.api.client import ClientApiManager
from app.models.server import Server, ServerTypes
from config import ADMIN_TG_IDS, MARZBAN_BASE_URL, MARZBAN_USERNAME, MARZBAN_PASSWORD
from app.utils.logging import get_logger

LOG = get_logger(__name__)

router = Router()


@router.callback_query(PageCB.filter((F.page == Pages.ADMIN_SERVERS) & (F.action == Actions.LIST)))
async def admin_servers(callback: CallbackQuery, callback_data: PageCB, t):
    """Show server status and management options"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id not in ADMIN_TG_IDS:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    # For now, we manually create the list of servers.
    # In the future, this should be fetched from a database.
    servers = [
        Server(
            id="default_marzban",
            name="Default Marzban",
            types=ServerTypes.MARZBAN,
            data={
                "host": MARZBAN_BASE_URL,
                "username": MARZBAN_USERNAME,
                "password": MARZBAN_PASSWORD,
            },
        )
    ]

    total_instances = len(servers)
    active_instances = 0
    
    servers_text = ""
    api_manager = ClientApiManager()

    for server in servers:
        # Get access token
        from app.api.clients.marzban import MarzbanApiManager as MarzbanApiClient
        api = MarzbanApiClient(host=server.data["host"])
        token = await api.get_token(
            username=server.data["username"], password=server.data["password"]
        )
        server.access = token.access_token if token else None

        if server.access:
            active_instances += 1
            status = t('admin_instance_active')
            try:
                nodes = await api_manager.get_nodes(server)
                node_count = len(nodes) if nodes else 0
            except Exception as e:
                LOG.debug(f"Failed to get nodes for server {server.name}: {e}")
                node_count = "N/A"
        else:
            status = t('admin_instance_inactive')
            node_count = "N/A"

        servers_text += t('admin_instance_item',
                          name=server.name,
                          id=server.id,
                          url=server.data['host'],
                          priority=1, # Hardcoded for now
                          status=status,
                          nodes=node_count,
                          excluded=0) # Hardcoded for now

    inactive_instances = total_instances - active_instances
    
    header = t('admin_servers_stats',
                     total=total_instances,
                     active=active_instances,
                     inactive=inactive_instances)
    
    full_text = header + servers_text

    await callback.message.edit_text(
        full_text,
        reply_markup=admin_servers_kb(t)
    )


@router.callback_query(PageCB.filter((F.page == Pages.ADMIN_SERVERS) & (F.action == Actions.DELETE) & (F.datatype == 'configs')))
async def admin_clear_configs(callback: CallbackQuery, callback_data: PageCB, t):
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


@router.callback_query(PageCB.filter((F.page == Pages.ADMIN_SERVERS) & (F.action == Actions.EXECUTE) & (F.datatype == 'clear_configs')))
async def admin_clear_configs_execute(callback: CallbackQuery, callback_data: PageCB, t):
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
