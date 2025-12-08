

# ===== START FILE: app/admin/keyboards.py =====

"""Admin panel keyboards"""

from typing import Callable

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def _build_keyboard(buttons_data: list[dict], adjust: list[int] | None = None):
    """Helper to build inline keyboard from button data"""
    kb = InlineKeyboardBuilder()

    for btn in buttons_data:
        if 'url' in btn:
            kb.button(text=btn['text'], url=btn['url'])
        else:
            kb.button(text=btn['text'], callback_data=btn['callback_data'])

    if adjust:
        kb.adjust(*adjust)
    else:
        kb.adjust(1)

    return kb.as_markup()


def admin_panel_kb(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    """Admin panel keyboard with various management options"""
    return _build_keyboard([
        {'text': t('admin_stats'), 'callback_data': 'admin_stats'},
        {'text': t('admin_users'), 'callback_data': 'admin_users'},
        {'text': t('admin_payments'), 'callback_data': 'admin_payments'},
        {'text': t('admin_servers'), 'callback_data': 'admin_servers'},
        {'text': t('admin_broadcast'), 'callback_data': 'admin_broadcast'},
        {'text': t('back_main'), 'callback_data': 'back_main'},
    ], adjust=[2, 2, 1, 1])


def admin_servers_kb(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    """Server management keyboard"""
    return _build_keyboard([
        {'text': t('admin_clear_configs'), 'callback_data': 'admin_clear_configs'},
        {'text': t('back'), 'callback_data': 'admin_panel'},
    ])


def admin_clear_configs_confirm_kb(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    """Confirmation keyboard for config cleanup"""
    return _build_keyboard([
        {'text': t('confirm_yes'), 'callback_data': 'admin_clear_configs_execute'},
        {'text': t('confirm_no'), 'callback_data': 'admin_servers'},
    ])


def broadcast_cancel_kb(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    """Cancel broadcast keyboard"""
    return _build_keyboard([
        {'text': t('cancel'), 'callback_data': 'broadcast_cancel'},
    ])


def broadcast_settings_kb(
    t: Callable[[str], str],
    selected_target: str = 'all',
    selected_time: str = 'now'
) -> InlineKeyboardMarkup:
    """Broadcast settings keyboard with target and time selection"""
    buttons = []

    # Target selection
    all_marker = '✓ ' if selected_target == 'all' else ''
    subscribed_marker = '✓ ' if selected_target == 'subscribed' else ''

    buttons.extend([
        {'text': f"{all_marker}{t('broadcast_target_all')}", 'callback_data': 'broadcast_target_all'},
        {'text': f"{subscribed_marker}{t('broadcast_target_subscribed')}", 'callback_data': 'broadcast_target_subscribed'},
    ])

    # Time selection
    now_marker = '✓ ' if selected_time == 'now' else ''
    buttons.append({'text': f"{now_marker}{t('broadcast_time_now')}", 'callback_data': 'broadcast_time_now'})

    # Action buttons
    buttons.extend([
        {'text': t('broadcast_send'), 'callback_data': 'broadcast_confirm'},
        {'text': t('cancel'), 'callback_data': 'broadcast_cancel'},
    ])

    return _build_keyboard(buttons, adjust=[2, 1, 1, 1])


def broadcast_confirm_kb(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    """Final confirmation keyboard for broadcast"""
    return _build_keyboard([
        {'text': t('broadcast_execute'), 'callback_data': 'broadcast_execute'},
        {'text': t('cancel'), 'callback_data': 'broadcast_cancel'},
    ], adjust=[1, 1])


def admin_users_kb(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    """User management keyboard"""
    return _build_keyboard([
        {'text': t('admin_search_user'), 'callback_data': 'admin_search_user'},
        {'text': t('admin_user_list'), 'callback_data': 'admin_user_list'},
        {'text': t('back'), 'callback_data': 'admin_panel'},
    ], adjust=[2, 1])


def admin_user_detail_kb(t: Callable[[str], str], user_id: int) -> InlineKeyboardMarkup:
    """User detail management keyboard"""
    return _build_keyboard([
        {'text': t('admin_grant_sub'), 'callback_data': f'admin_grant_sub:{user_id}'},
        {'text': t('admin_revoke_sub'), 'callback_data': f'admin_revoke_sub:{user_id}'},
        {'text': t('admin_add_balance'), 'callback_data': f'admin_add_balance:{user_id}'},
        {'text': t('admin_view_configs'), 'callback_data': f'admin_view_configs:{user_id}'},
        {'text': t('admin_search_user'), 'callback_data': 'admin_search_user'},
        {'text': t('back'), 'callback_data': 'admin_users'},
    ], adjust=[2, 2, 1, 1])


def admin_user_list_kb(t: Callable[[str], str], page: int, total_pages: int) -> InlineKeyboardMarkup:
    """User list pagination keyboard"""
    buttons = []

    # Navigation buttons
    if page > 0:
        buttons.append({'text': t('admin_prev_page'), 'callback_data': f'admin_user_list_page:{page-1}'})
    if page < total_pages - 1:
        buttons.append({'text': t('admin_next_page'), 'callback_data': f'admin_user_list_page:{page+1}'})

    # Add back button
    buttons.append({'text': t('back'), 'callback_data': 'admin_users'})

    # Adjust layout: navigation buttons in one row, back button in another
    if len(buttons) == 3:
        return _build_keyboard(buttons, adjust=[2, 1])
    else:
        return _build_keyboard(buttons, adjust=[1, 1])


def admin_payments_kb(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    """Payments statistics keyboard"""
    return _build_keyboard([
        {'text': t('admin_recent_payments'), 'callback_data': 'admin_recent_payments'},
        {'text': t('back'), 'callback_data': 'admin_panel'},
    ])


def admin_instance_detail_kb(t: Callable[[str], str], instance_id: str) -> InlineKeyboardMarkup:
    """Instance detail keyboard"""
    return _build_keyboard([
        {'text': t('admin_view_nodes'), 'callback_data': f'admin_view_nodes:{instance_id}'},
        {'text': t('back'), 'callback_data': 'admin_servers'},
    ])


# ===== END FILE: app/admin/keyboards.py =====



# ===== START FILE: app/admin/__init__.py =====

"""Admin module - admin panel functionality"""

from .handlers import router

__all__ = ['router']


# ===== END FILE: app/admin/__init__.py =====



# ===== START FILE: app/admin/middleware.py =====

"""Admin middleware for access control"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from config import ADMIN_TG_ID


class AdminMiddleware(BaseMiddleware):
    """
    Middleware to restrict admin handlers to authorized users.

    Checks if user's Telegram ID matches ADMIN_TG_ID from config.
    If not authorized, returns access denied message and blocks handler execution.
    """

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """
        Check admin access before executing handler.

        Args:
            handler: The handler function to be called
            event: Telegram event (Message or CallbackQuery)
            data: Additional data passed to handler

        Returns:
            Handler result if authorized, None otherwise
        """
        user_id = event.from_user.id

        # Check if user is admin
        if user_id != ADMIN_TG_ID:
            # Get translator function from data
            t = data.get('t')
            if t:
                access_denied_text = t('access_denied')
            else:
                access_denied_text = 'Access denied'

            # Handle callback query
            if isinstance(event, CallbackQuery):
                await event.answer(access_denied_text, show_alert=True)
                return None

            # Handle message
            if isinstance(event, Message):
                await event.answer(access_denied_text)
                return None

        # User is admin, proceed with handler
        return await handler(event, data)


# ===== END FILE: app/admin/middleware.py =====



# ===== START FILE: app/admin/handlers/users.py =====

"""Admin handlers for user management"""

import time
from datetime import datetime, timedelta
from decimal import Decimal

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, func

from app.admin.keyboards import admin_users_kb, admin_user_detail_kb, admin_user_list_kb
from app.repo.db import get_session
from app.repo.models import User
from app.repo.user import UserRepository
from config import ADMIN_TG_ID


router = Router()


class AdminUserStates(StatesGroup):
    """FSM states for admin user management"""
    waiting_user_id = State()
    waiting_grant_days = State()
    waiting_balance_amount = State()


async def safe_answer_callback(callback: CallbackQuery):
    """Safely answer callback query to prevent telegram errors"""
    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data == 'admin_users')
async def show_admin_users(callback: CallbackQuery, t):
    """Show user management panel with statistics"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    # Get user statistics
    async with get_session() as session:
        # Total users
        result = await session.execute(select(func.count(User.tg_id)))
        total_users = result.scalar() or 0

        # Users with active subscription
        now = datetime.utcnow()
        result = await session.execute(
            select(func.count(User.tg_id)).where(
                User.subscription_end > now
            )
        )
        active_subs = result.scalar() or 0

        # Users without subscription
        no_subs = total_users - active_subs

        # New users in last 24h
        day_ago = now - timedelta(days=1)
        result = await session.execute(
            select(func.count(User.tg_id)).where(
                User.created_at >= day_ago
            )
        )
        new_24h = result.scalar() or 0

        # Average balance
        result = await session.execute(select(func.avg(User.balance)))
        avg_balance = result.scalar() or 0.0
        if isinstance(avg_balance, Decimal):
            avg_balance = float(avg_balance)

    stats_text = t('admin_users_stats',
                   total=total_users,
                   active_sub=active_subs,
                   no_sub=no_subs,
                   new_24h=new_24h,
                   avg_balance=avg_balance)

    await callback.message.edit_text(
        stats_text,
        reply_markup=admin_users_kb(t)
    )


@router.callback_query(F.data == 'admin_search_user')
async def admin_search_user_start(callback: CallbackQuery, t, state: FSMContext):
    """Start user search by ID"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    await callback.message.edit_text(t('admin_enter_user_id'))
    await state.set_state(AdminUserStates.waiting_user_id)


@router.message(AdminUserStates.waiting_user_id)
async def admin_search_user_process(message: Message, t, state: FSMContext):
    """Process user ID search"""
    tg_id = message.from_user.id

    if tg_id != ADMIN_TG_ID:
        return

    try:
        search_id = int(message.text.strip())
    except ValueError:
        await message.answer(t('admin_invalid_days'))
        return

    await state.clear()

    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.tg_id == search_id)
        )
        user = result.scalar_one_or_none()

    if not user:
        await message.answer(t('admin_user_not_found'))
        return

    # Format user info
    username = user.username or "N/A"
    referrer = user.referrer_id if user.referrer_id else "N/A"
    created_at_str = user.created_at.strftime("%Y-%m-%d %H:%M") if user.created_at else "N/A"
    notifications_str = t('notifications_enabled') if user.notifications else t('notifications_disabled')

    user_text = t('admin_user_info',
                  username=username,
                  tg_id=user.tg_id,
                  balance=user.balance,
                  configs=user.configs,
                  lang=user.lang,
                  notifications=notifications_str,
                  referrer=referrer,
                  created_at=created_at_str)

    # Add subscription info
    if user.subscription_end:
        expire_ts = user.subscription_end.timestamp()
        expire_date = user.subscription_end.strftime("%Y-%m-%d %H:%M")

        if time.time() < expire_ts:
            sub_info = t('admin_sub_active', expire_date=expire_date)
        else:
            sub_info = t('admin_sub_expired', expire_date=expire_date)
    else:
        sub_info = t('admin_sub_none')

    user_text += t('admin_user_subscription', subscription=sub_info)

    await message.answer(
        user_text,
        reply_markup=admin_user_detail_kb(t, user.tg_id)
    )


@router.callback_query(F.data.startswith('admin_grant_sub:'))
async def admin_grant_sub_start(callback: CallbackQuery, t, state: FSMContext):
    """Start granting subscription to user"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    user_id = int(callback.data.split(':')[1])
    await state.update_data(grant_user_id=user_id)
    await state.set_state(AdminUserStates.waiting_grant_days)

    await callback.message.edit_text(t('admin_enter_days'))


@router.message(AdminUserStates.waiting_grant_days)
async def admin_grant_sub_process(message: Message, t, state: FSMContext):
    """Process granting subscription"""
    tg_id = message.from_user.id

    if tg_id != ADMIN_TG_ID:
        return

    try:
        days = int(message.text.strip())
        if days <= 0:
            raise ValueError("Days must be positive")
    except ValueError:
        await message.answer(t('admin_invalid_days'))
        return

    data = await state.get_data()
    user_id = data.get('grant_user_id')
    await state.clear()

    async with get_session() as session:
        user_repo = UserRepository(session)
        now_ts = time.time()

        # Get current subscription end
        current_sub_end = await user_repo.get_subscription_end(user_id)
        if current_sub_end and current_sub_end > now_ts:
            # Extend from current end
            new_end_ts = current_sub_end + (days * 86400)
        else:
            # Start from now
            new_end_ts = now_ts + (days * 86400)

        await user_repo.set_subscription_end(user_id, new_end_ts)

    await message.answer(t('admin_sub_granted', days=days))


@router.callback_query(F.data.startswith('admin_revoke_sub:'))
async def admin_revoke_sub(callback: CallbackQuery, t):
    """Revoke user subscription"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    user_id = int(callback.data.split(':')[1])

    async with get_session() as session:
        user_repo = UserRepository(session)
        # Set subscription end to past time
        await user_repo.set_subscription_end(user_id, time.time() - 86400)

    await callback.answer(t('admin_sub_revoked'), show_alert=True)
    await callback.message.answer(t('admin_sub_revoked'))


@router.callback_query(F.data.startswith('admin_add_balance:'))
async def admin_add_balance_start(callback: CallbackQuery, t, state: FSMContext):
    """Start adding balance to user"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    user_id = int(callback.data.split(':')[1])
    await state.update_data(balance_user_id=user_id)
    await state.set_state(AdminUserStates.waiting_balance_amount)

    await callback.message.edit_text(t('admin_enter_balance_amount'))


@router.message(AdminUserStates.waiting_balance_amount)
async def admin_add_balance_process(message: Message, t, state: FSMContext):
    """Process adding balance"""
    tg_id = message.from_user.id

    if tg_id != ADMIN_TG_ID:
        return

    try:
        amount = Decimal(message.text.strip())
    except (ValueError, ArithmeticError):
        await message.answer(t('admin_invalid_balance_amount'))
        return

    data = await state.get_data()
    user_id = data.get('balance_user_id')
    await state.clear()

    async with get_session() as session:
        user_repo = UserRepository(session)
        try:
            new_balance = await user_repo.change_balance(user_id, amount)
            await message.answer(t('admin_balance_added', amount=amount, new_balance=new_balance))
        except ValueError as e:
            await message.answer(f"Error: {e}")


@router.callback_query(F.data.startswith('admin_view_configs:'))
async def admin_view_configs(callback: CallbackQuery, t):
    """View user configurations"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    user_id = int(callback.data.split(':')[1])

    async with get_session() as session:
        user_repo = UserRepository(session)
        configs = await user_repo.get_configs(user_id)

    if not configs:
        await callback.message.edit_text(
            t('admin_no_configs'),
            reply_markup=admin_user_detail_kb(t, user_id)
        )
        return

    configs_list = []
    for idx, cfg in enumerate(configs, 1):
        configs_list.append(
            f"{idx}. {cfg['name']}\n"
            f"   Server: {cfg['server_id']}\n"
            f"   Username: {cfg['username']}"
        )

    configs_text = '\n\n'.join(configs_list)

    await callback.message.edit_text(
        t('admin_user_configs', tg_id=user_id, configs_list=configs_text),
        reply_markup=admin_user_detail_kb(t, user_id)
    )


@router.callback_query(F.data == 'admin_user_list')
async def admin_user_list(callback: CallbackQuery, t):
    """Show paginated user list"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    # Show first page (page 0)
    await show_user_list_page(callback, t, page=0)


@router.callback_query(F.data.startswith('admin_user_list_page:'))
async def admin_user_list_page_handler(callback: CallbackQuery, t):
    """Handle user list pagination"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    page = int(callback.data.split(':')[1])
    await show_user_list_page(callback, t, page)


async def show_user_list_page(callback: CallbackQuery, t, page: int):
    """Show paginated user list"""
    page_size = 10
    offset = page * page_size

    async with get_session() as session:
        # Get total count
        result = await session.execute(select(func.count(User.tg_id)))
        total_users = result.scalar() or 0

        # Get page of users
        result = await session.execute(
            select(User)
            .order_by(User.created_at.desc())
            .limit(page_size)
            .offset(offset)
        )
        users = result.scalars().all()

    if not users:
        await callback.message.edit_text(
            t('admin_no_recent_payments'),
            reply_markup=admin_users_kb(t)
        )
        return

    user_list = []
    for user in users:
        username = user.username or f"ID{user.tg_id}"
        sub_status = "✅" if user.subscription_end and user.subscription_end > datetime.utcnow() else "❌"
        user_list.append(
            f"{sub_status} {username} (ID: {user.tg_id})\n"
            f"   Balance: {user.balance} RUB | Configs: {user.configs}"
        )

    user_text = '\n\n'.join(user_list)

    total_pages = (total_users + page_size - 1) // page_size

    await callback.message.edit_text(
        f"{user_text}\n\n{t('admin_page', page=page+1, total=total_pages)}",
        reply_markup=admin_user_list_kb(t, page, total_pages)
    )


# ===== END FILE: app/admin/handlers/users.py =====



# ===== START FILE: app/admin/handlers/servers.py =====

"""Admin server management handlers"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, func

from app.admin.keyboards import admin_servers_kb, admin_clear_configs_confirm_kb, admin_instance_detail_kb
from app.core.handlers.utils import safe_answer_callback
from app.utils.config_cleanup import cleanup_expired_configs
from app.repo.db import get_session
from app.repo.models import MarzbanInstance
from app.repo.marzban_client import MarzbanClient
from app.utils.logging import get_logger
from config import ADMIN_TG_ID

LOG = get_logger(__name__)

router = Router()


@router.callback_query(F.data == 'admin_servers')
async def admin_servers(callback: CallbackQuery, t):
    """Show server status and management options"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    async with get_session() as session:
        # Get all Marzban instances
        result = await session.execute(
            select(MarzbanInstance).order_by(MarzbanInstance.priority.asc())
        )
        instances = result.scalars().all()

        # Count active/inactive
        total_instances = len(instances)
        active_instances = sum(1 for i in instances if i.is_active)
        inactive_instances = total_instances - active_instances

    servers_text = t('admin_servers_stats',
                     total=total_instances,
                     active=active_instances,
                     inactive=inactive_instances)

    # Add instance details
    if instances:
        for instance in instances:
            status = t('admin_instance_active') if instance.is_active else t('admin_instance_inactive')
            excluded_count = len(instance.excluded_node_names) if instance.excluded_node_names else 0

            # Try to get node count from Marzban API
            node_count = "N/A"
            if instance.is_active:
                try:
                    client = MarzbanClient()
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


# ===== END FILE: app/admin/handlers/servers.py =====



# ===== START FILE: app/admin/handlers/__init__.py =====

"""Admin handlers router aggregation"""

from aiogram import Router

from . import panel, servers, broadcast, users, payments


def get_router() -> Router:
    """Get admin handlers router with all sub-routers included"""
    admin_router = Router()

    admin_router.include_router(panel.router)
    admin_router.include_router(users.router)
    admin_router.include_router(payments.router)
    admin_router.include_router(servers.router)
    admin_router.include_router(broadcast.router)

    return admin_router


router = get_router()


# ===== END FILE: app/admin/handlers/__init__.py =====



# ===== START FILE: app/admin/handlers/payments.py =====

"""Admin handlers for payment statistics"""

from datetime import datetime, timedelta
from decimal import Decimal
from collections import Counter

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, func

from app.admin.keyboards import admin_payments_kb
from app.repo.db import get_session
from app.repo.models import Payment
from config import ADMIN_TG_ID


router = Router()


async def safe_answer_callback(callback: CallbackQuery):
    """Safely answer callback query to prevent telegram errors"""
    try:
        await callback.answer()
    except Exception:
        pass


@router.callback_query(F.data == 'admin_payments')
async def show_admin_payments(callback: CallbackQuery, t):
    """Show payment statistics"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    async with get_session() as session:
        # Total payments count by status
        result = await session.execute(
            select(
                func.count(Payment.id).label('total'),
                func.sum(func.cast(Payment.status == 'confirmed', func.Integer)).label('confirmed'),
                func.sum(func.cast(Payment.status == 'pending', func.Integer)).label('pending')
            )
        )
        row = result.one()
        total_payments = row.total or 0
        confirmed_payments = row.confirmed or 0
        pending_payments = row.pending or 0
        failed_payments = total_payments - confirmed_payments - pending_payments

        # Total revenue
        result = await session.execute(
            select(func.sum(Payment.amount)).where(Payment.status == 'confirmed')
        )
        total_revenue = result.scalar() or Decimal(0)
        if isinstance(total_revenue, Decimal):
            total_revenue = float(total_revenue)

        # Revenue by time periods
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # Today's revenue
        result = await session.execute(
            select(func.sum(Payment.amount)).where(
                Payment.status == 'confirmed',
                Payment.confirmed_at >= day_ago
            )
        )
        today_revenue = result.scalar() or Decimal(0)
        if isinstance(today_revenue, Decimal):
            today_revenue = float(today_revenue)

        # Week revenue
        result = await session.execute(
            select(func.sum(Payment.amount)).where(
                Payment.status == 'confirmed',
                Payment.confirmed_at >= week_ago
            )
        )
        week_revenue = result.scalar() or Decimal(0)
        if isinstance(week_revenue, Decimal):
            week_revenue = float(week_revenue)

        # Month revenue
        result = await session.execute(
            select(func.sum(Payment.amount)).where(
                Payment.status == 'confirmed',
                Payment.confirmed_at >= month_ago
            )
        )
        month_revenue = result.scalar() or Decimal(0)
        if isinstance(month_revenue, Decimal):
            month_revenue = float(month_revenue)

        # Payment methods breakdown
        result = await session.execute(
            select(Payment.method, func.count(Payment.id), func.sum(Payment.amount))
            .where(Payment.status == 'confirmed')
            .group_by(Payment.method)
        )
        methods_data = result.all()

    stats_text = t('admin_payments_stats',
                   total=total_payments,
                   confirmed=confirmed_payments,
                   pending=pending_payments,
                   failed=failed_payments,
                   total_revenue=total_revenue,
                   today_revenue=today_revenue,
                   week_revenue=week_revenue,
                   month_revenue=month_revenue)

    # Add methods breakdown if available
    if methods_data:
        methods_lines = []
        for method, count, amount in methods_data:
            if amount:
                amount_val = float(amount) if isinstance(amount, Decimal) else amount
                methods_lines.append(f"• {method}: {count} платежей ({amount_val:.2f} RUB)")
            else:
                methods_lines.append(f"• {method}: {count} платежей")

        methods_stats = '\n'.join(methods_lines)
        stats_text += t('admin_payment_methods', methods_stats=methods_stats)

    await callback.message.edit_text(
        stats_text,
        reply_markup=admin_payments_kb(t)
    )


@router.callback_query(F.data == 'admin_recent_payments')
async def show_recent_payments(callback: CallbackQuery, t):
    """Show recent payments list"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    async with get_session() as session:
        # Get last 15 payments
        result = await session.execute(
            select(Payment)
            .order_by(Payment.created_at.desc())
            .limit(15)
        )
        payments = result.scalars().all()

    if not payments:
        await callback.message.edit_text(
            t('admin_no_recent_payments'),
            reply_markup=admin_payments_kb(t)
        )
        return

    payment_lines = []
    for payment in payments:
        date_str = payment.created_at.strftime("%Y-%m-%d %H:%M") if payment.created_at else "N/A"
        amount_val = float(payment.amount) if isinstance(payment.amount, Decimal) else payment.amount

        payment_lines.append(
            t('admin_payment_item',
              amount=amount_val,
              method=payment.method,
              tg_id=payment.tg_id,
              status=payment.status,
              date=date_str)
        )

    payments_text = t('admin_recent_payments') + '\n\n' + '\n\n'.join(payment_lines)

    await callback.message.edit_text(
        payments_text,
        reply_markup=admin_payments_kb(t)
    )


# ===== END FILE: app/admin/handlers/payments.py =====



# ===== START FILE: app/admin/handlers/panel.py =====

"""Admin panel handlers - main sections"""

from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.admin.keyboards import admin_panel_kb
from app.core.handlers.utils import safe_answer_callback
from config import ADMIN_TG_ID

router = Router()


@router.callback_query(F.data == 'admin_panel')
async def show_admin_panel(callback: CallbackQuery, t):
    """Show admin panel - only accessible to admin"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    # Security check: only admin can access
    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    await callback.message.edit_text(
        t('admin_panel_welcome'),
        reply_markup=admin_panel_kb(t)
    )


@router.callback_query(F.data == 'admin_stats')
async def admin_stats(callback: CallbackQuery, t):
    """Show bot statistics"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    from datetime import datetime, timedelta
    from decimal import Decimal
    from sqlalchemy import select, func, case
    from app.repo.db import get_session
    from app.repo.models import User, Payment, Config

    async with get_session() as session:
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        user_stats = select(
            func.count(User.tg_id).label('total_users'),
            func.count(case((User.created_at >= day_ago, 1))).label('new_users_24h'),
            func.count(case((User.created_at >= week_ago, 1))).label('new_users_7d'),
            func.count(case((User.created_at >= month_ago, 1))).label('new_users_30d'),
            func.count(case((User.subscription_end > now, 1))).label('active_subs'),
            func.count(case((User.subscription_end.isnot(None) & (User.subscription_end <= now), 1))).label('expired_subs'),
            func.count(case((User.subscription_end.is_(None), 1))).label('no_subs')
        )

        payment_stats = select(
            func.coalesce(func.sum(case((Payment.status == 'confirmed', Payment.amount))), 0).label('total_revenue'),
            func.coalesce(func.sum(case(((Payment.status == 'confirmed') & (Payment.confirmed_at >= day_ago), Payment.amount))), 0).label('today_revenue'),
            func.coalesce(func.sum(case(((Payment.status == 'confirmed') & (Payment.confirmed_at >= week_ago), Payment.amount))), 0).label('week_revenue'),
            func.coalesce(func.sum(case(((Payment.status == 'confirmed') & (Payment.confirmed_at >= month_ago), Payment.amount))), 0).label('month_revenue')
        )

        config_stats = select(
            func.count(Config.id).label('total_configs'),
            func.count(case((Config.deleted == False, 1))).label('active_configs')
        )

        user_result = (await session.execute(user_stats)).first()
        payment_result = (await session.execute(payment_stats)).first()
        config_result = (await session.execute(config_stats)).first()

        total_users = user_result.total_users or 0
        new_users_24h = user_result.new_users_24h or 0
        new_users_7d = user_result.new_users_7d or 0
        new_users_30d = user_result.new_users_30d or 0
        active_subs = user_result.active_subs or 0
        expired_subs = user_result.expired_subs or 0
        no_subs = user_result.no_subs or 0

        total_revenue = float(payment_result.total_revenue or 0)
        today_revenue = float(payment_result.today_revenue or 0)
        week_revenue = float(payment_result.week_revenue or 0)
        month_revenue = float(payment_result.month_revenue or 0)

        total_configs = config_result.total_configs or 0
        active_configs = config_result.active_configs or 0
        deleted_configs = total_configs - active_configs

    stats_text = t('admin_bot_stats',
                   total_users=total_users,
                   new_users_24h=new_users_24h,
                   new_users_7d=new_users_7d,
                   new_users_30d=new_users_30d,
                   active_subs=active_subs,
                   expired_subs=expired_subs,
                   no_subs=no_subs,
                   total_revenue=total_revenue,
                   today_revenue=today_revenue,
                   week_revenue=week_revenue,
                   month_revenue=month_revenue,
                   total_configs=total_configs,
                   active_configs=active_configs,
                   deleted_configs=deleted_configs)

    await callback.message.edit_text(
        stats_text,
        reply_markup=admin_panel_kb(t)
    )




# ===== END FILE: app/admin/handlers/panel.py =====



# ===== START FILE: app/admin/handlers/broadcast.py =====

"""Admin broadcast handlers"""

import asyncio
from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.admin.keyboards import (
    admin_panel_kb,
    broadcast_settings_kb,
    broadcast_confirm_kb,
    broadcast_cancel_kb
)
from app.repo.db import get_session
from app.repo.user import UserRepository
from app.utils.logging import get_logger
from config import ADMIN_TG_ID

router = Router()
LOG = get_logger(__name__)


async def safe_answer_callback(callback: CallbackQuery):
    """Safely answer callback query to prevent telegram errors"""
    try:
        await callback.answer()
    except Exception:
        pass


class BroadcastState(StatesGroup):
    """FSM states for broadcast functionality"""
    waiting_message = State()
    confirming = State()


@router.callback_query(F.data == 'admin_broadcast')
async def admin_broadcast(callback: CallbackQuery, t, state: FSMContext):
    """Start broadcast - request message"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    await state.set_state(BroadcastState.waiting_message)

    await callback.message.edit_text(
        t('broadcast_enter_message'),
        reply_markup=broadcast_cancel_kb(t)
    )


@router.message(BroadcastState.waiting_message)
async def receive_broadcast_message(message: Message, t, state: FSMContext):
    """Receive broadcast message and show settings"""
    tg_id = message.from_user.id

    if tg_id != ADMIN_TG_ID:
        return

    # Save message to state
    await state.update_data(broadcast_text=message.text or message.caption)
    await state.update_data(message_obj=message)
    await state.set_state(BroadcastState.confirming)

    # Show settings keyboard
    await message.answer(
        t('broadcast_settings_prompt'),
        reply_markup=broadcast_settings_kb(t)
    )


@router.callback_query(F.data.startswith('broadcast_target_'))
async def set_broadcast_target(callback: CallbackQuery, t, state: FSMContext):
    """Set broadcast target audience"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    target = callback.data.split('_')[-1]  # 'all' or 'subscribed'
    await state.update_data(target=target)

    # Update keyboard to show selection
    data = await state.get_data()
    current_time = data.get('schedule_time', 'now')

    await callback.message.edit_text(
        t('broadcast_settings_prompt'),
        reply_markup=broadcast_settings_kb(t, selected_target=target, selected_time=current_time)
    )


@router.callback_query(F.data.startswith('broadcast_time_'))
async def set_broadcast_time(callback: CallbackQuery, t, state: FSMContext):
    """Set broadcast time"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    schedule_time = callback.data.split('_')[-1]  # 'now'
    await state.update_data(schedule_time=schedule_time)

    # Update keyboard to show selection
    data = await state.get_data()
    current_target = data.get('target', 'all')

    await callback.message.edit_text(
        t('broadcast_settings_prompt'),
        reply_markup=broadcast_settings_kb(t, selected_target=current_target, selected_time=schedule_time)
    )


@router.callback_query(F.data == 'broadcast_confirm')
async def confirm_broadcast(callback: CallbackQuery, t, state: FSMContext):
    """Confirm and execute broadcast"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    data = await state.get_data()
    broadcast_text = data.get('broadcast_text')
    target = data.get('target', 'all')
    schedule_time = data.get('schedule_time', 'now')

    if not broadcast_text:
        await callback.message.edit_text(
            t('broadcast_error_no_message'),
            reply_markup=admin_panel_kb(t)
        )
        await state.clear()
        return

    # Show confirmation
    preview_text = t('broadcast_preview',
                     message=broadcast_text[:200] + ('...' if len(broadcast_text) > 200 else ''),
                     target=t(f'broadcast_target_{target}'),
                     time=t(f'broadcast_time_{schedule_time}'))

    await callback.message.edit_text(
        preview_text,
        reply_markup=broadcast_confirm_kb(t)
    )


@router.callback_query(F.data == 'broadcast_execute')
async def execute_broadcast(callback: CallbackQuery, t, state: FSMContext):
    """Execute the broadcast"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    data = await state.get_data()
    broadcast_text = data.get('broadcast_text')
    target = data.get('target', 'all')

    await callback.message.edit_text(t('broadcast_in_progress'))

    # Get users to send to
    async with get_session() as session:
        user_repo = UserRepository(session)

        if target == 'subscribed':
            # Only users with notifications enabled
            users = await user_repo.get_users_with_notifications()
        else:
            # All users
            users = await user_repo.get_all_users()

    # Execute broadcast
    success_count = 0
    failed_count = 0

    for user in users:
        try:
            await callback.bot.send_message(
                chat_id=user.tg_id,
                text=broadcast_text
            )
            success_count += 1
            # Small delay to avoid rate limits
            await asyncio.sleep(0.05)
        except Exception as e:
            LOG.error(f"Failed to send broadcast to user {user.tg_id}: {e}")
            failed_count += 1

    # Show results
    result_text = t('broadcast_completed',
                    total=len(users),
                    success=success_count,
                    failed=failed_count)

    await callback.message.edit_text(
        result_text,
        reply_markup=admin_panel_kb(t)
    )

    await state.clear()
    LOG.info(f"Broadcast completed: {success_count} sent, {failed_count} failed out of {len(users)} total")


@router.callback_query(F.data == 'broadcast_cancel')
async def cancel_broadcast(callback: CallbackQuery, t, state: FSMContext):
    """Cancel broadcast"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id != ADMIN_TG_ID:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    await state.clear()

    await callback.message.edit_text(
        t('broadcast_cancelled'),
        reply_markup=admin_panel_kb(t)
    )


# ===== END FILE: app/admin/handlers/broadcast.py =====



# ===== START FILE: app/repo/db.py =====

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager

from config import DATABASE_URL

print("DATABASE_URL:", DATABASE_URL)

engine: AsyncEngine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    pool_size=20, 
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

@asynccontextmanager
async def get_session():
    async with SessionLocal() as session:
        yield session

async def close_db():
    await engine.dispose()


# ===== END FILE: app/repo/db.py =====



# ===== START FILE: app/repo/marzban_client.py =====

from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from aiomarzban import MarzbanAPI, UserDataLimitResetStrategy
from sqlalchemy import select

from app.repo.models import MarzbanInstance
from app.repo.db import get_session
from app.utils.logging import get_logger
from config import MAX_IPS_PER_CONFIG

LOG = get_logger(__name__)


@dataclass
class NodeLoadMetrics:
    node_id: int
    node_name: str
    active_users: int
    usage_coefficient: float
    uplink: int
    downlink: int
    instance_id: str

    @property
    def load_score(self) -> float:
        total_traffic_gb = (self.uplink + self.downlink) / (1024 ** 3)

        user_weight = 100.0
        traffic_weight = 1.0

        score = (
            (self.active_users * user_weight * self.usage_coefficient) +
            (total_traffic_gb * traffic_weight)
        )

        return score


class MarzbanClient:
    def __init__(self):
        self._instances_cache: Dict[str, MarzbanAPI] = {}

    async def _get_active_instances(self) -> List[MarzbanInstance]:
        async with get_session() as session:
            result = await session.execute(
                select(MarzbanInstance)
                .where(MarzbanInstance.is_active == True)
                .order_by(MarzbanInstance.priority.asc())
            )
            return list(result.scalars().all())

    def _get_or_create_api(self, instance: MarzbanInstance) -> MarzbanAPI:
        if instance.id not in self._instances_cache:
            self._instances_cache[instance.id] = MarzbanAPI(
                address=instance.base_url,
                username=instance.username,
                password=instance.password,
                default_proxies={"vless": {"flow": ""}}
            )
        return self._instances_cache[instance.id]

    async def _get_node_metrics(
        self,
        instance: MarzbanInstance,
        api: MarzbanAPI
    ) -> List[NodeLoadMetrics]:
        from app.utils.redis import get_redis
        import json

        redis_key = f"marzban:{instance.id}:node_metrics"

        try:
            redis = await get_redis()
            cached = await redis.get(redis_key)
            if cached:
                cached_data = json.loads(cached)
                return [
                    NodeLoadMetrics(
                        node_id=m['node_id'],
                        node_name=m['node_name'],
                        active_users=m['active_users'],
                        usage_coefficient=m['usage_coefficient'],
                        uplink=m['uplink'],
                        downlink=m['downlink'],
                        instance_id=m['instance_id']
                    )
                    for m in cached_data
                ]
        except Exception as e:
            LOG.warning(f"Redis error reading node metrics for {instance.id}: {e}")

        try:
            try:
                nodes = await api.get_nodes()
            except Exception as e:
                LOG.debug(f"Nodes API not available for instance {instance.id}: {e}")
                return []

            excluded_names = instance.excluded_node_names or []
            if excluded_names:
                original_count = len(nodes)
                nodes = [n for n in nodes if n.name not in excluded_names]
                if len(nodes) < original_count:
                    LOG.info(f"Excluded {original_count - len(nodes)} node(s) from instance {instance.id}: {excluded_names}")

            if not nodes:
                LOG.warning(f"All nodes excluded for instance {instance.id}")
                return []

            usage_map = {}
            try:
                usage_response = await api.get_nodes_usage()
                usage_map = {
                    u.node_id: u for u in usage_response.usages
                    if u.node_id is not None
                }
            except Exception as e:
                LOG.debug(f"Node usage API not available for instance {instance.id}: {e}")

            try:
                users = await api.get_users(limit=10000)
                total_active_users = sum(1 for u in users.users if u.status == 'active')
            except Exception as e:
                LOG.debug(f"Failed to get users for instance {instance.id}: {e}")
                total_active_users = 0

            node_count = len(nodes)
            avg_users_per_node = total_active_users / node_count if node_count > 0 else 0

            metrics = []
            for node in nodes:
                usage = usage_map.get(node.id)
                uplink = usage.uplink if usage else 0
                downlink = usage.downlink if usage else 0

                metrics.append(NodeLoadMetrics(
                    node_id=node.id,
                    node_name=node.name,
                    active_users=int(avg_users_per_node),
                    usage_coefficient=node.usage_coefficient or 1.0,
                    uplink=uplink,
                    downlink=downlink,
                    instance_id=instance.id
                ))

            try:
                redis = await get_redis()
                cache_data = [
                    {
                        'node_id': m.node_id,
                        'node_name': m.node_name,
                        'active_users': m.active_users,
                        'usage_coefficient': m.usage_coefficient,
                        'uplink': m.uplink,
                        'downlink': m.downlink,
                        'instance_id': m.instance_id
                    }
                    for m in metrics
                ]
                await redis.setex(redis_key, 120, json.dumps(cache_data))
            except Exception as e:
                LOG.warning(f"Redis error caching node metrics for {instance.id}: {e}")

            return metrics

        except Exception as e:
            LOG.error(f"Failed to get node metrics for instance {instance.id}: {e}")
            return []

    async def get_best_instance_and_node(
        self,
        manual_instance_id: Optional[str] = None
    ) -> Tuple[MarzbanInstance, MarzbanAPI, Optional[int]]:
        instances = await self._get_active_instances()

        if not instances:
            raise ValueError("No active Marzban instances available")

        # Manual instance selection (for future feature: user chooses server)
        if manual_instance_id:
            selected_instance = next(
                (inst for inst in instances if inst.id == manual_instance_id),
                None
            )
            if not selected_instance:
                raise ValueError(f"Marzban instance {manual_instance_id} not found or inactive")

            api = self._get_or_create_api(selected_instance)
            LOG.info(f"Manually selected instance: {manual_instance_id}")
            return selected_instance, api, None

        # Automatic selection: find least loaded node across all instances
        all_metrics: List[NodeLoadMetrics] = []

        for instance in instances:
            api = self._get_or_create_api(instance)
            metrics = await self._get_node_metrics(instance, api)
            all_metrics.extend(metrics)

        if not all_metrics:
            # Fallback to first available instance without node selection
            first_instance = instances[0]
            api = self._get_or_create_api(first_instance)
            LOG.warning("No node metrics available, using first instance without node selection")
            return first_instance, api, None

        # Sort by load score (ascending = least loaded first)
        all_metrics.sort(key=lambda m: m.load_score)
        best_metric = all_metrics[0]

        # Get the instance for the best node
        selected_instance = next(
            inst for inst in instances if inst.id == best_metric.instance_id
        )
        api = self._get_or_create_api(selected_instance)

        LOG.info(
            f"Selected node {best_metric.node_name} (ID: {best_metric.node_id}) "
            f"on instance {selected_instance.id} with load score {best_metric.load_score:.2f}"
        )

        return selected_instance, api, best_metric.node_id

    async def add_user(
        self,
        username: str,
        days: int,
        data_limit: int = 300,
        max_ips: Optional[int] = None,
        manual_instance_id: Optional[str] = None
    ):
        """
        Create a new VPN user on the least loaded node.

        Args:
            username: Unique username for the user
            days: Subscription duration in days
            data_limit: Traffic limit in GB
            max_ips: Maximum concurrent IPs (devices) allowed. Defaults to MAX_IPS_PER_CONFIG from config
            manual_instance_id: Optional instance ID for manual selection

        Returns:
            User object from Marzban API with subscription links

        Raises:
            ValueError: If user creation fails or no instances available
        """
        instance, api, node_id = await self.get_best_instance_and_node(manual_instance_id)

        # Use default from config if not specified
        if max_ips is None:
            max_ips = MAX_IPS_PER_CONFIG

        try:
            # Note: aiomarzban v1.0.3 doesn't support ip_limit in UserCreate model
            # We need to manually add it to the request payload

            # First, prepare the user data using the standard method
            from aiomarzban.models import UserCreate, UserStatusCreate
            from aiomarzban.utils import future_unix_time, gb_to_bytes
            from aiomarzban.enums import Methods

            expire = future_unix_time(days=days)

            # Create the user data model
            user_data = UserCreate(
                proxies=api.default_proxies,
                expire=expire,
                data_limit=gb_to_bytes(data_limit),
                data_limit_reset_strategy=UserDataLimitResetStrategy.month,
                inbounds=api.default_inbounds,
                username=username,
                status=UserStatusCreate.active,
            )

            # Convert to dict and add ip_limit (not supported by aiomarzban model)
            payload = user_data.model_dump()
            payload['ip_limit'] = max_ips

            # Make the request directly using the API's internal method
            resp = await api._request(Methods.POST, "/user", data=payload)

            # Parse response manually
            from aiomarzban.models import UserResponse
            new_user = UserResponse(**resp)

            if not new_user.links:
                raise ValueError("No VLESS link returned from Marzban")

            LOG.info(
                f"Created user {username} on instance {instance.id} "
                f"(target node: {node_id if node_id else 'auto'}, max_ips: {max_ips})"
            )

            return new_user

        except Exception as e:
            LOG.error(f"Failed to add user {username} on instance {instance.id}: {e}")
            raise

    async def remove_user(self, username: str, instance_id: Optional[str] = None):
        """
        Remove a user from Marzban.

        Args:
            username: Username to remove
            instance_id: If known, specify the instance; otherwise tries all instances
        """
        if instance_id:
            instances = [inst for inst in await self._get_active_instances() if inst.id == instance_id]
        else:
            instances = await self._get_active_instances()

        for instance in instances:
            try:
                api = self._get_or_create_api(instance)
                await api.remove_user(username)
                LOG.info(f"Removed user {username} from instance {instance.id}")
                return
            except Exception as e:
                LOG.debug(f"User {username} not found on instance {instance.id}: {e}")
                continue

        LOG.warning(f"User {username} not found on any instance")

    async def get_user(self, username: str, instance_id: Optional[str] = None):
        """
        Get user info from Marzban.

        Args:
            username: Username to fetch
            instance_id: If known, specify the instance; otherwise tries all instances

        Returns:
            User object or None if not found
        """
        if instance_id:
            instances = [inst for inst in await self._get_active_instances() if inst.id == instance_id]
        else:
            instances = await self._get_active_instances()

        for instance in instances:
            try:
                api = self._get_or_create_api(instance)
                user = await api.get_user(username)
                return user
            except Exception:
                continue

        return None

    async def modify_user(
        self,
        username: str,
        instance_id: Optional[str] = None,
        max_ips: Optional[int] = None,
        **kwargs
    ):
        """
        Modify user settings in Marzban.

        Args:
            username: Username to modify
            instance_id: If known, specify the instance; otherwise tries all instances
            max_ips: Maximum concurrent IPs (devices) allowed
            **kwargs: Parameters to update (expire, data_limit, etc.)
        """
        if instance_id:
            instances = [inst for inst in await self._get_active_instances() if inst.id == instance_id]
        else:
            instances = await self._get_active_instances()

        for instance in instances:
            try:
                api = self._get_or_create_api(instance)

                # If max_ips is specified, we need to add it to the payload manually
                if max_ips is not None:
                    from aiomarzban.models import UserModify
                    from aiomarzban.utils import gb_to_bytes
                    from aiomarzban.enums import Methods

                    # Convert data_limit to bytes if present
                    if 'data_limit' in kwargs and kwargs['data_limit'] is not None:
                        kwargs['data_limit'] = gb_to_bytes(kwargs['data_limit'])

                    # Create UserModify model
                    user_data = UserModify(**kwargs)

                    # Convert to dict and add ip_limit
                    payload = user_data.model_dump(exclude_none=True)
                    payload['ip_limit'] = max_ips

                    # Make request directly
                    await api._request(Methods.PUT, f"/user/{username}", data=payload)
                    LOG.info(f"Modified user {username} on instance {instance.id} (max_ips: {max_ips})")
                else:
                    # Use standard method if no ip_limit needed
                    await api.modify_user(username, **kwargs)
                    LOG.info(f"Modified user {username} on instance {instance.id}")

                return
            except Exception:
                continue

        raise ValueError(f"User {username} not found on any instance")


# ===== END FILE: app/repo/marzban_client.py =====



# ===== START FILE: app/repo/base.py =====

from .db import get_session, AsyncSession
import redis.asyncio as redis

class BaseRepository:
    def __init__(self, session: AsyncSession, redis_client: redis.Redis = None):
        self.session = session
        self.redis = redis_client

    async def get_redis(self) -> redis.Redis:
        if self.redis is None:
            raise RuntimeError("Redis client not provided")
        return self.redis

# ===== END FILE: app/repo/base.py =====



# ===== START FILE: app/repo/user.py =====

import json
import re
import time
from decimal import Decimal
from datetime import datetime
from typing import Optional, List, Dict
from urllib.parse import urlparse, urlunparse

from sqlalchemy import select, update, func

from .models import User, Config, Server
from .db import get_session
from .marzban_client import MarzbanClient
from app.utils.logging import get_logger
from .base import BaseRepository
from config import REFERRAL_BONUS, REDIS_TTL

LOG = get_logger(__name__)

CACHE_TTL_BALANCE = 60
CACHE_TTL_CONFIGS = 600
CACHE_TTL_SUB_END = 3600
CACHE_TTL_LANG = 86400
CACHE_TTL_NOTIFICATIONS = 3600

class UserRepository(BaseRepository):

    @staticmethod
    def _validate_username(username: str) -> bool:
        return bool(re.match(r'^orbit_\d+$', username))

    # ----------------------------
    # Balance
    # ----------------------------
    async def get_balance(self, tg_id: int) -> Decimal:
        """
        Get user balance with Redis caching and automatic fallback to database.

        CRITICAL: Redis failures are handled gracefully - if Redis is unavailable,
        the method falls back to database without failing.
        """
        redis = await self.get_redis()

        # Try to get from cache, but don't fail if Redis is down
        try:
            cached = await redis.get(f"user:{tg_id}:balance")
            if cached:
                return Decimal(cached)
        except Exception as e:
            LOG.warning(f"Redis error reading balance for user {tg_id}: {e}")
            # Continue to database fallback

        # Fallback to database
        result = await self.session.execute(select(User.balance).filter_by(tg_id=tg_id))
        balance = result.scalar() or Decimal("0.0")

        # Try to cache the result, but don't fail if Redis is down
        try:
            await redis.setex(f"user:{tg_id}:balance", CACHE_TTL_BALANCE, str(balance))
        except Exception as e:
            LOG.warning(f"Redis error caching balance for user {tg_id}: {e}")
            # Continue anyway - database read succeeded

        return balance

    async def change_balance(self, tg_id: int, amount: Decimal) -> Decimal:
        """
        Change user balance atomically with SELECT FOR UPDATE lock.

        CRITICAL: This method now uses row-level locking to prevent lost updates
        from concurrent balance modifications (race conditions).

        Returns:
            New balance after change

        Raises:
            ValueError: If user not found or insufficient balance
        """
        redis = await self.get_redis()

        # CRITICAL FIX: Lock user row BEFORE reading balance
        # This prevents race conditions where two concurrent updates both read
        # the same balance value and one update gets lost
        result = await self.session.execute(
            select(User)
            .where(User.tg_id == tg_id)
            .with_for_update()  # Acquire exclusive lock on row
        )
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"User {tg_id} not found")

        old_balance = user.balance
        new_balance = old_balance + amount

        # Prevent negative balance
        if new_balance < 0:
            raise ValueError(f"Insufficient balance: {old_balance} + {amount} = {new_balance}")

        # Update locked row
        user.balance = new_balance
        await self.session.commit()

        LOG.info(f"Balance changed for user {tg_id}: {old_balance} → {new_balance} ({amount:+.2f})")

        # Invalidate cache after successful commit (tolerate Redis failures)
        try:
            await redis.delete(f"user:{tg_id}:balance")
        except Exception as e:
            LOG.warning(f"Redis error invalidating balance cache for user {tg_id}: {e}")
            # Don't fail the transaction - balance was successfully updated in database

        return new_balance

    # ----------------------------
    # Add user if not exists
    # ----------------------------
    async def add_if_not_exists(
        self,
        tg_id: int,
        username: str,
        referrer_id: Optional[int] = None
    ) -> bool:
        redis = await self.get_redis()
        now = datetime.utcnow()

        user = await self.session.get(User, tg_id)
        if user:
            return False

        new_user = User(
            tg_id=tg_id,
            username=username,
            balance=0,
            configs=0,
            lang='ru',
            referrer_id=referrer_id,
            first_buy=True,
            notifications=True,
            created_at=now
        )
        self.session.add(new_user)

        if referrer_id:
            await self.session.execute(
                update(User)
                .where(User.tg_id == referrer_id)
                .values(balance=User.balance + REFERRAL_BONUS)
            )
            await redis.delete(f"user:{referrer_id}:balance")

        await self.session.commit()
        return True

    # ----------------------------
    # Configs
    # ----------------------------
    async def get_configs(self, tg_id: int) -> List[Dict]:
        redis = await self.get_redis()
        key = f"user:{tg_id}:configs"
        cached = await redis.get(key)
        if cached:
            return json.loads(cached)

        result = await self.session.execute(
            select(Config).filter_by(tg_id=tg_id, deleted=False).order_by(Config.id)
        )
        configs = [dict(
            id=c.id,
            name=c.name,
            vless_link=c.vless_link,
            server_id=c.server_id,
            username=c.username
        ) for c in result.scalars().all()]

        await redis.setex(key, CACHE_TTL_CONFIGS, json.dumps(configs))
        return configs

    async def add_config(self, tg_id: int, vless_link: str, server_id: str, username: str) -> Dict:
        redis = await self.get_redis()

        result = await self.session.execute(
            select(func.count(Config.id)).filter_by(tg_id=tg_id, deleted=False)
        )
        count = result.scalar() or 0
        new_name = f"Configuration {count + 1}"

        cfg = Config(
            tg_id=tg_id,
            name=new_name,
            vless_link=vless_link,
            server_id=server_id,
            username=username,
            deleted=False
        )
        self.session.add(cfg)

        await self.session.execute(
            update(User)
            .where(User.tg_id == tg_id)
            .values(configs=User.configs + 1)
        )

        await self.session.commit()

        await redis.delete(f"user:{tg_id}:configs")
        return {
            "id": cfg.id,
            "name": cfg.name,
            "vless_link": cfg.vless_link,
            "server_id": cfg.server_id,
            "username": cfg.username
        }

    # ----------------------------
    # Marzban safe wrappers
    # ----------------------------
    async def _safe_remove_marzban_user(self, username: str):
        marzban_client = MarzbanClient()
        try:
            await marzban_client.remove_user(username)
            LOG.info("Removed marzban user %s", username)
        except Exception as e:
            LOG.warning("Failed to remove marzban user %s: %s", username, e)
            try:
                await marzban_client.modify_user(username, expire=int(time.time() - 86400))
                LOG.info("Expired marzban user %s as fallback", username)
            except Exception as ex:
                LOG.error("Failed to expire marzban user %s during fallback: %s", username, ex)

    async def _safe_modify_marzban_user(self, username: str, expire_ts: int):
        marzban_client = MarzbanClient()
        try:
            await marzban_client.modify_user(username, expire=expire_ts)
            LOG.info("Modified marzban user %s expire=%s", username, expire_ts)
        except Exception as e:
            LOG.error("Failed to modify marzban user %s expire=%s: %s", username, expire_ts, e)

    # ----------------------------
    # Delete config (clean delete)
    # ----------------------------
    async def delete_config(self, cfg_id: int, tg_id: int):
        redis = await self.get_redis()
        username = None

        cfg = await self.session.get(Config, cfg_id)
        if not cfg or cfg.tg_id != tg_id or cfg.deleted:
            LOG.debug("delete_config: config not found or already deleted id=%s tg=%s", cfg_id, tg_id)
            return

        username = cfg.username

        cfg.deleted = True
        await self.session.execute(
            update(User)
            .where(User.tg_id == tg_id)
            .values(configs=func.greatest(User.configs - 1, 0))
        )
        await self.session.commit()

        if username:
            await self._safe_remove_marzban_user(username)

        await redis.delete(f"user:{tg_id}:configs")

    # ----------------------------
    # Language
    # ----------------------------
    async def get_lang(self, tg_id: int) -> str:
        redis = await self.get_redis()
        key = f"user:{tg_id}:lang"
        cached = await redis.get(key)
        if cached:
            return cached

        user = await self.session.get(User, tg_id)
        lang = user.lang if user else "ru"

        await redis.setex(key, CACHE_TTL_LANG, lang)
        return lang

    async def set_lang(self, tg_id: int, lang: str):
        redis = await self.get_redis()
        await redis.setex(f"user:{tg_id}:lang", CACHE_TTL_LANG, lang)

        await self.session.execute(update(User).where(User.tg_id == tg_id).values(lang=lang))
        await self.session.commit()

    # ----------------------------
    # Notifications
    # ----------------------------
    async def get_notifications(self, tg_id: int) -> bool:
        redis = await self.get_redis()
        key = f"user:{tg_id}:notifications"

        try:
            cached = await redis.get(key)
            if cached is not None:
                return cached == "1"
        except Exception as e:
            LOG.warning(f"Redis error reading notifications for user {tg_id}: {e}")

        user = await self.session.get(User, tg_id)
        notifications = user.notifications if user and user.notifications is not None else True

        try:
            await redis.setex(key, CACHE_TTL_NOTIFICATIONS, "1" if notifications else "0")
        except Exception as e:
            LOG.warning(f"Redis error caching notifications for user {tg_id}: {e}")

        return notifications

    async def toggle_notifications(self, tg_id: int) -> bool:
        redis = await self.get_redis()

        user = await self.session.get(User, tg_id)
        if not user:
            LOG.warning(f"User {tg_id} not found during toggle_notifications")
            return True

        new_state = not (user.notifications if user.notifications is not None else True)

        await self.session.execute(
            update(User).where(User.tg_id == tg_id).values(notifications=new_state)
        )
        await self.session.commit()

        try:
            await redis.setex(f"user:{tg_id}:notifications", CACHE_TTL_NOTIFICATIONS, "1" if new_state else "0")
        except Exception as e:
            LOG.warning(f"Redis error updating notifications cache for user {tg_id}: {e}")

        LOG.info(f"Notifications toggled for user {tg_id}: {new_state}")
        return new_state

    # ----------------------------
    # Subscription helpers
    # ----------------------------
    async def get_subscription_end(self, tg_id: int) -> Optional[float]:
        redis = await self.get_redis()
        key = f"user:{tg_id}:sub_end"
        cached = await redis.get(key)
        if cached:
            return float(cached) if cached != 'None' else None

        result = await self.session.execute(select(User.subscription_end).where(User.tg_id == tg_id))
        sub_end_dt = result.scalar()
        sub_end = sub_end_dt.timestamp() if sub_end_dt else None

        await redis.setex(key, CACHE_TTL_SUB_END, str(sub_end) if sub_end else 'None')
        return sub_end

    async def set_subscription_end(self, tg_id: int, timestamp: float):
        redis = await self.get_redis()
        expire_dt = datetime.fromtimestamp(timestamp)

        await self.session.execute(
            update(User).where(User.tg_id == tg_id).values(subscription_end=expire_dt)
        )
        result = await self.session.execute(select(Config.username).where(Config.tg_id == tg_id, Config.deleted == False))
        usernames = [r[0] for r in result.all()]
        await self.session.commit()

        await redis.setex(f"user:{tg_id}:sub_end", CACHE_TTL_SUB_END, str(timestamp))

        if usernames:
            import asyncio
            await asyncio.gather(*[
                self._safe_modify_marzban_user(username, int(timestamp))
                for username in usernames
            ], return_exceptions=True)

    async def has_active_subscription(self, tg_id: int) -> bool:
        sub_end = await self.get_subscription_end(tg_id)
        if not sub_end:
            return False
        return time.time() < sub_end

    async def buy_subscription(self, tg_id: int, days: int, price: float) -> bool:
        redis = await self.get_redis()
        price_decimal = Decimal(str(price))
        now_ts = time.time()

        result = await self.session.execute(
            select(User).where(User.tg_id == tg_id).with_for_update()
        )
        user = result.scalar_one_or_none()
        if not user:
            LOG.warning(f"User {tg_id} not found during subscription purchase")
            return False

        if user.balance < price_decimal:
            LOG.info(f"User {tg_id} has insufficient balance: {user.balance} < {price_decimal}")
            return False

        new_balance = user.balance - price_decimal
        user.balance = new_balance

        current_sub_ts = user.subscription_end.timestamp() if user.subscription_end else now_ts
        new_end_ts = max(current_sub_ts, now_ts) + days * 86400
        user.subscription_end = datetime.fromtimestamp(new_end_ts)

        if user.first_buy:
            user.first_buy = False
            if user.referrer_id:
                ref_result = await self.session.execute(
                    select(User).where(User.tg_id == user.referrer_id)
                )
                ref_user = ref_result.scalar_one_or_none()
                if ref_user:
                    ref_user.balance += Decimal(str(REFERRAL_BONUS))
                    await redis.delete(f"user:{user.referrer_id}:balance")
                    LOG.info(f"Referral bonus {REFERRAL_BONUS} credited to {user.referrer_id} from {tg_id}")

        result = await self.session.execute(select(Config.username).where(Config.tg_id == tg_id, Config.deleted == False))
        usernames = [r[0] for r in result.all()]

        await self.session.commit()

        await redis.setex(f"user:{tg_id}:sub_end", CACHE_TTL_SUB_END, str(new_end_ts))
        await redis.setex(f"user:{tg_id}:balance", CACHE_TTL_BALANCE, str(new_balance))

        if usernames:
            import asyncio
            await asyncio.gather(*[
                self._safe_modify_marzban_user(username, int(new_end_ts))
                for username in usernames
            ], return_exceptions=True)

        LOG.info(f"User {tg_id} purchased {days} days for {price} RUB. New balance: {new_balance}")
        return True

    async def create_and_add_config(
        self,
        tg_id: int,
        manual_instance_id: Optional[str] = None
    ) -> Dict:

        redis = await self.get_redis()
        username = f'orbit_{tg_id}'

        if not self._validate_username(username):
            raise ValueError("Invalid username format")

        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.tg_id == tg_id).with_for_update()
            )
            user = result.scalar_one_or_none()
            if not user or not user.subscription_end or time.time() >= user.subscription_end.timestamp():
                raise ValueError("No active subscription or subscription expired")

            result = await session.execute(
                select(func.count(Config.id)).where(
                    Config.tg_id == tg_id,
                    Config.deleted == False
                )
            )
            count = result.scalar()
            if count >= 1:
                raise ValueError("Max configs reached (limit: 1)")

            days_remaining = max(1, int((user.subscription_end.timestamp() - time.time()) / 86400) + 1)

        marzban_client = MarzbanClient()

        try:
            new_user = await marzban_client.add_user(
                username=username,
                days=days_remaining,
                manual_instance_id=manual_instance_id
            )
            if not new_user.links:
                raise ValueError("No VLESS link returned from Marzban")
            vless_link = new_user.links[0]

            instance, _, _ = await marzban_client.get_best_instance_and_node(manual_instance_id)
            instance_id = instance.id

        except Exception as e:
            error_str = str(e).lower()
            if "already exists" in error_str or "409" in error_str:
                LOG.warning("Marzban user %s already exists; attempting remove+recreate", username)
                await marzban_client.remove_user(username)
                new_user = await marzban_client.add_user(
                    username=username,
                    days=days_remaining,
                    manual_instance_id=manual_instance_id
                )
                if not new_user.links:
                    raise ValueError("No VLESS link after recreate")
                vless_link = new_user.links[0]
                instance, _, _ = await marzban_client.get_best_instance_and_node(manual_instance_id)
                instance_id = instance.id
            else:
                LOG.error("Marzban add_user failed for %s: %s", username, e)
                raise

        parsed = urlparse(vless_link)
        vless_link = urlunparse(parsed._replace(fragment="OrbitVPN"))

        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.tg_id == tg_id).with_for_update()
            )
            user = result.scalar_one_or_none()
            if not user or not user.subscription_end or time.time() >= user.subscription_end.timestamp():
                await marzban_client.remove_user(username, instance_id)
                raise ValueError("Subscription expired during config creation")

            result = await session.execute(
                select(func.count(Config.id)).where(Config.tg_id == tg_id, Config.deleted == False)
            )
            count = result.scalar()
            if count >= 1:
                await marzban_client.remove_user(username, instance_id)
                raise ValueError("Max configs reached during creation")

            new_name = f"Configuration {count + 1}"
            cfg = Config(
                tg_id=tg_id,
                name=new_name,
                vless_link=vless_link,
                server_id=instance_id,
                username=username,
                deleted=False
            )
            session.add(cfg)
            await session.execute(
                update(User).where(User.tg_id == tg_id).values(configs=User.configs + 1)
            )
            await session.commit()

        await redis.delete(f"user:{tg_id}:configs")

        LOG.info("Config created for user %s on Marzban instance %s", tg_id, instance_id)
        return {
            "id": cfg.id,
            "name": cfg.name,
            "vless_link": cfg.vless_link,
            "server_id": cfg.server_id,
            "username": cfg.username
        }

    async def get_all_users(self) -> List[User]:
        """Get all users for broadcast"""
        session = self.session
        result = await session.execute(select(User))
        return list(result.scalars().all())

    async def get_users_with_notifications(self) -> List[User]:
        """Get users with notifications enabled for targeted broadcast"""
        session = self.session
        result = await session.execute(
            select(User).where(User.notifications == True)
        )
        return list(result.scalars().all())

# ===== END FILE: app/repo/user.py =====



# ===== START FILE: app/repo/payments.py =====

from decimal import Decimal
from typing import Optional, List, Dict, Union
from datetime import datetime, timedelta
import asyncio


from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.payments.models import PaymentMethod
from app.repo.models import Payment as PaymentModel, TonTransaction
from .db import get_session
from app.utils.logging import get_logger
from .base import BaseRepository
from config import PAYMENT_TIMEOUT_MINUTES

LOG = get_logger(__name__)


class PaymentRepository(BaseRepository):
    async def create_payment(
        self,
        tg_id: int,
        method: str,
        amount: Decimal,
        currency: str,
        status: str = 'pending',
        comment: Optional[str] = None,
        expected_crypto_amount: Optional[Decimal] = None
    ) -> int:
        # Set expiration time for pending payments
        expires_at = None
        if status == 'pending':
            expires_at = datetime.utcnow() + timedelta(minutes=PAYMENT_TIMEOUT_MINUTES)

        payment = PaymentModel(
            tg_id=tg_id,
            method=method,
            amount=amount,
            currency=currency,
            status=status,
            comment=comment,
            expected_crypto_amount=expected_crypto_amount,
            expires_at=expires_at
        )
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment.id

    async def get_payment(self, payment_id: int) -> Optional[Dict]:
        result = await self.session.execute(select(PaymentModel).where(PaymentModel.id == payment_id))
        payment = result.scalar_one_or_none()
        return payment.__dict__ if payment else None

    async def update_payment_status(
        self,
        payment_id: int,
        status: str,
        tx_hash: Optional[str] = None
    ):
        stmt = update(PaymentModel).where(PaymentModel.id == payment_id).values(status=status)
        if status == 'confirmed':
            stmt = stmt.values(tx_hash=tx_hash, confirmed_at=datetime.utcnow())
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_pending_payments(
        self,
        method: Optional[Union[str, PaymentMethod]] = None
    ) -> List[Dict]:
        query = select(PaymentModel).where(PaymentModel.status == 'pending')
        if method:
            m = method.value if isinstance(method, PaymentMethod) else method
            query = query.where(PaymentModel.method == m)
        query = query.order_by(PaymentModel.created_at)
        result = await self.session.execute(query)
        payments = result.scalars().all()
        return [p.__dict__ for p in payments]

    async def mark_transaction_processed(self, tx_hash: str):
        stmt = update(TonTransaction).where(TonTransaction.tx_hash == tx_hash).values(
            processed_at=datetime.utcnow()
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def mark_failed_old_payments(self):
        threshold = datetime.utcnow() - timedelta(minutes=PAYMENT_TIMEOUT_MINUTES)
        stmt = update(PaymentModel).where(
            PaymentModel.status == 'pending',
            PaymentModel.created_at < threshold
        ).values(status='expired')
        await self.session.execute(stmt)
        await self.session.commit()

    async def mark_payment_processed(self, payment_id: str, tg_id: int, amount: Decimal) -> bool:
        """Mark Telegram Stars payment as processed"""
        result = await self.session.execute(
            select(PaymentModel).where(
                PaymentModel.tx_hash == payment_id,
                PaymentModel.tg_id == tg_id,
                PaymentModel.status == 'pending'
            )
        )
        payment = result.scalar_one_or_none()
        if not payment:
            LOG.warning(f"Payment {payment_id} not found or already processed for user {tg_id}")
            return False

        payment.status = 'confirmed'
        payment.confirmed_at = datetime.utcnow()
        await self.session.commit()
        LOG.info(f"Payment {payment_id} marked as processed for user {tg_id}, amount {amount}")
        return True

    async def mark_payment_processed_with_lock(self, payment_id: str, tg_id: int, amount: Decimal) -> bool:
        """Mark Telegram Stars payment as processed with database lock to prevent race conditions"""
        result = await self.session.execute(
            select(PaymentModel).where(
                PaymentModel.tx_hash == payment_id,
                PaymentModel.tg_id == tg_id,
                PaymentModel.status == 'pending'
            ).with_for_update()
        )
        payment = result.scalar_one_or_none()
        if not payment:
            LOG.warning(f"Payment {payment_id} not found or already processed for user {tg_id}")
            return False

        payment.status = 'confirmed'
        payment.confirmed_at = datetime.utcnow()
        await self.session.commit()
        LOG.info(f"Payment {payment_id} marked as processed for user {tg_id}, amount {amount}")
        return True

    async def get_pending_ton_transaction(self, comment: str, amount: Decimal) -> Optional[TonTransaction]:
        """Get pending TON transaction by comment and amount"""
        result = await self.session.execute(
            select(TonTransaction).where(
                TonTransaction.comment == comment,
                TonTransaction.amount >= amount * Decimal("0.95"),
                TonTransaction.processed_at == None
            ).order_by(TonTransaction.created_at.desc())
        )
        return result.scalar_one_or_none()

    async def is_tx_hash_already_used(self, tx_hash: str) -> bool:
        """Check if a transaction hash has already been used for a confirmed payment"""
        result = await self.session.execute(
            select(PaymentModel).where(
                PaymentModel.tx_hash == tx_hash,
                PaymentModel.status == 'confirmed'
            )
        )
        return result.scalar_one_or_none() is not None

    async def update_payment_metadata(self, payment_id: int, metadata: dict):
        """Update payment extra_data (e.g., CryptoBot invoice_id)"""
        stmt = update(PaymentModel).where(PaymentModel.id == payment_id).values(extra_data=metadata)
        await self.session.execute(stmt)
        await self.session.commit()

    async def cancel_payment(self, payment_id: int) -> bool:
        """
        Cancel a pending payment

        IMPORTANT: For YooKassa/CryptoBot, checks if payment is already succeeded
        before cancellation to prevent loss of user funds
        """
        # Get payment details first
        result = await self.session.execute(
            select(PaymentModel).where(PaymentModel.id == payment_id)
        )
        payment = result.scalar_one_or_none()

        if not payment or payment.status != 'pending':
            return False

        # For YooKassa/CryptoBot, check if payment is already succeeded on gateway side
        if payment.method in ['yookassa', 'cryptobot']:
            extra_data = payment.extra_data or {}

            if payment.method == 'yookassa':
                yookassa_payment_id = extra_data.get('yookassa_payment_id')
                if yookassa_payment_id:
                    # Check if payment is succeeded in YooKassa
                    try:
                        from yookassa import Payment as YooKassaPayment
                        # run blocking network call in thread to avoid blocking event loop
                        yookassa_payment = await asyncio.to_thread(YooKassaPayment.find_one, yookassa_payment_id)
                        if yookassa_payment and getattr(yookassa_payment, "status", None) == 'succeeded':
                            LOG.warning(f"Cannot cancel payment {payment_id}: already succeeded in YooKassa")
                            return False
                    except Exception as e:
                        LOG.error(f"Error checking YooKassa payment status: {e}")
                        # Don't cancel if we can't verify
                        return False

        # Safe to cancel
        stmt = update(PaymentModel).where(
            PaymentModel.id == payment_id,
            PaymentModel.status == 'pending'
        ).values(status='cancelled', confirmed_at=datetime.utcnow())
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def get_active_pending_payments(self, tg_id: int) -> List[Dict]:
        """Get active (non-expired) pending payments for a user"""
        now = datetime.utcnow()
        query = select(PaymentModel).where(
            PaymentModel.tg_id == tg_id,
            PaymentModel.status == 'pending',
            PaymentModel.expires_at > now
        ).order_by(PaymentModel.created_at.desc())
        result = await self.session.execute(query)
        payments = result.scalars().all()
        return [p.__dict__ for p in payments]

    async def get_pending_or_recent_expired_payments(
        self,
        method: Optional[Union[str, PaymentMethod]] = None,
        expired_hours: int = 1
    ) -> List[Dict]:
        """
        Get pending payments AND recently expired payments (to catch late confirmations).

        This is critical for payment gateways like YooKassa where:
        - Local timeout is 10 minutes
        - Gateway timeout is 60 minutes
        - User might pay after local expiry but before gateway expiry

        Args:
            method: Payment method to filter by
            expired_hours: How many hours back to check expired payments
        """
        now = datetime.utcnow()
        expired_threshold = now - timedelta(hours=expired_hours)

        # Get pending payments
        query_pending = select(PaymentModel).where(PaymentModel.status == 'pending')

        # Get recently expired payments (created within last N hours)
        query_expired = select(PaymentModel).where(
            PaymentModel.status == 'expired',
            PaymentModel.created_at > expired_threshold
        )

        if method:
            m = method.value if isinstance(method, PaymentMethod) else method
            query_pending = query_pending.where(PaymentModel.method == m)
            query_expired = query_expired.where(PaymentModel.method == m)

        # Execute both queries
        result_pending = await self.session.execute(query_pending.order_by(PaymentModel.created_at))
        result_expired = await self.session.execute(query_expired.order_by(PaymentModel.created_at))

        pending_payments = result_pending.scalars().all()
        expired_payments = result_expired.scalars().all()

        all_payments = list(pending_payments) + list(expired_payments)
        return [p.__dict__ for p in all_payments]

    async def expire_old_payments(self) -> int:
        """Mark expired pending payments as expired"""
        now = datetime.utcnow()
        stmt = update(PaymentModel).where(
            PaymentModel.status == 'pending',
            PaymentModel.expires_at < now
        ).values(status='expired')
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

    async def cleanup_old_payments(self, days: int = 7) -> int:
        """Delete old expired/cancelled payments (older than specified days)"""
        threshold = datetime.utcnow() - timedelta(days=days)
        from sqlalchemy import delete
        stmt = delete(PaymentModel).where(
            PaymentModel.status.in_(['expired', 'cancelled']),
            PaymentModel.created_at < threshold
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

# ===== END FILE: app/repo/payments.py =====



# ===== START FILE: app/repo/init_db.py =====

from app.repo.db import engine, Base
from app.utils.logging import get_logger

LOG = get_logger(__name__)


async def init_database():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        LOG.info("Database tables initialized successfully")
    except Exception as e:
        LOG.error(f"Error initializing database: {e}")
        raise


# ===== END FILE: app/repo/init_db.py =====



# ===== START FILE: app/repo/models.py =====

from sqlalchemy import (
    Column, Integer, BigInteger, String, Boolean, DateTime, Numeric, Float, Text, CHAR, ARRAY, JSON
)
from .db import Base
from datetime import datetime

class Config(Base):
    __tablename__ = "configs"
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, index=True)
    name = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    vless_link = Column(String)
    server_id = Column(String)
    username = Column(String)
    deleted = Column(Boolean, default=False)

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger)
    method = Column(String)
    amount = Column(Numeric)
    currency = Column(String)
    status = Column(String)
    comment = Column(Text)
    tx_hash = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # Payment expiration time
    expected_crypto_amount = Column(Numeric, nullable=True)
    extra_data = Column(JSON, nullable=True)  # For storing extra data like CryptoBot invoice_id

class Referral(Base):
    __tablename__ = "referrals"
    id = Column(BigInteger, primary_key=True)
    inviter_id = Column(BigInteger)
    invited_id = Column(BigInteger)
    invite_code = Column(Text)
    created_at = Column(DateTime)
    reward_given = Column(Boolean)
    reward_amount = Column(Float)
    note = Column(Text)

class MarzbanInstance(Base):
    __tablename__ = "marzban_instances"
    id = Column(String, primary_key=True)  # e.g., "s001", "s002"
    name = Column(String)  # Friendly name
    base_url = Column(Text, nullable=False)  # Marzban panel URL
    username = Column(Text, nullable=False)  # Marzban login
    password = Column(Text, nullable=False)  # Marzban password
    is_active = Column(Boolean, default=True)  # Enable/disable instance
    priority = Column(Integer, default=100)  # Lower = higher priority
    excluded_node_names = Column(ARRAY(String), default=[])  # Node names to exclude from load balancing
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Server(Base):
    """
    DEPRECATED: Use MarzbanInstance instead.
    Kept for backward compatibility with existing data.
    """
    __tablename__ = "servers"
    id = Column(String, primary_key=True)
    country = Column(String)
    ip = Column(String)
    ram = Column(Integer)
    volume = Column(Integer)
    users_count = Column(Integer)
    base_url = Column(Text)
    load_avg = Column(Float)
    login = Column(Text)
    password = Column(Text)
    updated_at = Column(DateTime)

class TonTransaction(Base):
    __tablename__ = "ton_transactions"
    tx_hash = Column(Text, primary_key=True)
    amount = Column(Numeric)
    comment = Column(Text)
    sender = Column(String)
    created_at = Column(DateTime)
    processed_at = Column(DateTime, nullable=True)

class User(Base):
    __tablename__ = "users"
    tg_id = Column(BigInteger, primary_key=True)
    balance = Column(Numeric, default=0)
    subscription_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    username = Column(Text)
    lang = Column(String, default="ru")
    configs = Column(Integer, default=0)
    referrer_id = Column(BigInteger)
    first_buy = Column(Boolean, default=True)
    notifications = Column(Boolean, default=True)

# ===== END FILE: app/repo/models.py =====



# ===== START FILE: app/payments/__init__.py =====



# ===== END FILE: app/payments/__init__.py =====



# ===== START FILE: app/payments/manager.py =====

import logging
import uuid
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
import asyncio
from app.payments.models import PaymentResult, PaymentMethod
from app.payments.gateway.base import BasePaymentGateway
from app.payments.gateway.ton import TonGateway
from app.payments.gateway.stars import TelegramStarsGateway
from app.payments.gateway.cryptobot import CryptoBotGateway
from app.payments.gateway.yookassa import YooKassaGateway
from app.repo.payments import PaymentRepository
from app.repo.user import UserRepository
from app.repo.db import get_session
from app.utils.redis import get_redis
from config import bot

LOG = logging.getLogger(__name__)

class PaymentManager:
    def __init__(self, session, redis_client=None):
        self.session = session
        self.redis_client = redis_client
        self.payment_repo = PaymentRepository(session, redis_client)
        self.gateways: dict[PaymentMethod, BasePaymentGateway] = {
            PaymentMethod.TON: TonGateway(session, redis_client, bot=bot),
            PaymentMethod.STARS: TelegramStarsGateway(bot, session, redis_client),
            PaymentMethod.CRYPTOBOT: CryptoBotGateway(session, redis_client, bot=bot),
            PaymentMethod.YOOKASSA: YooKassaGateway(session, redis_client, bot=bot),
        }
        self.user_repo = UserRepository(session, redis_client)
        self.polling_task: Optional[asyncio.Task] = None

    async def create_payment(
        self,
        t,
        tg_id: int,
        method: PaymentMethod,
        amount: Decimal,
        chat_id: Optional[int] = None,
    ) -> PaymentResult:
        try:
            from app.repo.models import User
            from sqlalchemy import select

            # CRITICAL FIX: Lock user row BEFORE checking for active payments
            result = await self.session.execute(
                select(User)
                .where(User.tg_id == tg_id)
                .with_for_update()  # Serialize payment creation per user
            )
            user = result.scalar_one_or_none()
            if not user:
                raise ValueError(f"User {tg_id} not found")

            # Automatically cancel any existing pending payments for the user.
            active_payments = await self.payment_repo.get_active_pending_payments(tg_id)
            if active_payments:
                LOG.info(f"User {tg_id} has active payments: {[p['id'] for p in active_payments]}. Cancelling them.")
                for payment in active_payments:
                    await self.cancel_payment(payment['id'])

            currency = "RUB"
            comment = None
            expected_crypto_amount = None

            if method == PaymentMethod.TON:
                comment = uuid.uuid4().hex[:10]
                from app.utils.rates import get_ton_price
                ton_price = await get_ton_price()
                expected_crypto_amount = (Decimal(amount) / ton_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            payment_id = await self.payment_repo.create_payment(
                tg_id=tg_id,
                method=method.value,
                amount=amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                currency=currency,
                comment=comment,
                expected_crypto_amount=expected_crypto_amount
            )

            gateway = self.gateways[method]
            result = await gateway.create_payment(
                t,
                tg_id=tg_id,
                amount=amount,
                chat_id=chat_id,
                payment_id=payment_id,
                comment=comment
            )

            LOG.info(f"Payment created: {method} for user {tg_id}, amount {amount}, id={payment_id}")
            if method in [PaymentMethod.TON, PaymentMethod.CRYPTOBOT, PaymentMethod.YOOKASSA]:
                await self.start_polling_if_needed()
            return result
        except Exception as e:
            LOG.error(f"Create payment error for user {tg_id}: {type(e).__name__}: {e}")
            raise

    async def cancel_payment(self, payment_id: int):
        """
        Cancels a payment both remotely (via gateway) and locally.
        """
        payment = await self.payment_repo.get_payment(payment_id)
        if not payment or payment['status'] != 'pending':
            LOG.warning(f"Attempted to cancel payment {payment_id} which is not pending.")
            return

        LOG.info(f"Cancelling payment {payment_id} for user {payment['tg_id']}.")
        
        try:
            method = PaymentMethod(payment['method'])
            gateway = self.gateways.get(method)
            
            # Check if gateway supports remote cancellation
            if gateway and hasattr(gateway, 'cancel_payment'):
                await gateway.cancel_payment(payment_id)
            
        except Exception as e:
            LOG.error(f"Remote cancellation for payment {payment_id} failed: {e}", exc_info=True)
            # Continue to cancel locally regardless of remote failure

        await self.payment_repo.update_payment_status(payment_id, 'cancelled')
        LOG.info(f"Locally cancelled payment {payment_id}.")

    async def confirm_payment(self, payment_id: int, tg_id: int, amount: Decimal, tx_hash: Optional[str] = None):
        try:
            # Credit payment amount
            await self.user_repo.change_balance(tg_id, amount)

            if tx_hash:
                await self.payment_repo.update_payment_status(payment_id, "confirmed", tx_hash)

            LOG.info(f"Payment {payment_id} confirmed: +{amount} for user {tg_id}, tx={tx_hash}")

            return None
        except Exception as e:
            LOG.error(f"Confirm payment error for user {tg_id}: {type(e).__name__}: {e}")
            raise

    async def start_polling_if_needed(self):
        if self.polling_task is None or self.polling_task.done():
            self.polling_task = asyncio.create_task(self.run_polling_loop())

    async def run_polling_loop(self):
        while True:
            try:
                # Create new session for each polling iteration
                async with get_session() as session:
                    redis_client = await get_redis()
                    temp_payment_repo = PaymentRepository(session, redis_client)

                    # Check TON payments
                    ton_pendings = await temp_payment_repo.get_pending_payments(PaymentMethod.TON.value)
                    if ton_pendings:
                        from app.utils.updater import TonTransactionsUpdater
                        updater = TonTransactionsUpdater()
                        await updater.run_once()

                    # Check CryptoBot payments
                    cryptobot_pendings = await temp_payment_repo.get_pending_payments(PaymentMethod.CRYPTOBOT.value)
                    if cryptobot_pendings:
                        for payment in cryptobot_pendings:
                            # Create new session for each check
                            async with get_session() as check_session:
                                check_redis = await get_redis()
                                check_gateway = self.gateways[PaymentMethod.CRYPTOBOT].__class__(check_session, check_redis, bot=bot)
                                await check_gateway.check_payment(payment['id'])

                    # Check YooKassa payments (including recently expired ones)
                    # CRITICAL: Check expired payments too, in case user paid after local timeout
                    # but before YooKassa timeout (local=10min, YooKassa=60min)
                    yookassa_pendings = await temp_payment_repo.get_pending_or_recent_expired_payments(
                        PaymentMethod.YOOKASSA.value,
                        expired_hours=1
                    )
                    if yookassa_pendings:
                        for payment in yookassa_pendings:
                            # Create new session for each check
                            async with get_session() as check_session:
                                check_redis = await get_redis()
                                check_gateway = self.gateways[PaymentMethod.YOOKASSA].__class__(check_session, check_redis, bot=bot)
                                await check_gateway.check_payment(payment['id'])

                    # If no pending payments, stop polling
                    if not ton_pendings and not cryptobot_pendings and not yookassa_pendings:
                        break
            except Exception as e:
                LOG.error(f"Polling loop error: {type(e).__name__}: {e}")
            await asyncio.sleep(60)

    async def check_payment(self, payment_id: int) -> bool:
        try:
            payment = await self.payment_repo.get_payment(payment_id)
            if not payment or payment['status'] != 'pending':
                return False

            gateway = self.gateways[PaymentMethod(payment['method'])]
            confirmed = await gateway.check_payment(payment_id)

            # NOTE: TON and CryptoBot gateways handle balance updates internally
            # to maintain atomicity with transaction locks. Only call confirm_payment
            # for gateways that don't do this (currently: Stars via webhook)
            # For TON/CryptoBot, check_payment() already updated balance + payment status

            # Don't double-credit: TON and CryptoBot already updated balance in check_payment()
            # if confirmed and payment['method'] not in ['ton', 'cryptobot']:
            #     await self.confirm_payment(payment_id, payment['tg_id'], payment['amount'])

            return confirmed
        except Exception as e:
            LOG.error(f"Check payment error for payment {payment_id}: {type(e).__name__}: {e}")
            return False

    async def get_pending_payments(self, method: Optional[PaymentMethod | str] = None):
        return await self.payment_repo.get_pending_payments(method if method else None)

    async def close(self):
        for gateway in self.gateways.values():
            if hasattr(gateway, 'close'):
                await gateway.close()
        if self.polling_task:
            self.polling_task.cancel()

# ===== END FILE: app/payments/manager.py =====



# ===== START FILE: app/payments/models.py =====

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from datetime import datetime
from enum import Enum

class PaymentMethod(str, Enum):
    TON = "ton"
    STARS = "stars"
    CRYPTOBOT = "cryptobot"
    YOOKASSA = "yookassa"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    EXPIRED = "expired"

@dataclass
class PaymentResult:
    payment_id: int
    method: PaymentMethod
    amount: Decimal
    text: str
    url: Optional[str] = None
    wallet: Optional[str] = None
    comment: Optional[str] = None
    expected_crypto_amount: Optional[Decimal] = None
    pay_url: Optional[str] = None  # For CryptoBot invoice URL
    invoice_id: Optional[str] = None  # For CryptoBot invoice tracking

@dataclass
class Payment:
    id: int
    tg_id: int
    method: PaymentMethod
    amount: Decimal
    currency: str
    status: PaymentStatus
    comment: Optional[str]
    tx_hash: Optional[str]
    created_at: datetime
    confirmed_at: Optional[datetime]
    expected_crypto_amount: Optional[Decimal] = None

# ===== END FILE: app/payments/models.py =====



# ===== START FILE: app/payments/gateway/ton.py =====

import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from aiogram import Bot
from app.payments.gateway.base import BasePaymentGateway
from app.payments.models import PaymentResult, PaymentMethod
from app.repo.payments import PaymentRepository
from config import TON_ADDRESS

LOG = logging.getLogger(__name__)

class TonGateway(BasePaymentGateway):
    requires_polling = True

    def __init__(self, session, redis_client=None, bot: Optional[Bot] = None):
        self.session = session
        self.payment_repo = PaymentRepository(session, redis_client)
        self.bot = bot

    async def create_payment(
        self,
        t,
        tg_id: int,
        amount: Decimal,
        chat_id: Optional[int] = None,
        payment_id: Optional[int] = None,
        comment: Optional[str] = None
    ) -> PaymentResult:
        if payment_id is None or comment is None:
            raise ValueError("payment_id and comment required for TON")

        from app.utils.rates import get_ton_price
        try:
            ton_price = await get_ton_price()
            expected_ton = (Decimal(amount) / ton_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except Exception as e:
            LOG.error(f"Error fetching TON price: {e}")
            raise ValueError("Failed to fetch TON price")

        wallet = TON_ADDRESS
        text = (
            t("ton_payment_intro") + "\n\n"
            + t("ton_send_amount", expected_ton=expected_ton, amount=amount) + "\n"
            + t("ton_wallet", wallet=wallet) + "\n\n"
            + t("ton_comment", comment=comment) + "\n\n"
            + t("ton_comment_warning")
        )

        return PaymentResult(
            payment_id=payment_id,
            method=PaymentMethod.TON,
            amount=amount,
            text=text,
            wallet=wallet,
            comment=comment,
            expected_crypto_amount=expected_ton
        )

    async def check_payment(self, payment_id: int) -> bool:
        """
        Check if TON payment has been confirmed on blockchain.
        Uses database locks to prevent replay attacks and race conditions.
        """
        payment = await self.payment_repo.get_payment(payment_id)
        if not payment:
            LOG.warning(f"Payment {payment_id} not found")
            return False

        if not payment.get('comment') or not payment.get('expected_crypto_amount'):
            LOG.debug(f"TON payment {payment_id} incomplete: {payment}")
            return False

        current_status = payment.get('status')
        if current_status == 'confirmed':
            LOG.debug(f"TON payment {payment_id} already confirmed")
            return False

        if current_status not in ['pending', 'expired']:
            LOG.debug(f"TON payment {payment_id} has status {current_status}, cannot process")
            return False

        tx = await self.payment_repo.get_pending_ton_transaction(
            comment=payment.get('comment'),
            amount=payment.get('expected_crypto_amount')
        )

        if not tx:
            return False

        from datetime import datetime
        tx.processed_at = datetime.utcnow()

        confirmed = await self._confirm_payment_atomic(
            payment_id=payment_id,
            tx_hash=tx.tx_hash,
            amount=payment['amount'],
            allow_expired=True
        )

        if confirmed:
            from app.repo.models import User
            from sqlalchemy import select

            async with self.session.begin():
                result = await self.session.execute(
                    select(User).where(User.tg_id == payment['tg_id'])
                )
                user = result.scalar_one_or_none()

                if user:
                    has_active_sub = user.subscription_end and user.subscription_end > datetime.utcnow()

                    await self.on_payment_confirmed(
                        payment_id=payment_id,
                        tx_hash=tx.tx_hash,
                        tg_id=user.tg_id,
                        total_amount=payment['amount'],
                        lang=user.lang,
                        has_active_subscription=has_active_sub
                    )

        return confirmed

    async def on_payment_confirmed(
        self,
        payment_id: int,
        tx_hash: Optional[str] = None,
        tg_id: Optional[int] = None,
        total_amount: Optional[Decimal] = None,
        lang: str = "ru",
        has_active_subscription: bool = False
    ):
        """
        Callback when payment is confirmed.

        Sends Telegram notification to user about successful payment.
        """
        LOG.info(f"TON payment confirmed callback: id={payment_id}, tx={tx_hash}")

        # Send notification if bot is available and we have user info
        if self.bot and tg_id and total_amount:
            from app.utils.payment_notifications import send_payment_notification

            try:
                await send_payment_notification(
                    bot=self.bot,
                    tg_id=tg_id,
                    amount=total_amount,
                    lang=lang,
                    has_active_subscription=has_active_subscription
                )
            except Exception as e:
                LOG.error(f"Error sending payment notification to {tg_id}: {e}")
                # Don't fail payment confirmation if notification fails

# ===== END FILE: app/payments/gateway/ton.py =====



# ===== START FILE: app/payments/gateway/stars.py =====

import logging
from decimal import Decimal
from typing import Optional
from aiogram.types import LabeledPrice
from app.payments.gateway.base import BasePaymentGateway
from app.payments.models import PaymentResult, PaymentMethod
from app.repo.payments import PaymentRepository
from config import TELEGRAM_STARS_RATE

LOG = logging.getLogger(__name__)

class TelegramStarsGateway(BasePaymentGateway):
    requires_polling = False

    def __init__(self, bot, session, redis_client=None):
        self.bot = bot
        self.session = session
        self.payment_repo = PaymentRepository(session, redis_client)

    async def create_payment(
        self,
        t,
        tg_id: int,
        amount: Decimal,
        chat_id: Optional[int] = None,
        payment_id: Optional[int] = None,
        comment: Optional[str] = None
    ) -> PaymentResult:
        if not chat_id:
            raise ValueError("chat_id required for Stars payment")

        stars_amount = int(amount / Decimal(str(TELEGRAM_STARS_RATE)))
        payload = f"topup_{tg_id}_{int(amount)}"

        try:
            await self.bot.send_invoice(
                chat_id=chat_id,
                title=t("stars_add_title"),
                description=t("stars_add_description", amount=amount),
                payload=payload,
                currency="XTR",
                prices=[LabeledPrice(label=t("stars_price_label"), amount=stars_amount)]
            )
        except Exception as e:
            LOG.error(f"Error sending invoice for user {tg_id}: {e}")
            raise

        return PaymentResult(
            payment_id=payment_id or 0,
            method=PaymentMethod.STARS,
            amount=amount,
            text=t("stars_invoice_sent")
        )

    async def check_payment(self, payment_id: int) -> bool:
        return False

# ===== END FILE: app/payments/gateway/stars.py =====



# ===== START FILE: app/payments/gateway/__init__.py =====



# ===== END FILE: app/payments/gateway/__init__.py =====



# ===== START FILE: app/payments/gateway/base.py =====

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional
from datetime import datetime
from app.payments.models import PaymentResult
from app.utils.logging import get_logger

LOG = get_logger(__name__)

class BasePaymentGateway(ABC):

    @abstractmethod
    async def create_payment(self, tg_id: int, amount: Decimal, chat_id: Optional[int] = None) -> PaymentResult:
        pass

    @abstractmethod
    async def check_payment(self, payment_id: int) -> bool:
        pass

    @property
    @abstractmethod
    def requires_polling(self) -> bool:
        pass

    async def on_payment_confirmed(self, payment_id: int, tx_hash: Optional[str] = None):
        pass

    async def _confirm_payment_atomic(
        self,
        payment_id: int,
        tx_hash: str,
        amount: Decimal,
        allow_expired: bool = False
    ) -> bool:
        """
        Atomically confirm payment with database locks to prevent race conditions.

        Args:
            payment_id: Payment ID to confirm
            tx_hash: Transaction hash (for deduplication)
            amount: Amount to credit
            allow_expired: Whether to allow confirming expired payments (for blockchain recovery)

        Returns:
            True if confirmed successfully, False otherwise
        """
        from app.repo.models import Payment as PaymentModel, User
        from sqlalchemy import select

        try:
            result = await self.session.execute(
                select(PaymentModel)
                .where(PaymentModel.id == payment_id)
                .with_for_update()
            )
            payment = result.scalar_one_or_none()

            if not payment:
                LOG.warning(f"Payment {payment_id} not found during confirmation")
                return False

            valid_statuses = ['pending', 'expired'] if allow_expired else ['pending']
            if payment.status not in valid_statuses:
                LOG.debug(f"Payment {payment_id} has status {payment.status}, cannot confirm")
                return False

            if payment.status == 'expired' and allow_expired:
                LOG.warning(f"Recovering expired payment {payment_id} - late confirmation")

            result = await self.session.execute(
                select(User)
                .where(User.tg_id == payment.tg_id)
                .with_for_update()
            )
            user = result.scalar_one_or_none()

            if not user:
                LOG.error(f"User {payment.tg_id} not found for payment {payment_id}")
                return False

            if payment.tx_hash is not None:
                LOG.warning(f"Payment {payment_id} already has tx_hash: {payment.tx_hash}")
                return False

            result = await self.session.execute(
                select(PaymentModel).where(PaymentModel.tx_hash == tx_hash)
            )
            existing_payment = result.scalar_one_or_none()
            if existing_payment:
                LOG.warning(f"Transaction {tx_hash} already used for payment {existing_payment.id}")
                return False

            old_balance = user.balance

            payment.status = 'confirmed'
            payment.tx_hash = tx_hash
            payment.confirmed_at = datetime.utcnow()
            user.balance += amount

            await self.session.commit()

            LOG.info(f"Payment confirmed: id={payment_id}, user={user.tg_id}, "
                    f"amount={amount}, balance: {old_balance} → {user.balance}, tx_hash={tx_hash}")

            try:
                redis = await self.get_redis()
                await redis.delete(f"user:{user.tg_id}:balance")
            except Exception as e:
                LOG.warning(f"Redis error invalidating cache for user {user.tg_id}: {e}")

            return True

        except Exception as e:
            await self.session.rollback()
            LOG.error(f"Error confirming payment {payment_id}: {type(e).__name__}: {e}")
            return False

    async def get_redis(self):
        """Get Redis client (must be implemented by subclass if needed)"""
        if hasattr(self, 'redis_client') and self.redis_client:
            return self.redis_client
        from app.utils.redis import get_redis
        return await get_redis()

# ===== END FILE: app/payments/gateway/base.py =====



# ===== START FILE: app/payments/gateway/cryptobot.py =====

import logging
from decimal import Decimal
from typing import Optional
from aiogram import Bot
from aiocryptopay import AioCryptoPay, Networks
from app.payments.gateway.base import BasePaymentGateway
from app.payments.models import PaymentResult, PaymentMethod
from app.repo.payments import PaymentRepository
from app.utils.rates import get_usdt_rub_rate
from config import CRYPTOBOT_TOKEN, CRYPTOBOT_TESTNET

LOG = logging.getLogger(__name__)


class CryptoBotGateway(BasePaymentGateway):
    requires_polling = True

    def __init__(self, session, redis_client=None, bot: Optional[Bot] = None):
        self.session = session
        self.payment_repo = PaymentRepository(session, redis_client)
        self._cryptopay: Optional[AioCryptoPay] = None
        self.bot = bot

    async def _get_cryptopay(self) -> AioCryptoPay:
        if self._cryptopay is None:
            if not CRYPTOBOT_TOKEN:
                raise ValueError("CRYPTOBOT_TOKEN is not configured in .env")

            network = Networks.TEST_NET if CRYPTOBOT_TESTNET else Networks.MAIN_NET
            self._cryptopay = AioCryptoPay(token=CRYPTOBOT_TOKEN, network=network)

        return self._cryptopay

    async def create_payment(
        self,
        t,
        tg_id: int,
        amount: Decimal,
        chat_id: Optional[int] = None,
        payment_id: Optional[int] = None,
        comment: Optional[str] = None
    ) -> PaymentResult:
        """Create CryptoBot invoice"""
        if payment_id is None:
            raise ValueError("payment_id is required for CryptoBot")

        try:
            cryptopay = await self._get_cryptopay()

            # Get current USDT/RUB exchange rate
            usdt_rate = await get_usdt_rub_rate()

            # Convert RUB to USDT
            usdt_amount = amount / usdt_rate

            LOG.info(f"Converting {amount} RUB to {usdt_amount:.2f} USDT (rate: {usdt_rate})")

            # Get bot username for callback URL
            profile = await cryptopay.get_me()
            bot_username = profile.payment_processing_bot_username

            invoice = await cryptopay.create_invoice(
                asset='USDT',
                amount=float(usdt_amount),  # Amount in USDT after conversion from RUB
                description=comment or f"Payment #{payment_id}",
                paid_btn_name="callback",  # Button to return to bot after payment
                paid_btn_url=f"https://t.me/{bot_username}",
                payload=str(payment_id),  # Used to identify payment in webhook
                allow_comments=False,
                allow_anonymous=False,
            )

            # Store invoice_id in payment metadata
            await self.payment_repo.update_payment_metadata(
                payment_id=payment_id,
                metadata={'invoice_id': invoice.invoice_id}
            )

            pay_url = invoice.bot_invoice_url

            text = (
                t("cryptobot_payment_intro") + "\n\n"
                + t("cryptobot_amount", amount=amount) + "\n"
                + f"≈ {usdt_amount:.2f} USDT\n\n"
                + t("cryptobot_click_button")
            )

            return PaymentResult(
                payment_id=payment_id,
                method=PaymentMethod.CRYPTOBOT,
                amount=amount,
                text=text,
                pay_url=pay_url,
                invoice_id=invoice.invoice_id
            )

        except Exception as e:
            LOG.error(f"Error creating CryptoBot invoice: {e}")
            raise ValueError(f"Failed to create CryptoBot invoice: {e}")

    async def check_payment(self, payment_id: int) -> bool:
        """
        Check if CryptoBot invoice has been paid.

        CRITICAL FIX: Uses database locks to prevent concurrent confirmations
        of the same payment from polling loop.
        """
        try:
            from app.repo.models import Payment as PaymentModel, User
            from sqlalchemy import select

            payment = await self.payment_repo.get_payment(payment_id)
            if not payment:
                LOG.warning(f"Payment {payment_id} not found")
                return False

            # CRITICAL FIX: Allow confirming expired payments if paid on CryptoBot side
            # This prevents loss of user funds when payment expires locally but succeeds on gateway
            current_status = payment.get('status')
            if current_status == 'confirmed':
                LOG.debug(f"CryptoBot payment {payment_id} already confirmed")
                return False

            # Allow processing for 'pending' and 'expired' statuses
            if current_status not in ['pending', 'expired']:
                LOG.debug(f"CryptoBot payment {payment_id} has status {current_status}, cannot process")
                return False

            extra_data = payment.get('extra_data', {})
            invoice_id = extra_data.get('invoice_id') if extra_data else None

            if not invoice_id:
                LOG.debug(f"CryptoBot payment {payment_id} has no invoice_id")
                return False

            cryptopay = await self._get_cryptopay()

            # Get invoice status from CryptoBot
            invoices = await cryptopay.get_invoices(invoice_ids=[invoice_id])

            if not invoices:
                LOG.warning(f"CryptoBot invoice {invoice_id} not found")
                return False

            invoice = invoices[0]

            # Check if invoice is paid
            if invoice.status == 'paid':
                # CRITICAL FIX: Lock payment AND user rows for atomic update
                result = await self.session.execute(
                    select(PaymentModel)
                    .where(PaymentModel.id == payment_id)
                    .with_for_update()
                )
                payment_locked = result.scalar_one_or_none()

                if not payment_locked:
                    LOG.debug(f"Payment {payment_id} not found during lock")
                    return False

                # Allow confirming if status is pending OR expired (but paid on gateway side)
                if payment_locked.status not in ['pending', 'expired']:
                    LOG.debug(f"Payment {payment_id} has status {payment_locked.status}, cannot confirm")
                    return False

                # Log if recovering expired payment
                if payment_locked.status == 'expired':
                    LOG.warning(f"Recovering expired payment {payment_id} - user paid after local timeout but succeeded on CryptoBot")

                # Lock user row for atomic balance update
                result = await self.session.execute(
                    select(User)
                    .where(User.tg_id == payment_locked.tg_id)
                    .with_for_update()
                )
                user = result.scalar_one_or_none()
                if not user:
                    LOG.error(f"User {payment_locked.tg_id} not found for payment {payment_id}")
                    return False

                # Check if tx_hash already set
                if payment_locked.tx_hash is not None:
                    LOG.warning(f"Payment {payment_id} already has tx_hash: {payment_locked.tx_hash}")
                    return False

                # ATOMIC UPDATE: Update payment status and balance
                from datetime import datetime

                old_balance = user.balance
                tx_hash = f"cryptobot_{invoice_id}"

                payment_locked.status = 'confirmed'
                payment_locked.tx_hash = tx_hash
                payment_locked.confirmed_at = datetime.utcnow()

                # Credit payment amount
                user.balance += payment_locked.amount

                await self.session.commit()

                LOG.info(f"CryptoBot payment confirmed: payment_id={payment_id}, user={user.tg_id}, "
                        f"amount={payment_locked.amount}, balance: {old_balance} → {user.balance}, "
                        f"invoice={invoice_id}")

                # Check subscription status BEFORE cache invalidation
                from datetime import datetime
                has_active_sub = user.subscription_end and user.subscription_end > datetime.utcnow()

                # Invalidate cache (tolerate Redis failures)
                try:
                    redis = await self.payment_repo.get_redis()
                    await redis.delete(f"user:{user.tg_id}:balance")
                except Exception as e:
                    LOG.warning(f"Redis error invalidating cache for user {user.tg_id}: {e}")

                # Send notification to user about successful payment
                await self.on_payment_confirmed(
                    payment_id=payment_id,
                    tx_hash=tx_hash,
                    tg_id=user.tg_id,
                    total_amount=payment_locked.amount,
                    lang=user.lang,
                    has_active_subscription=has_active_sub
                )
                return True

            return False

        except Exception as e:
            LOG.error(f"Error checking CryptoBot payment {payment_id}: {e}")
            return False

    async def on_payment_confirmed(
        self,
        payment_id: int,
        tx_hash: Optional[str] = None,
        tg_id: Optional[int] = None,
        total_amount: Optional[Decimal] = None,
        lang: str = "ru",
        has_active_subscription: bool = False
    ):
        """
        Callback when payment is confirmed.

        Sends Telegram notification to user about successful payment.
        """
        LOG.info(f"CryptoBot payment confirmed callback: id={payment_id}, tx={tx_hash}")

        # Send notification if bot is available and we have user info
        if self.bot and tg_id and total_amount:
            from app.utils.payment_notifications import send_payment_notification

            try:
                await send_payment_notification(
                    bot=self.bot,
                    tg_id=tg_id,
                    amount=total_amount,
                    lang=lang,
                    has_active_subscription=has_active_subscription
                )
            except Exception as e:
                LOG.error(f"Error sending payment notification to {tg_id}: {e}")
                # Don't fail payment confirmation if notification fails

    async def close(self):
        """Close CryptoPay client session"""
        if self._cryptopay:
            await self._cryptopay.close()


# ===== END FILE: app/payments/gateway/cryptobot.py =====



# ===== START FILE: app/payments/gateway/yookassa.py =====

import logging
import asyncio
import uuid
from decimal import Decimal
from typing import Optional
from aiogram import Bot
from yookassa import Configuration, Payment as YooKassaPayment
from app.payments.gateway.base import BasePaymentGateway
from app.payments.models import PaymentResult, PaymentMethod
from app.repo.payments import PaymentRepository
from config import (
    YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY,
    YOOKASSA_TEST_SHOP_ID, YOOKASSA_TEST_SECRET_KEY,
    YOOKASSA_TESTNET
)

LOG = logging.getLogger(__name__)


class YooKassaGateway(BasePaymentGateway):
    requires_polling = True

    def __init__(self, session, redis_client=None, bot: Optional[Bot] = None):
        self.session = session
        self.payment_repo = PaymentRepository(session, redis_client)
        self._configured = False
        self.bot = bot

    async def _ensure_configured(self):
        """Configure YooKassa SDK with credentials based on test/production mode"""
        if not self._configured:
            # Select credentials based on testnet mode
            if YOOKASSA_TESTNET:
                shop_id = YOOKASSA_TEST_SHOP_ID
                secret_key = YOOKASSA_TEST_SECRET_KEY
                mode = "TESTNET"

                if not shop_id or not secret_key:
                    raise ValueError(
                        "YOOKASSA_TEST_SHOP_ID and YOOKASSA_TEST_SECRET_KEY must be configured in .env "
                        "when YOOKASSA_TESTNET=true"
                    )
            else:
                shop_id = YOOKASSA_SHOP_ID
                secret_key = YOOKASSA_SECRET_KEY
                mode = "PRODUCTION"

                if not shop_id or not secret_key:
                    raise ValueError(
                        "YOOKASSA_SHOP_ID and YOOKASSA_SECRET_KEY must be configured in .env "
                        "when YOOKASSA_TESTNET=false"
                    )

            await asyncio.to_thread(Configuration.configure, shop_id, secret_key)
            Configuration.timeout = 15  # Set timeout to 15 seconds
            self._configured = True
            LOG.info(f"YooKassa configured successfully in {mode} mode (shop_id: {shop_id})")

    async def create_payment(
        self,
        t,
        tg_id: int,
        amount: Decimal,
        chat_id: Optional[int] = None,
        payment_id: Optional[int] = None,
        comment: Optional[str] = None
    ) -> PaymentResult:
        """Create YooKassa payment and return payment URL"""
        if payment_id is None:
            raise ValueError("payment_id is required for YooKassa")

        try:
            await self._ensure_configured()

            # Get bot username for return URL
            from config import bot
            bot_info = await bot.get_me()
            bot_username = bot_info.username
            return_url = f"https://t.me/{bot_username}"

            # Create payment via YooKassa API
            payment_data = {
                "amount": {
                    "value": str(amount),
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": return_url
                },
                "capture": True,
                "description": comment or f"Payment #{payment_id}",
                "metadata": {
                    "payment_id": str(payment_id),
                    "tg_id": str(tg_id)
                },
                "receipt": {
                    "customer": {
                        "email": f"user{tg_id}@orbitvpn.com"  # Dummy email for receipt
                    },
                    "items": [
                        {
                            "description": "VPN subscription top-up",
                            "quantity": "1.00",
                            "amount": {
                                "value": str(amount),
                                "currency": "RUB"
                            },
                            "vat_code": 1,  # VAT 0% (no tax for digital services)
                            "payment_mode": "full_payment",
                            "payment_subject": "service"
                        }
                    ]
                }
            }

            yookassa_payment = await asyncio.to_thread(YooKassaPayment.create, payment_data)

            # Store YooKassa payment ID in metadata
            await self.payment_repo.update_payment_metadata(
                payment_id=payment_id,
                metadata={'yookassa_payment_id': yookassa_payment.id}
            )

            # Get confirmation URL
            confirmation_url = yookassa_payment.confirmation.confirmation_url

            text = (
                t("yookassa_payment_intro") + "\n\n"
                + t("yookassa_amount", amount=amount) + "\n\n"
                + t("yookassa_click_button")
            )

            mode = "TESTNET" if YOOKASSA_TESTNET else "PRODUCTION"
            LOG.info(f"YooKassa payment created: payment_id={payment_id}, "
                    f"yookassa_id={yookassa_payment.id}, amount={amount}, mode={mode}")

            return PaymentResult(
                payment_id=payment_id,
                method=PaymentMethod.YOOKASSA,
                amount=amount,
                text=text,
                pay_url=confirmation_url
            )

        except Exception as e:
            LOG.error(f"Error creating YooKassa payment: {e}")
            raise ValueError(f"Failed to create YooKassa payment: {e}")

    async def check_payment(self, payment_id: int) -> bool:
        """
        Check if YooKassa payment has been paid.

        Uses database locks to prevent concurrent confirmations
        of the same payment from polling loop.
        """
        try:
            from app.repo.models import Payment as PaymentModel, User
            from sqlalchemy import select

            payment = await self.payment_repo.get_payment(payment_id)
            if not payment:
                LOG.warning(f"Payment {payment_id} not found")
                return False

            # CRITICAL FIX: Allow confirming expired payments if succeeded on YooKassa side
            # This prevents loss of user funds when payment expires locally but succeeds on gateway
            current_status = payment.get('status')
            if current_status == 'confirmed':
                LOG.debug(f"YooKassa payment {payment_id} already confirmed")
                return False

            # Allow processing for 'pending' and 'expired' statuses
            if current_status not in ['pending', 'expired']:
                LOG.debug(f"YooKassa payment {payment_id} has status {current_status}, cannot process")
                return False

            extra_data = payment.get('extra_data', {})
            yookassa_payment_id = extra_data.get('yookassa_payment_id') if extra_data else None

            if not yookassa_payment_id:
                LOG.debug(f"YooKassa payment {payment_id} has no yookassa_payment_id")
                return False

            await self._ensure_configured()

            # Get payment status from YooKassa
            yookassa_payment = await asyncio.to_thread(YooKassaPayment.find_one, yookassa_payment_id)

            if not yookassa_payment:
                LOG.warning(f"YooKassa payment {yookassa_payment_id} not found")
                return False

            # Check if payment is succeeded
            if yookassa_payment.status == 'succeeded':
                # CRITICAL FIX: Lock payment AND user rows for atomic update
                result = await self.session.execute(
                    select(PaymentModel)
                    .where(PaymentModel.id == payment_id)
                    .with_for_update()
                )
                payment_locked = result.scalar_one_or_none()

                if not payment_locked:
                    LOG.debug(f"Payment {payment_id} not found during lock")
                    return False

                # Allow confirming if status is pending OR expired (but succeeded on gateway side)
                if payment_locked.status not in ['pending', 'expired']:
                    LOG.debug(f"Payment {payment_id} has status {payment_locked.status}, cannot confirm")
                    return False

                # Log if recovering expired payment
                if payment_locked.status == 'expired':
                    LOG.warning(f"Recovering expired payment {payment_id} - user paid after local timeout but succeeded on YooKassa")

                # Lock user row for atomic balance update
                result = await self.session.execute(
                    select(User)
                    .where(User.tg_id == payment_locked.tg_id)
                    .with_for_update()
                )
                user = result.scalar_one_or_none()
                if not user:
                    LOG.error(f"User {payment_locked.tg_id} not found for payment {payment_id}")
                    return False

                # Check if tx_hash already set
                if payment_locked.tx_hash is not None:
                    LOG.warning(f"Payment {payment_id} already has tx_hash: {payment_locked.tx_hash}")
                    return False

                # ATOMIC UPDATE: Update payment status and balance
                from datetime import datetime

                old_balance = user.balance
                tx_hash = f"yookassa_{yookassa_payment_id}"

                payment_locked.status = 'confirmed'
                payment_locked.tx_hash = tx_hash
                payment_locked.confirmed_at = datetime.utcnow()

                # Credit payment amount
                user.balance += payment_locked.amount

                await self.session.commit()

                LOG.info(f"YooKassa payment confirmed: payment_id={payment_id}, user={user.tg_id}, "
                        f"amount={payment_locked.amount}, balance: {old_balance} → {user.balance}, "
                        f"yookassa_id={yookassa_payment_id}")

                # Check subscription status BEFORE cache invalidation
                has_active_sub = user.subscription_end and user.subscription_end > datetime.utcnow()

                # Invalidate cache (tolerate Redis failures)
                try:
                    redis = await self.payment_repo.get_redis()
                    await redis.delete(f"user:{user.tg_id}:balance")
                except Exception as e:
                    LOG.warning(f"Redis error invalidating cache for user {user.tg_id}: {e}")

                # Send notification to user about successful payment
                await self.on_payment_confirmed(
                    payment_id=payment_id,
                    tx_hash=tx_hash,
                    tg_id=user.tg_id,
                    total_amount=payment_locked.amount,
                    lang=user.lang,
                    has_active_subscription=has_active_sub
                )
                return True

            return False

        except Exception as e:
            LOG.error(f"Error checking YooKassa payment {payment_id}: {e}")
            return False

    async def cancel_payment(self, payment_id: int) -> bool:
        try:
            # Получаем локальный платеж
            payment = await self.payment_repo.get_payment(payment_id)
            if not payment or payment.get('status') != 'pending':
                LOG.warning(f"Payment {payment_id} not found or not pending, cannot cancel.")
                return False

            # Безопасно достаем extra_data
            extra_data = payment.get('extra_data') or {}
            yookassa_payment_id = extra_data.get('yookassa_payment_id')

            if not yookassa_payment_id:
                LOG.warning(f"Payment {payment_id} has no yookassa_payment_id, skipping remote cancel.")
                return True  # локально можно считать отменённым

            # Убеждаемся, что SDK настроен
            await self._ensure_configured()
            idempotency_key = uuid.uuid4()

            LOG.info(f"Attempting to cancel YooKassa payment {yookassa_payment_id} for local payment {payment_id}")

            # Отмена через SDK в отдельном потоке
            cancelled_payment = await asyncio.to_thread(
                YooKassaPayment.cancel, yookassa_payment_id, idempotency_key
            )

            if getattr(cancelled_payment, 'status', None) == 'canceled':
                LOG.info(f"Successfully cancelled YooKassa payment {yookassa_payment_id}")
                return True
            else:
                LOG.warning(f"Could not cancel YooKassa payment {yookassa_payment_id}, status is {getattr(cancelled_payment, 'status', 'unknown')}")
                return False

        except Exception as e:
            LOG.error(f"Error cancelling YooKassa payment for local_id {payment_id}: {e}", exc_info=True)
            return False

    async def on_payment_confirmed(
        self,
        payment_id: int,
        tx_hash: Optional[str] = None,
        tg_id: Optional[int] = None,
        total_amount: Optional[Decimal] = None,
        lang: str = "ru",
        has_active_subscription: bool = False
    ):
        """
        Callback when payment is confirmed.

        Sends Telegram notification to user about successful payment.
        """
        LOG.info(f"YooKassa payment confirmed callback: id={payment_id}, tx={tx_hash}")

        # Send notification if bot is available and we have user info
        if self.bot and tg_id and total_amount:
            from app.utils.payment_notifications import send_payment_notification

            try:
                await send_payment_notification(
                    bot=self.bot,
                    tg_id=tg_id,
                    amount=total_amount,
                    lang=lang,
                    has_active_subscription=has_active_subscription
                )
            except Exception as e:
                LOG.error(f"Error sending payment notification to {tg_id}: {e}")
                # Don't fail payment confirmation if notification fails


# ===== END FILE: app/payments/gateway/yookassa.py =====



# ===== START FILE: app/locales/locales.py =====

LOCALES = {
    "ru": {
        "cmd_start": "Добро пожаловать в OrbitVPN! Выберите опцию:",
        "change_language": "Язык",
        "buy_subscription": "Купить подписку",
        "no_configs": "У вас ещё нет VPN конфигураций.",
        "your_configs": "Ваши VPN конфигурации:",
        "config_created": "Конфигурация создана. Ваши VPN конфигурации:",
        'your_config': 'Ваша подписка:',
        "config_selected": "Нажмите чтобы скопировать:",
        "config_deleted": "Конфигурация удалена",
        "balance_text": "Ваш баланс: {balance} RUB",
        "welcome": "Добро пожаловать в OrbitVPN! Выберите опцию:",
        "settings_text": "Ваши настройки:",
        "choose_language": "Выберите язык:",
        "language_updated": "Язык обновлён.",
        "under_development": "Это в разработке",
        "balance": "Баланс 💵",
        "my_vpn": "Мой VPN 👤",
        "help": "Помощь 💬",
        "settings": "Настройки ⚙️",
        "low_balance": "Недостаточно средств.",
        "add_funds": "Пополнить баланс 💸",
        "transaction_history": "История транзакций",
        "referral": "Реферал",
        "error_creating_config": "Ошибка при создании конфигурации. Попробуйте позже или свяжитесь с поддержкой.",
        "add_config": "Добавить конфигурацию",
        "back_main": "В главное меню",
        "back": "Назад",
        "delete_config": "Удалить",
        "qr_code": "QR-код",
        "error_creating_payment": "Ошибка при создании платежа. Попробуйте позже.",
        "top_up_text": "Ссылка для пополнения {amount} RUB: {payment_url}",
        "link_not_found": "(Ссылка не найдена)",
        "creating_config": "Создаём конфигурацию...",
        "instruction": "Установка",
        "instruction_text": (
            "Установка VLESS-конфига:\n\n"
            "1. Скачайте клиент V2RayTun (или аналог) для вашей платформы.\n"
            "2. Откройте приложение и найдите кнопку импорта конфигурации.\n"
            "3. Вставьте ссылку VLESS, которую прислал бот.\n"
            "4. Сохраните конфигурацию и включите соединение."
        ),
        "max_configs_reached": "Достигнут максимум конфигураций (1). Удалите старую.",
        "no_servers": "Нет доступных серверов. Свяжитесь с поддержкой.",
        "buy_sub_text": "Выберите подписку:",
        "sub_1m": "1 мес - {price} RUB",
        "sub_3m": "3 мес - {price} RUB",
        "sub_6m": "6 мес - {price} RUB",
        "sub_12m": "12 мес - {price} RUB",
        "sub_success": "Подписка куплена! Конфигурация создана.",
        "payment_method": "Выберите способ оплаты:",
        "pm_stars": "Telegram Stars",
        "select_amount": "Выберите сумму пополнения:",
        "enter_amount": "Введите сумму пополнения (RUB, минимум 200):",
        "invalid_amount": "Неверная сумма. Введите число >=200.",
        "pay_button": "Оплатить",
        "payment_created": "Оплатите {amount} Stars для пополнения {amount} RUB.",
        'renew_config': 'Продлить',
        'config_expired': 'Истёк',
        'config_active': 'Активно',
        "free_trial_created": "Пробная подписка на 3 дня активирована.",
        "free_trial_activated": "Вам доступен бесплатный пробный период 3 дня",
        "referral_text": "Пригласите друга — каждый получит 50 RUB.\n\nВаша реферальная ссылка:\n{ref_link}",
        "sub_renewed_auto": "Подписка продлена автоматически.",
        "sub_expired_low_balance": "Подписка истекла (недостаточно средств для авто-продления).",
        "sub_renewed": "Подписка продлена.",
        'buy_sub': 'Купить подписку',
        "no_active_subscription": "У вас нет активной подписки. Купите подписку, чтобы создать конфигурацию.",
        "subscription_expired": "Ваша подписка истекла. Продлите подписку, чтобы продолжить использование VPN.",
        "config_created": "Конфигурация создана успешно!",
        "your_configs_with_sub": "Ваша подписка:\n\nАктивна до: {expire_date}",
        "no_configs_has_sub": "У вас нет конфигураций\n\nПодписка активна до: {expire_date}",
        "subscription_active_until": "Подписка активна до: {expire_date}",
        "subscription_expired_on": "Подписка истекла: {expire_date}",
        "renew_subscription_btn": "Продлить подписку",
        "no_subscription": "Нет активной подписки",
        "sub_purchased": "Подписка успешно приобретена!",
        "sub_purchased_create_config": "Подписка куплена! Создайте конфигурацию.",
        "create_first_config": "Подписка активирована!\n\nТеперь создайте свою первую конфигурацию VPN:",
        "error_buying_sub": "Ошибка при покупке подписки",
        "sub_success_with_expire": "Подписка активна до: {expire_date}",
        "extend_subscription": "Выберите срок продления:",
        "current_sub_until": "Подписка действует до: {expire_date}",
        "add_config": "Добавить конфигурацию",
        'share': 'Поделиться',
        "too_fast": "Вы отправляете слишком много запросов",
        'custom_amount': 'Другая сумма',
        'subscription_from': 'Подписка от {price} RUB/мес',
        'extend_by_1m': '+ 1 мес ({price} RUB)',
        'extend_by_3m': '+ 3 мес ({price} RUB)',
        'extend_by_6m': '+ 6 мес ({price} RUB)',
        'extend_by_12m': '+ 12 мес ({price} RUB)',
        'config': 'Конфигурация',
        'payment_success': '✓ Баланс пополнен на {amount:.2f} RUB\n\nТеперь вы можете:',
        'top_up_text_ton': "Пополнить {amount} RUB\nОтправьте {ton_amount:.6f} TON на кошелек:\n{wallet}",
        'extend': 'Продлить',
        'renew_now': 'Продлить',
        'ton_payment_instruction': (
                "Оплата через TON\n\n"
                "Отправьте {ton_amount} на кошелек:\n"
                "{wallet}\n\n"
                "Комментарий: {comment}\n\n"
                "Без комментария платёж не будет засчитан."    
        ),
        'stars_add_title': 'Пополнение баланса',
        'stars_add_description': 'Пополните баланс на {amount} RUB',
        'how_to_install': 'Инструкция по установке',
        'stars_invoice_sent': 'Счёт отправлен. Проверьте сообщения',
        'stars_price_label': 'Пополнение',
        'config_not_found': 'Конфигурация не найдена',
        'error_deleting_config': 'Ошибка при удалении конфигурации',
        'no_servers_or_cache_error': 'Нет доступных серверов. Попробуйте позже',
        'payment_already_processed': 'Платёж уже обработан',
        'ton_payment_intro': 'Оплата через TON',
        'ton_send_amount': 'Сумма к оплате: {expected_ton} TON (~{amount} RUB)',
        'ton_wallet': 'Кошелёк: {wallet}',
        'ton_comment': 'Комментарий: {comment}',
        'ton_comment_warning': '⚠️ Важно: Без комментария платёж не будет засчитан!',
        'cryptobot_payment_intro': 'Оплата через CryptoBot',
        'cryptobot_amount': 'Сумма к оплате: {amount} RUB',
        'cryptobot_click_button': 'Нажмите кнопку ниже для оплаты',
        'yookassa_payment_intro': 'Оплата через YooKassa',
        'yookassa_amount': 'Сумма к оплате: {amount} RUB',
        'yookassa_click_button': 'Нажмите кнопку ниже для оплаты',
        'cancel_payment': 'Отменить платёж',
        'payment_cancelled': 'Платёж отменён',
        'payment_cancel_error': 'Не удалось отменить платёж',
        'payment_expired': 'Платёж истёк',
        'payment_not_found': 'Платёж не найден или уже обработан',
        'service_temporarily_unavailable': 'Сервис временно недоступен. Пожалуйста, попробуйте позже.',
        'active_payment_exists': 'У вас уже есть активный платёж на {amount} RUB через {method}. Хотите продолжить с ним или создать новый?',
        'continue_payment': 'Продолжить',
        'create_new_payment': 'Создать новый',
        'payment_sent': 'Отправил оплату',
        'payment_checking': 'Проверяем платёж...\n\nБаланс будет зачислен автоматически после подтверждения транзакции в блокчейне.\n\nОбычно это занимает 1-2 минуты.',
        'admin': 'Админ',
        'admin_panel_welcome': '🔧 Панель администратора\n\nВыберите раздел:',
        'admin_stats': 'Статистика',
        'admin_users': 'Пользователи',
        'admin_payments': 'Платежи',
        'admin_servers': 'Серверы',
        'admin_broadcast': 'Рассылка',
        'access_denied': 'Доступ запрещён',
        'admin_stats_placeholder': '📊 Статистика бота\n\n[В разработке]\n\nЗдесь будет:\n- Общее количество пользователей\n- Активные подписки\n- Доход за период\n- Конверсия',
        'admin_users_placeholder': '👥 Управление пользователями\n\n[В разработке]\n\nЗдесь будет:\n- Поиск пользователей\n- Выдача/отзыв подписок\n- Блокировка пользователей\n- История активности',
        'admin_payments_placeholder': '💰 Статистика платежей\n\n[В разработке]\n\nЗдесь будет:\n- Последние платежи\n- Статистика по методам оплаты\n- Неудачные платежи\n- Общий доход',
        'admin_servers_placeholder': '🖥 Статус серверов\n\n[В разработке]\n\nЗдесь будет:\n- Список Marzban серверов\n- Загрузка серверов\n- Активные конфигурации\n- Управление серверами',
        'admin_broadcast_placeholder': '📢 Рассылка сообщений\n\n[В разработке]\n\nЗдесь будет:\n- Отправка сообщений всем пользователям\n- Отправка определённым группам\n- Статистика доставки',
        # Notifications settings
        'notifications': 'Уведомления',
        'notifications_enabled': 'Включены 🟢',
        'notifications_disabled': 'Выключены 🔴',
        'notifications_text': 'Уведомления\n\nВключают в себя:\n• Оповещения о статусе подписки (окончание, продление)\n• Новости о сервисе OrbitVPN\n• Обновления функционала\n• Специальные предложения\n\nТекущий статус: {status}',
        'toggle_notifications': 'Изменить',
        'notifications_updated': 'Настройки уведомлений обновлены',
        'sub_expiry_3days_1': 'Ваша подписка истекает через 3 дня!\n\nРекомендуем продлить её заранее, чтобы избежать перебоев в работе VPN.',
        'sub_expiry_3days_2': 'Осталось всего 3 дня до окончания подписки.\n\nПродлите сейчас и продолжайте пользоваться безопасным интернетом без ограничений!',
        'sub_expiry_3days_3': 'Напоминание: через 3 дня закончится ваша подписка OrbitVPN.\n\nНе забудьте продлить, чтобы оставаться защищённым в сети!',
        'sub_expiry_1day_1': 'Внимание! Ваша подписка истекает завтра.\n\nПродлите прямо сейчас, чтобы не потерять доступ к VPN.',
        'sub_expiry_1day_2': 'Последний день! Завтра заканчивается ваша подписка.\n\nОбновите подписку сегодня и сохраните непрерывный доступ к защищённому интернету.',
        'sub_expiry_1day_3': 'До окончания подписки остался 1 день.\n\nПродлите сейчас — это займёт меньше минуты!',
        'quick_renewal_info': '💰 Месяц: {price}₽ | Нужно: {needed}₽',
        'quick_renewal_ready': '✓ Баланс достаточен! Месяц: {price}₽',
        'sub_expired_1': 'Ваша подписка OrbitVPN истекла.\n\nПополните баланс и продлите подписку, чтобы восстановить доступ к защищённому интернету.',
        'sub_expired_2': 'Подписка закончилась. Все ваши конфигурации приостановлены.\n\nОбновите подписку прямо сейчас для продолжения использования VPN.',
        'sub_expired_3': 'Срок действия вашей подписки истёк.\n\nПродлите подписку, чтобы снова пользоваться безопасным и быстрым VPN без ограничений!',
        'auto_renewal_success': '✓ Подписка автоматически продлена!\n\n📅 +{days} дней за {price:.0f}₽\n💰 Баланс: {balance:.2f}₽\n⏰ Активна до: {expire_date}',
        # Admin config cleanup
        'admin_clear_configs': 'Очистить конфиги',
        'admin_clear_configs_confirm': '🗑 Очистка истекших конфигов\n\nУдалит все конфиги пользователей, чья подписка истекла более 14 дней назад.\n\nВы уверены?',
        'admin_cleanup_started': '⏳ Запущена очистка истекших конфигов...',
        'admin_cleanup_result': '✅ Очистка завершена\n\nПроверено: {total}\nУдалено: {deleted}\nОшибок: {failed}\nПропущено: {skipped}',
        'confirm_yes': 'Да, удалить',
        'confirm_no': 'Отмена',
        # Broadcast
        'broadcast_enter_message': '📢 Рассылка сообщений\n\nВведите текст сообщения, которое хотите разослать пользователям:',
        'broadcast_settings_prompt': '⚙️ Настройки рассылки\n\nВыберите кому и когда отправить сообщение:',
        'broadcast_target_all': 'Всем пользователям',
        'broadcast_target_subscribed': 'С уведомлениями',
        'broadcast_time_now': 'Сейчас',
        'broadcast_send': '✉️ Подтвердить',
        'broadcast_execute': '✅ Отправить',
        'broadcast_preview': '📝 Предпросмотр рассылки\n\nСообщение:\n{message}\n\nКому: {target}\nКогда: {time}\n\nОтправить?',
        'broadcast_in_progress': '⏳ Отправка сообщений...',
        'broadcast_completed': '✅ Рассылка завершена!\n\nВсего пользователей: {total}\nОтправлено: {success}\nОшибок: {failed}',
        'broadcast_cancelled': '❌ Рассылка отменена',
        'broadcast_error_no_message': '❌ Сообщение не найдено. Попробуйте ещё раз.',
        'cancel': 'Отмена',
        # Admin Users Management
        'admin_users_stats': '👥 Статистика пользователей\n\nВсего: {total}\nС активной подпиской: {active_sub}\nБез подписки: {no_sub}\nНовых за 24ч: {new_24h}\n\nСредний баланс: {avg_balance:.2f} RUB',
        'admin_search_user': 'Поиск',
        'admin_user_list': 'Список',
        'admin_enter_user_id': 'Введите Telegram ID пользователя для поиска:',
        'admin_user_not_found': 'Пользователь не найден',
        'admin_user_info': '👤 Пользователь {username}\n\nID: {tg_id}\nБаланс: {balance} RUB\nКонфигов: {configs}\nЯзык: {lang}\nУведомления: {notifications}\nРеферер: {referrer}\nДата регистрации: {created_at}',
        'admin_user_subscription': '\n\nПодписка:\n{subscription}',
        'admin_sub_active': 'Активна до: {expire_date}',
        'admin_sub_expired': 'Истекла: {expire_date}',
        'admin_sub_none': 'Нет подписки',
        'admin_grant_sub': 'Выдать подписку',
        'admin_revoke_sub': 'Отозвать подписку',
        'admin_add_balance': 'Пополнить баланс',
        'admin_view_configs': 'Посмотреть конфиги',
        'admin_enter_days': 'Введите количество дней для подписки:',
        'admin_invalid_days': 'Неверное количество дней',
        'admin_sub_granted': '✅ Подписка выдана на {days} дней',
        'admin_sub_revoked': '✅ Подписка отозвана',
        'admin_enter_balance_amount': 'Введите сумму для пополнения (может быть отрицательной):',
        'admin_invalid_balance_amount': 'Неверная сумма',
        'admin_balance_added': '✅ Баланс изменен на {amount} RUB\nНовый баланс: {new_balance} RUB',
        'admin_user_configs': '🔧 Конфигурации пользователя {tg_id}:\n\n{configs_list}',
        'admin_no_configs': 'У пользователя нет конфигураций',
        'admin_page': 'Страница {page}/{total}',
        'admin_next_page': 'Далее →',
        'admin_prev_page': '← Назад',
        # Admin Payments Statistics
        'admin_payments_stats': '💰 Статистика платежей\n\nВсего платежей: {total}\nУспешных: {confirmed}\nВ ожидании: {pending}\nОтменено/Истекло: {failed}\n\nОбщий доход: {total_revenue:.2f} RUB\nЗа сегодня: {today_revenue:.2f} RUB\nЗа неделю: {week_revenue:.2f} RUB\nЗа месяц: {month_revenue:.2f} RUB',
        'admin_payment_methods': '\n\nПо методам:\n{methods_stats}',
        'admin_recent_payments': 'Последние платежи',
        'admin_payment_item': '• {amount} RUB через {method}\n  Пользователь: {tg_id}\n  Статус: {status}\n  Дата: {date}',
        'admin_no_recent_payments': 'Нет недавних платежей',
        # Admin Servers Status
        'admin_servers_stats': '🖥 Статус серверов Marzban\n\nИнстансов: {total}\nАктивных: {active}\nНеактивных: {inactive}',
        'admin_instance_item': '\n\n📡 {name} ({id})\nURL: {url}\nПриоритет: {priority}\nСтатус: {status}\nУзлов: {nodes}\nИсключено узлов: {excluded}',
        'admin_instance_active': '✅ Активен',
        'admin_instance_inactive': '⛔ Неактивен',
        'admin_view_nodes': 'Узлы сервера',
        'admin_instance_nodes': '🖥 Узлы инстанса {name}:\n\n{nodes_list}',
        'admin_node_item': '• {name}\n  ID: {id}\n  Статус: {status}\n  Пользователей: {users}\n  Трафик: ↑{uplink} ↓{downlink}\n  Коэффициент: {coefficient}',
        'admin_no_nodes': 'Нет доступных узлов',
        'admin_node_online': '🟢 Онлайн',
        'admin_node_offline': '🔴 Оффлайн',
        # Admin Bot Statistics
        'admin_bot_stats': '📊 Общая статистика бота\n\n👥 Пользователи:\nВсего: {total_users}\nНовых за 24ч: {new_users_24h}\nНовых за 7д: {new_users_7d}\nНовых за 30д: {new_users_30d}\n\n📅 Подписки:\nАктивных: {active_subs}\nИстекших: {expired_subs}\nНе покупали: {no_subs}\n\n💰 Доходы:\nВсего: {total_revenue:.2f} RUB\nЗа сегодня: {today_revenue:.2f} RUB\nЗа неделю: {week_revenue:.2f} RUB\nЗа месяц: {month_revenue:.2f} RUB\n\n🔧 Конфигурации:\nВсего: {total_configs}\nАктивных: {active_configs}\nУдаленных: {deleted_configs}',
        # Promocodes
        'activate_promocode': 'Активировать промокод',
        'enter_promocode': 'Введите промокод:',
        'promocode_activated_success': '✅ Промокод активирован!\n\nПри следующем пополнении вы получите {bonus}',
        'promocode_not_found': '❌ Промокод не найден',
        'promocode_inactive': '❌ Промокод недействителен',
        'promocode_expired': '❌ Срок действия промокода истёк',
        'promocode_limit_reached': '❌ Достигнут лимит использований промокода',
        'promocode_already_used': '❌ Вы уже использовали этот промокод',
        'promocode_activation_error': '❌ Ошибка при активации промокода',
        'promocode_already_active': '✅ У вас уже активирован промокод {code}\n\nБонус: {bonus}',
        'bonus_on_deposit': 'бонус при пополнении',
        'promocode_bonus_applied': '🎁 Применён промокод {code}: +{bonus_amount:.2f} RUB бонус ({percent}%)',
    },
    "en": {
        "cmd_start": "Welcome to OrbitVPN! Choose an option:",
        "change_language": "Language",
        "buy_subscription": "Buy subscription",
        "no_configs": "You don't have any VPN configs yet.",
        "your_configs": "Your VPN configs:",
        "config_created": "Config created. Your VPN configs:",
        'your_config': 'Your config:',
        "config_selected": "Click to copy:",
        "config_deleted": "Config deleted",
        "balance_text": "Your balance is {balance} RUB",
        "welcome": "Welcome to OrbitVPN! Choose an option:",
        "settings_text": "Your settings:",
        "choose_language": "Choose your language:",
        "language_updated": "Language updated.",
        "under_development": "It's currently under development",
        "balance": "Balance 💵",
        "my_vpn": "My VPN 👤",
        "help": "Help 💬",
        "settings": "Settings ⚙️",
        "low_balance": "Not enough funds.",
        "add_funds": "Add Funds 💸",
        "transaction_history": "Transaction History",
        "referral": "Referral",
        "error_creating_config": "Error creating config. Try later or contact support.",
        "add_config": "Add Config",
        "back_main": "Back to main",
        "back": "Back",
        "delete_config": "Delete",
        "qr_code": "QR Code",
        "error_creating_payment": "Error creating payment. Try later.",
        "top_up_text": "Click to top up {amount} RUB: {payment_url}",
        "link_not_found": "(Link not found)",
        "creating_config": "Creating config...",
        "instruction": "Installation",
        "instruction_text": (
            "VLESS configuration installation:\n\n"
            "1. Download V2RayTun client (or similar) for your platform.\n"
            "2. Open the app and find the import configuration button.\n"
            "3. Paste the VLESS link provided by the bot.\n"
            "4. Save the configuration and enable the connection."
        ),
        "max_configs_reached": "Max configs reached (1). Delete old one.",
        "no_servers": "No servers available. Contact support.",
        "buy_sub_text": "Choose subscription:",
        "sub_1m": "1 mo - {price} RUB",
        "sub_3m": "3 mo - {price} RUB",
        "sub_6m": "6 mo - {price} RUB",
        "sub_12m": "12 mo - {price} RUB",
        "sub_success": "Subscription bought! Config created.",
        "payment_method": "Choose payment method:",
        "pm_stars": "Telegram Stars",
        "select_amount": "Select top-up amount:",
        "enter_amount": "Enter top-up amount (RUB, min 200):",
        "invalid_amount": "Invalid amount. Enter number >=200.",
        "pay_button": "Pay",
        "payment_created": "Pay {amount} Stars to top up {amount} RUB.",
        'renew_config': 'Renew',
        'config_expired': 'Expired',
        'config_active': 'Active',
        "free_trial_created": "You got a free 3-day trial subscription.",
        "free_trial_activated": "You have access to a free 3-day trial period",
        "referral_text": "Invite a friend — each of you get 50 RUB.\n\nYour referral link:\n{ref_link}",
        "sub_renewed_auto": "Subscription renewed automatically.",
        "sub_expired_low_balance": "Subscription expired (low balance for auto-renew).",
        "sub_renewed": "Subscription renewed.",
        'buy_sub': 'Subscribe',
        "no_active_subscription": "You don't have an active subscription. Buy a subscription to create a configuration.",
        "subscription_expired": "Your subscription has expired. Renew your subscription to continue using VPN.",
        "config_created": "Configuration created successfully!",
        "your_configs_with_sub": "Your subscription:\n\nActive until: {expire_date}",
        "no_configs_has_sub": "You have no configurations\n\nSubscription active until: {expire_date}",
        "subscription_active_until": "Subscription active until: {expire_date}",
        "subscription_expired_on": "Subscription expired: {expire_date}",
        "renew_subscription_btn": "Renew Subscription",
        "no_subscription": "No active subscription",
        "sub_purchased": "Subscription purchased successfully!",
        "sub_purchased_create_config": "Subscription purchased! Create a configuration.",
        "create_first_config": "Subscription activated!\n\nNow create your first VPN configuration:",
        "error_buying_sub": "Error purchasing subscription",
        "sub_success_with_expire": "Subscription active until: {expire_date}",
        "extend_subscription": "Select the duration:",
        "current_sub_until": "Subscription valid until: {expire_date}",
        "add_config": "Add configuration",
        'share': 'Share',
        "too_fast": "You're sending too many requests",
        'custom_amount': 'Custom amount',
        'subscription_from': 'Subscription from {price} RUB/mo',
        'extend_by_1m': '+ 1 mo ({price} RUB)',
        'extend_by_3m': '+ 3 mo ({price} RUB)',
        'extend_by_6m': '+ 6 mo ({price} RUB)',
        'extend_by_12m': '+ 12 mo ({price} RUB)',
        'config': 'Config',
        'payment_success': '✓ Balance topped up by {amount:.2f} RUB\n\nYou can now:',
        'top_up_text_ton': "Top up {amount} RUB\nSend {ton_amount:.6f} TON to wallet:\n{wallet}",
        'extend': 'Extend',
        'renew_now': 'Renew',
        'ton_payment_instruction': (
                "Payment via TON\n\n"
                "Send {ton_amount} to the wallet:\n"
                "{wallet}\n\n"
                "Comment: {comment}\n\n"
                "Payment without the comment will not be credited."
        ),
        'stars_add_title': 'Add funds to balance',
        'stars_add_description': 'Add {amount} RUB to your balance',
        'how_to_install': 'How to install',
        'stars_invoice_sent': 'Invoice sent. Check your messages',
        'stars_price_label': 'Top-up',
        'config_not_found': 'Configuration not found',
        'error_deleting_config': 'Error deleting configuration',
        'no_servers_or_cache_error': 'No available servers. Try again later',
        'payment_already_processed': 'Payment already processed',
        'ton_payment_intro': 'Payment via TON',
        'ton_send_amount': 'Amount to pay: {expected_ton} TON (~{amount} RUB)',
        'ton_wallet': 'Wallet: {wallet}',
        'ton_comment': 'Comment: {comment}',
        'ton_comment_warning': '⚠️ Important: Payment without comment will not be credited!',
        'cryptobot_payment_intro': 'Payment via CryptoBot',
        'cryptobot_amount': 'Amount to pay: {amount} RUB',
        'cryptobot_click_button': 'Click the button below to pay',
        'yookassa_payment_intro': 'Payment via YooKassa',
        'yookassa_amount': 'Amount to pay: {amount} RUB',
        'yookassa_click_button': 'Click the button below to pay',
        'cancel_payment': 'Cancel payment',
        'payment_cancelled': 'Payment cancelled',
        'payment_cancel_error': 'Failed to cancel payment',
        'payment_expired': 'Payment expired',
        'payment_not_found': 'Payment not found or already processed',
        'service_temporarily_unavailable': 'Service temporarily unavailable. Please try again later.',
        'active_payment_exists': 'You already have an active payment for {amount} RUB via {method}. Continue with it or create a new one?',
        'continue_payment': 'Continue',
        'create_new_payment': 'Create new',
        'payment_sent': 'Payment sent',
        'payment_checking': 'Checking payment...\n\nBalance will be credited automatically after blockchain confirmation.\n\nUsually takes 1-2 minutes.',
        'admin': 'Admin',
        'admin_panel_welcome': '🔧 Admin Panel\n\nSelect a section:',
        'admin_stats': 'Statistics',
        'admin_users': 'Users',
        'admin_payments': 'Payments',
        'admin_servers': 'Servers',
        'admin_broadcast': 'Broadcast',
        'access_denied': 'Access denied',
        'admin_stats_placeholder': '📊 Bot Statistics\n\n[Under development]\n\nWill include:\n- Total users\n- Active subscriptions\n- Revenue by period\n- Conversion rates',
        'admin_users_placeholder': '👥 User Management\n\n[Under development]\n\nWill include:\n- User search\n- Grant/revoke subscriptions\n- Block users\n- Activity history',
        'admin_payments_placeholder': '💰 Payment Statistics\n\n[Under development]\n\nWill include:\n- Recent payments\n- Statistics by payment method\n- Failed payments\n- Total revenue',
        'admin_servers_placeholder': '🖥 Server Status\n\n[Under development]\n\nWill include:\n- Marzban server list\n- Server load\n- Active configurations\n- Server management',
        'admin_broadcast_placeholder': '📢 Message Broadcast\n\n[Under development]\n\nWill include:\n- Send messages to all users\n- Send to specific groups\n- Delivery statistics',
        # Notifications settings
        'notifications': 'Notifications',
        'notifications_enabled': 'Enabled 🟢',
        'notifications_disabled': 'Disabled 🔴',
        'notifications_text': 'Notifications\n\nInclude:\n• Subscription status alerts (expiration, renewal)\n• OrbitVPN service news\n• Feature updates\n• Special offers\n\nCurrent status: {status}',
        'toggle_notifications': 'Toggle',
        'notifications_updated': 'Notification settings updated',
        'sub_expiry_3days_1': 'Your subscription expires in 3 days!\n\nWe recommend renewing it in advance to avoid VPN service interruptions.',
        'sub_expiry_3days_2': 'Only 3 days left until your subscription ends.\n\nRenew now and continue enjoying unrestricted secure internet access!',
        'sub_expiry_3days_3': 'Reminder: your OrbitVPN subscription expires in 3 days.\n\nDon\'t forget to renew to stay protected online!',
        'sub_expiry_1day_1': 'Attention! Your subscription expires tomorrow.\n\nRenew right now to keep your VPN access.',
        'sub_expiry_1day_2': 'Last day! Your subscription ends tomorrow.\n\nRenew today and maintain uninterrupted access to secure internet.',
        'sub_expiry_1day_3': '1 day left until your subscription expires.\n\nRenew now — it takes less than a minute!',
        'quick_renewal_info': '💰 Month: {price}₽ | Need: {needed}₽',
        'quick_renewal_ready': '✓ Balance sufficient! Month: {price}₽',
        'sub_expired_1': 'Your OrbitVPN subscription has expired.\n\nTop up your balance and renew your subscription to restore access to secure internet.',
        'sub_expired_2': 'Subscription ended. All your configurations have been suspended.\n\nRenew your subscription now to continue using VPN.',
        'sub_expired_3': 'Your subscription has expired.\n\nRenew now to enjoy safe and fast VPN without limitations again!',
        'auto_renewal_success': '✓ Subscription auto-renewed!\n\n📅 +{days} days for {price:.0f}₽\n💰 Balance: {balance:.2f}₽\n⏰ Active until: {expire_date}',
        # Admin config cleanup
        'admin_clear_configs': 'Clear Configs',
        'admin_clear_configs_confirm': '🗑 Clean up expired configs\n\nWill delete all configs for users whose subscription expired more than 14 days ago.\n\nAre you sure?',
        'admin_cleanup_started': '⏳ Expired config cleanup started...',
        'admin_cleanup_result': '✅ Cleanup completed\n\nChecked: {total}\nDeleted: {deleted}\nFailed: {failed}\nSkipped: {skipped}',
        'confirm_yes': 'Yes, delete',
        'confirm_no': 'Cancel',
        # Broadcast
        'broadcast_enter_message': '📢 Message Broadcast\n\nEnter the message text you want to send to users:',
        'broadcast_settings_prompt': '⚙️ Broadcast Settings\n\nChoose who and when to send the message:',
        'broadcast_target_all': 'All users',
        'broadcast_target_subscribed': 'With notifications',
        'broadcast_time_now': 'Now',
        'broadcast_send': '✉️ Confirm',
        'broadcast_execute': '✅ Send',
        'broadcast_preview': '📝 Broadcast Preview\n\nMessage:\n{message}\n\nTo: {target}\nWhen: {time}\n\nSend?',
        'broadcast_in_progress': '⏳ Sending messages...',
        'broadcast_completed': '✅ Broadcast completed!\n\nTotal users: {total}\nSent: {success}\nFailed: {failed}',
        'broadcast_cancelled': '❌ Broadcast cancelled',
        'broadcast_error_no_message': '❌ Message not found. Please try again.',
        'cancel': 'Cancel',
        # Admin Users Management
        'admin_users_stats': '👥 User Statistics\n\nTotal: {total}\nWith active subscription: {active_sub}\nNo subscription: {no_sub}\nNew in 24h: {new_24h}\n\nAverage balance: {avg_balance:.2f} RUB',
        'admin_search_user': 'Search',
        'admin_user_list': 'List',
        'admin_enter_user_id': 'Enter user Telegram ID to search:',
        'admin_user_not_found': 'User not found',
        'admin_user_info': '👤 User {username}\n\nID: {tg_id}\nBalance: {balance} RUB\nConfigs: {configs}\nLanguage: {lang}\nNotifications: {notifications}\nReferrer: {referrer}\nRegistration date: {created_at}',
        'admin_user_subscription': '\n\nSubscription:\n{subscription}',
        'admin_sub_active': 'Active until: {expire_date}',
        'admin_sub_expired': 'Expired: {expire_date}',
        'admin_sub_none': 'No subscription',
        'admin_grant_sub': 'Grant subscription',
        'admin_revoke_sub': 'Revoke subscription',
        'admin_add_balance': 'Add balance',
        'admin_view_configs': 'View configs',
        'admin_enter_days': 'Enter number of days for subscription:',
        'admin_invalid_days': 'Invalid number of days',
        'admin_sub_granted': '✅ Subscription granted for {days} days',
        'admin_sub_revoked': '✅ Subscription revoked',
        'admin_enter_balance_amount': 'Enter amount to add (can be negative):',
        'admin_invalid_balance_amount': 'Invalid amount',
        'admin_balance_added': '✅ Balance changed by {amount} RUB\nNew balance: {new_balance} RUB',
        'admin_user_configs': '🔧 User {tg_id} configurations:\n\n{configs_list}',
        'admin_no_configs': 'User has no configurations',
        'admin_page': 'Page {page}/{total}',
        'admin_next_page': 'Next →',
        'admin_prev_page': '← Back',
        # Admin Payments Statistics
        'admin_payments_stats': '💰 Payment Statistics\n\nTotal payments: {total}\nConfirmed: {confirmed}\nPending: {pending}\nCancelled/Expired: {failed}\n\nTotal revenue: {total_revenue:.2f} RUB\nToday: {today_revenue:.2f} RUB\nThis week: {week_revenue:.2f} RUB\nThis month: {month_revenue:.2f} RUB',
        'admin_payment_methods': '\n\nBy method:\n{methods_stats}',
        'admin_recent_payments': 'Recent payments',
        'admin_payment_item': '• {amount} RUB via {method}\n  User: {tg_id}\n  Status: {status}\n  Date: {date}',
        'admin_no_recent_payments': 'No recent payments',
        # Admin Servers Status
        'admin_servers_stats': '🖥 Marzban Server Status\n\nInstances: {total}\nActive: {active}\nInactive: {inactive}',
        'admin_instance_item': '\n\n📡 {name} ({id})\nURL: {url}\nPriority: {priority}\nStatus: {status}\nNodes: {nodes}\nExcluded nodes: {excluded}',
        'admin_instance_active': '✅ Active',
        'admin_instance_inactive': '⛔ Inactive',
        'admin_view_nodes': 'Server nodes',
        'admin_instance_nodes': '🖥 Instance {name} nodes:\n\n{nodes_list}',
        'admin_node_item': '• {name}\n  ID: {id}\n  Status: {status}\n  Users: {users}\n  Traffic: ↑{uplink} ↓{downlink}\n  Coefficient: {coefficient}',
        'admin_no_nodes': 'No available nodes',
        'admin_node_online': '🟢 Online',
        'admin_node_offline': '🔴 Offline',
        # Admin Bot Statistics
        'admin_bot_stats': '📊 Bot Statistics\n\n👥 Users:\nTotal: {total_users}\nNew in 24h: {new_users_24h}\nNew in 7d: {new_users_7d}\nNew in 30d: {new_users_30d}\n\n📅 Subscriptions:\nActive: {active_subs}\nExpired: {expired_subs}\nNever purchased: {no_subs}\n\n💰 Revenue:\nTotal: {total_revenue:.2f} RUB\nToday: {today_revenue:.2f} RUB\nThis week: {week_revenue:.2f} RUB\nThis month: {month_revenue:.2f} RUB\n\n🔧 Configurations:\nTotal: {total_configs}\nActive: {active_configs}\nDeleted: {deleted_configs}',
        # Promocodes
        'activate_promocode': 'Activate Promocode',
        'enter_promocode': 'Enter promocode:',
        'promocode_activated_success': '✅ Promocode activated!\n\nOn your next deposit you will get {bonus}',
        'promocode_not_found': '❌ Promocode not found',
        'promocode_inactive': '❌ Promocode is inactive',
        'promocode_expired': '❌ Promocode has expired',
        'promocode_limit_reached': '❌ Promocode usage limit reached',
        'promocode_already_used': '❌ You have already used this promocode',
        'promocode_activation_error': '❌ Error activating promocode',
        'promocode_already_active': '✅ You already have an active promocode {code}\n\nBonus: {bonus}',
        'bonus_on_deposit': 'bonus on deposit',
        'promocode_bonus_applied': '🎁 Promocode {code} applied: +{bonus_amount:.2f} RUB bonus ({percent}%)',
    }
}


def t(lang: str, key: str, **kwargs):
    lang_dict = LOCALES.get(lang, LOCALES["en"])
    text = lang_dict.get(key, key)
    try:
        return text.format(**kwargs)
    except Exception:
        return text


def get_translator(lang: str):
    lang_dict = LOCALES.get(lang, LOCALES["en"])

    def translate(key: str, **kwargs):
        text = lang_dict.get(key, key)
        try:
            return text.format(**kwargs)
        except Exception:
            return text

    return translate

# ===== END FILE: app/locales/locales.py =====



# ===== START FILE: app/locales/locales_mw.py =====

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from app.repo.user import UserRepository
from app.repo.db import get_session
from app.locales.locales import get_translator
from app.utils.redis import get_redis

class LocaleMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user = data.get("event_from_user")
        lang = "ru"  # Default language

        if tg_user:
            # Try Redis first without opening DB session (performance optimization)
            redis_client = await get_redis()
            key = f"user:{tg_user.id}:lang"
            cached_lang = await redis_client.get(key)

            if cached_lang:
                # Cache hit - no DB session needed
                lang = cached_lang
            else:
                # Cache miss - open session only when necessary
                async with get_session() as session:
                    user_repo = UserRepository(session, redis_client)
                    lang = await user_repo.get_lang(tg_user.id)

        data["lang"] = lang
        data["t"] = get_translator(lang)

        return await handler(event, data)

# ===== END FILE: app/locales/locales_mw.py =====



# ===== START FILE: app/core/keyboards.py =====

from collections.abc import Callable
from typing import Any

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import ADMIN_TG_ID, PLANS


def _build_keyboard(
    buttons: list[dict[str, Any]],
    adjust: int | list[int] = 1,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for btn in buttons:
        if 'url' in btn:
            builder.button(text=btn['text'], url=btn['url'])
        elif 'switch_inline_query' in btn:
            builder.button(text=btn['text'], switch_inline_query=btn['switch_inline_query'])
        else:
            builder.button(text=btn['text'], callback_data=btn['callback_data'])

    if isinstance(adjust, int):
        return builder.adjust(adjust).as_markup()
    else:
        return builder.adjust(*adjust).as_markup()


def qr_delete_kb(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    return _build_keyboard([
        {'text': t('delete_config'), 'callback_data': 'delete_qr_msg'},
    ])


def main_kb(t: Callable[[str], str], user_id: int | None = None) -> InlineKeyboardMarkup:
    buttons = [
        {'text': t('my_vpn'), 'callback_data': 'myvpn'},
        {'text': t('balance'), 'callback_data': 'balance'},
        {'text': t('settings'), 'callback_data': 'settings'},
    ]

    # Show Admin button for admin, Help for others
    if user_id and user_id == ADMIN_TG_ID:
        buttons.append({'text': t('admin'), 'callback_data': 'admin_panel'})
    else:
        buttons.append({'text': t('help'), 'url': 'https://t.me/chnddy'})

    return _build_keyboard(buttons, adjust=[1, 1, 2])


def balance_kb(t: Callable[[str], str], show_renew: bool = False) -> InlineKeyboardMarkup:
    """Balance screen keyboard, optionally with renew button for expired subs"""
    buttons = [{'text': t('add_funds'), 'callback_data': 'add_funds'}]

    if show_renew:
        buttons.append({'text': t('renew_subscription_btn'), 'callback_data': 'renew_subscription'})

    buttons.append({'text': t('back_main'), 'callback_data': 'back_main'})

    return _build_keyboard(buttons)


def balance_button_kb(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    """Single balance button for notifications"""
    return _build_keyboard([
        {'text': t('balance'), 'callback_data': 'balance'},
    ])


def get_renewal_notification_keyboard(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    """Keyboard for subscription expiry notifications with renewal action"""
    return _build_keyboard([
        {'text': t('renew_now'), 'callback_data': 'renew_subscription'},
        {'text': t('balance'), 'callback_data': 'balance'},
    ], adjust=2)


def set_kb(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    return _build_keyboard([
        {'text': t('referral'), 'callback_data': 'referral'},
        {'text': t('notifications'), 'callback_data': 'notifications_settings'},
        {'text': t('change_language'), 'callback_data': 'change_lang'},
        {'text': t('back_main'), 'callback_data': 'back_main'},
    ])


def myvpn_kb(
    t: Callable[[str], str],
    configs: list[dict[str, Any]],
    has_active_sub: bool = False,
) -> InlineKeyboardMarkup:
    buttons = []

    if not configs:
        buttons.append({
            'text': t('add_config' if has_active_sub else 'buy_sub'),
            'callback_data': 'add_config' if has_active_sub else 'buy_sub',
        })

    for i, cfg in enumerate(configs, 1):

        display_name = cfg.get('name') or f"{t('config')} {i}"
        buttons.append({
            'text': display_name,
            'callback_data': f"cfg_{cfg['id']}"
        })

    # Show renew button if: active subscription OR expired subscription (has configs but no active sub)
    if has_active_sub or configs:
        buttons.append({'text': t('extend'), 'callback_data': 'renew_subscription'})

    buttons.append({'text': t('back_main'), 'callback_data': 'back_main'})

    return _build_keyboard(buttons)


def actions_kb(t: Callable[[str], str], cfg_id: int | None = None) -> InlineKeyboardMarkup:
    delete_callback = f"delete_cfg_{cfg_id}" if cfg_id else "delete_config"
    qr_callback = f"qr_cfg_{cfg_id}" if cfg_id else "qr_config"

    return _build_keyboard([
        {'text': t('delete_config'), 'callback_data': delete_callback},
        {'text': t('qr_code'), 'callback_data': qr_callback},
        {'text': t('back'), 'callback_data': 'myvpn'},
    ], adjust=2)


def get_language_keyboard(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    return _build_keyboard([
        {'text': '🇺🇸 English', 'callback_data': 'set_lang:en'},
        {'text': '🇷🇺 Русский', 'callback_data': 'set_lang:ru'},
        {'text': t('back'), 'callback_data': 'settings'},
    ])


def get_notifications_keyboard(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    return _build_keyboard([
        {'text': t('toggle_notifications'), 'callback_data': 'toggle_notifications'},
        {'text': t('back'), 'callback_data': 'settings'},
    ])


def sub_kb(t: Callable[[str], str], is_extension: bool = False) -> InlineKeyboardMarkup:
    # Calculate savings for multi-month plans (base: 1-month price)
    monthly_price = PLANS['sub_1m']['price']

    buttons = []
    for key, plan in PLANS.items():
        if not key.startswith('sub_'):
            continue

        months = plan['days'] // 30
        regular_cost = monthly_price * months
        savings = regular_cost - plan['price']
        savings_percent = int((savings / regular_cost) * 100) if regular_cost > 0 else 0

        if is_extension:
            base_text = t(f'extend_by_{key.split("_")[1]}').format(price=plan['price'])
        else:
            base_text = t(key).format(price=plan['price'])

        # Add savings indicator for 3+ month plans (compact format with percentage)
        if months >= 3 and savings_percent > 0:
            text = f"{base_text} 💰(-{savings_percent}%)"
        else:
            text = base_text

        buttons.append({'text': text, 'callback_data': key})

    buttons.append({'text': t('back_main'), 'callback_data': 'back_main'})

    return _build_keyboard(buttons)


def get_payment_methods_keyboard(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    return _build_keyboard([
        {'text': 'TON', 'callback_data': 'select_method_ton'},
        {'text': t('pm_stars'), 'callback_data': 'select_method_stars'},
        {'text': 'CryptoBot (USDT)', 'callback_data': 'select_method_cryptobot'},
        {'text': 'YooKassa (RUB)', 'callback_data': 'select_method_yookassa'},
        {'text': t('back'), 'callback_data': 'balance'},
    ], adjust=1)


def get_referral_keyboard(t: Callable[[str], str], ref_link: str) -> InlineKeyboardMarkup:
    return _build_keyboard([
        {'text': t('share'), 'switch_inline_query': ref_link},
        {'text': t('back'), 'callback_data': 'back_main'},
    ])


def back_balance(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    return _build_keyboard([
        {'text': t('back'), 'callback_data': 'balance'},
    ])


def get_payment_amounts_keyboard(t: Callable[[str], str], method: str) -> InlineKeyboardMarkup:
    # All methods support custom amounts
    return _build_keyboard([
        {'text': '200 RUB', 'callback_data': f'amount_{method}_200'},
        {'text': '500 RUB', 'callback_data': f'amount_{method}_500'},
        {'text': '1000 RUB', 'callback_data': f'amount_{method}_1000'},
        {'text': t('custom_amount'), 'callback_data': f'amount_{method}_custom'},
        {'text': t('back'), 'callback_data': 'add_funds'},
    ], adjust=[3, 1, 1])


def payment_success_actions(t: Callable[[str], str], has_active_sub: bool) -> InlineKeyboardMarkup:
    """Next action buttons after successful payment"""
    if has_active_sub:
        return _build_keyboard([
            {'text': t('extend'), 'callback_data': 'renew_subscription'},
            {'text': t('back_main'), 'callback_data': 'back_main'},
        ])
    else:
        return _build_keyboard([
            {'text': t('buy_sub'), 'callback_data': 'buy_sub'},
            {'text': t('back_main'), 'callback_data': 'back_main'},
        ])


# ===== END FILE: app/core/keyboards.py =====



# ===== START FILE: app/core/handlers/configs.py =====

from io import BytesIO

from aiogram import Router, F
from aiogram.types import CallbackQuery, LinkPreviewOptions, BufferedInputFile
from sqlalchemy.exc import OperationalError, TimeoutError as SQLTimeoutError
import qrcode

from app.core.keyboards import actions_kb, sub_kb, qr_delete_kb
from app.repo.db import get_session
from app.utils.logging import get_logger
from config import INSTALL_GUIDE_URLS
from .utils import safe_answer_callback, get_repositories, update_configs_view

router = Router()
LOG = get_logger(__name__)


@router.callback_query(F.data == "myvpn")
async def myvpn_callback(callback: CallbackQuery, t):
    await safe_answer_callback(callback)

    async with get_session() as session:
        user_repo, _ = await get_repositories(session)
        await update_configs_view(callback, t, user_repo, callback.from_user.id)


@router.callback_query(F.data == "add_config")
async def add_config_callback(callback: CallbackQuery, t):
    tg_id = callback.from_user.id

    async with get_session() as session:
        user_repo, _ = await get_repositories(session)

        await safe_answer_callback(callback, t('creating_config'))

        try:
            await user_repo.create_and_add_config(tg_id)
            await update_configs_view(callback, t, user_repo, tg_id, t('config_created'))

        except ValueError as e:
            error_msg = str(e)
            if "No active subscription" in error_msg or "Subscription expired" in error_msg:
                await callback.message.edit_text(t('subscription_expired'), reply_markup=sub_kb(t))
            elif "Max configs reached" in error_msg:
                await safe_answer_callback(callback, t('max_configs_reached'), show_alert=True)
            elif "No active Marzban instances" in error_msg:
                await safe_answer_callback(callback, t('no_servers_or_cache_error'), show_alert=True)
            else:
                LOG.error(f"ValueError creating config for user {tg_id}: {error_msg}")
                await safe_answer_callback(callback, t('error_creating_config'), show_alert=True)

        except (OperationalError, SQLTimeoutError) as e:
            LOG.error(f"Database error creating config for user {tg_id}: {type(e).__name__}: {e}")
            await safe_answer_callback(callback, t('service_temporarily_unavailable'), show_alert=True)

        except Exception as e:
            LOG.error(f"Unexpected error creating config for user {tg_id}: {type(e).__name__}: {e}")
            await safe_answer_callback(callback, t('error_creating_config'), show_alert=True)


@router.callback_query(F.data.startswith("cfg_"))
async def config_selected(callback: CallbackQuery, t, lang: str):
    await safe_answer_callback(callback)
    cfg_id = int(callback.data.split("_")[1])
    tg_id = callback.from_user.id

    async with get_session() as session:
        user_repo, _ = await get_repositories(session)
        configs = await user_repo.get_configs(tg_id)

        cfg = next((c for c in configs if c["id"] == cfg_id), None)
        if not cfg:
            await callback.message.edit_text(t('config_not_found'), reply_markup=actions_kb(t, cfg_id))
            return

        install_url = INSTALL_GUIDE_URLS.get(lang, INSTALL_GUIDE_URLS["ru"])

        text = f"{t('your_config')}\n\n{t('config_selected')}\n<pre><code>{cfg['vless_link']}</code></pre>\n<a href='{install_url}'>{t('how_to_install')}</a>"
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=actions_kb(t, cfg_id),
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )


@router.callback_query(F.data.startswith("delete_cfg_"))
async def config_delete(callback: CallbackQuery, t):
    cfg_id = int(callback.data.split("_")[2])
    tg_id = callback.from_user.id

    async with get_session() as session:
        user_repo, _ = await get_repositories(session)

        try:
            await user_repo.delete_config(cfg_id, tg_id)
            await safe_answer_callback(callback, t("config_deleted"))
            await update_configs_view(callback, t, user_repo, tg_id)

        except Exception as e:
            LOG.error(f"Error deleting config {cfg_id} for user {tg_id}: {type(e).__name__}: {e}")
            await safe_answer_callback(callback, t('error_deleting_config'), show_alert=True)


@router.callback_query(F.data.startswith("qr_cfg_"))
async def qr_config(callback: CallbackQuery, t):
    await safe_answer_callback(callback)
    cfg_id = int(callback.data.split("_")[2])
    tg_id = callback.from_user.id

    async with get_session() as session:
        user_repo, _ = await get_repositories(session)
        configs = await user_repo.get_configs(tg_id)

        cfg = next((c for c in configs if c["id"] == cfg_id), None)
        if not cfg:
            await safe_answer_callback(callback, t('config_not_found'), show_alert=True)
            return

        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(cfg['vless_link'])
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            bio = BytesIO()
            img.save(bio, format='PNG')
            bio.seek(0)

            photo = BufferedInputFile(bio.read(), filename="qr_code.png")
            await callback.message.answer_photo(
                photo=photo,
                caption=t('your_config'),
                reply_markup=qr_delete_kb(t)
            )

        except Exception as e:
            LOG.error(f"Error generating QR code for config {cfg_id}: {type(e).__name__}: {e}")
            await safe_answer_callback(callback, t('error_creating_config'), show_alert=True)


@router.callback_query(F.data == "delete_qr_msg")
async def delete_qr_message(callback: CallbackQuery):
    await safe_answer_callback(callback)
    await callback.message.delete()


# ===== END FILE: app/core/handlers/configs.py =====



# ===== START FILE: app/core/handlers/auth.py =====

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.core.keyboards import main_kb, get_referral_keyboard
from app.repo.db import get_session
from config import FREE_TRIAL_DAYS
from .utils import safe_answer_callback, get_repositories, extract_referrer_id

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, t):
    tg_id = message.from_user.id
    username = message.from_user.username or f"unknown_{tg_id}"
    referrer_id = extract_referrer_id(message.text)

    # Prevent self-referral
    if referrer_id and referrer_id == tg_id:
        referrer_id = None

    async with get_session() as session:
        user_repo, _ = await get_repositories(session)

        is_new_user = await user_repo.add_if_not_exists(tg_id, username, referrer_id=referrer_id)
        if is_new_user:
            await user_repo.buy_subscription(tg_id, days=FREE_TRIAL_DAYS, price=0.0)

        await message.answer(t("cmd_start"), reply_markup=main_kb(t, user_id=tg_id))

        if is_new_user:
            await message.answer(t("free_trial_activated"))


@router.callback_query(F.data == 'back_main')
async def back_to_main(callback: CallbackQuery, t):
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id
    await callback.message.edit_text(t('welcome'), reply_markup=main_kb(t, user_id=tg_id))


@router.callback_query(F.data == 'referral')
async def referral(callback: CallbackQuery, t):
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    bot_username = (await callback.message.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref_{tg_id}"

    text = t('referral_text', ref_link=f"<pre><code>{ref_link}</code></pre>")
    await callback.message.edit_text(
        text,
        reply_markup=get_referral_keyboard(t, ref_link),
        parse_mode="HTML"
    )


# ===== END FILE: app/core/handlers/auth.py =====



# ===== START FILE: app/core/handlers/__init__.py =====

from aiogram import Router

from app.admin import router as admin_router
from . import auth, configs, subscriptions, payments, settings, admin


def get_router() -> Router:
    main_router = Router()

    main_router.include_router(auth.router)
    main_router.include_router(configs.router)
    main_router.include_router(subscriptions.router)
    main_router.include_router(payments.router)
    main_router.include_router(settings.router)
    main_router.include_router(admin.router)  # Promocode admin commands
    main_router.include_router(admin_router)

    return main_router


router = get_router()


# ===== END FILE: app/core/handlers/__init__.py =====



# ===== START FILE: app/core/handlers/admin.py =====

"""
Admin commands placeholder.
Promocode functionality has been removed.
"""

from aiogram import Router

router = Router()

# This file is kept for import compatibility but promocode functionality has been removed

# ===== END FILE: app/core/handlers/admin.py =====



# ===== START FILE: app/core/handlers/settings.py =====

from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.core.keyboards import set_kb, get_language_keyboard, get_notifications_keyboard
from app.repo.db import get_session
from .utils import safe_answer_callback, get_repositories

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
        reply_markup=get_language_keyboard(t)
    )


@router.callback_query(F.data.startswith("set_lang:"))
async def set_lang_callback(callback: CallbackQuery, t):
    lang = callback.data.split(":")[1]
    tg_id = callback.from_user.id

    async with get_session() as session:
        user_repo, _ = await get_repositories(session)
        await user_repo.set_lang(tg_id, lang)

    await safe_answer_callback(callback, t("language_updated"), show_alert=True)

    from app.locales.locales import get_translator
    new_t = get_translator(lang)
    await callback.message.edit_text(
        new_t("settings_text"),
        reply_markup=set_kb(new_t)
    )


@router.callback_query(F.data == 'notifications_settings')
async def notifications_settings_callback(callback: CallbackQuery, t):
    tg_id = callback.from_user.id

    async with get_session() as session:
        user_repo, _ = await get_repositories(session)
        notifications_enabled = await user_repo.get_notifications(tg_id)

    status = t('notifications_enabled') if notifications_enabled else t('notifications_disabled')

    await safe_answer_callback(callback)
    await callback.message.edit_text(
        t('notifications_text', status=status),
        reply_markup=get_notifications_keyboard(t)
    )


@router.callback_query(F.data == 'toggle_notifications')
async def toggle_notifications_callback(callback: CallbackQuery, t):
    tg_id = callback.from_user.id

    async with get_session() as session:
        user_repo, _ = await get_repositories(session)
        new_state = await user_repo.toggle_notifications(tg_id)

    status = t('notifications_enabled') if new_state else t('notifications_disabled')

    await safe_answer_callback(callback, t('notifications_updated'), show_alert=True)
    await callback.message.edit_text(
        t('notifications_text', status=status),
        reply_markup=get_notifications_keyboard(t)
    )


# ===== END FILE: app/core/handlers/settings.py =====



# ===== START FILE: app/core/handlers/payments.py =====

from decimal import Decimal
from datetime import datetime

from aiogram import Router, F
from aiogram.filters.state import State, StatesGroup, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, ContentType, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.exc import OperationalError, TimeoutError as SQLTimeoutError

from app.core.keyboards import (
    balance_kb, get_payment_methods_keyboard, get_payment_amounts_keyboard,
    back_balance, payment_success_actions
)
from app.repo.db import get_session
from app.payments.manager import PaymentManager
from app.payments.models import PaymentMethod
from app.utils.logging import get_logger
from app.utils.redis import get_redis
from config import TELEGRAM_STARS_RATE, PLANS, bot, MIN_PAYMENT_AMOUNT, MAX_PAYMENT_AMOUNT
from .utils import safe_answer_callback, get_repositories, get_user_balance, format_expire_date

router = Router()
LOG = get_logger(__name__)


class PaymentState(StatesGroup):
    waiting_custom_amount = State()


@router.callback_query(F.data == 'balance')
async def balance_callback(callback: CallbackQuery, t, state: FSMContext):
    await safe_answer_callback(callback)
    await state.clear()
    tg_id = callback.from_user.id

    async with get_session() as session:
        user_repo, _ = await get_repositories(session)
        balance = await get_user_balance(user_repo, tg_id)
        has_active_sub = await user_repo.has_active_subscription(tg_id)
        sub_end = await user_repo.get_subscription_end(tg_id)

        text = t('balance_text', balance=balance)

        # Check if user had subscription before (even if expired)
        show_renew_button = sub_end is not None and not has_active_sub

        if has_active_sub:
            expire_date = format_expire_date(sub_end)
            text += f"\n\n{t('subscription_active_until', expire_date=expire_date)}"
        elif sub_end is not None:
            # Had subscription before but expired
            expire_date = format_expire_date(sub_end)
            text += f"\n\n{t('subscription_expired_on', expire_date=expire_date)}"
        else:
            cheapest = min(PLANS.values(), key=lambda x: x['price'])
            text += f"\n\n{t('subscription_from', price=cheapest['price'])}"

        await callback.message.edit_text(text, reply_markup=balance_kb(t, show_renew=show_renew_button))


@router.callback_query(F.data == 'add_funds')
async def add_funds_callback(callback: CallbackQuery, t):
    await safe_answer_callback(callback)
    await callback.message.edit_text(
        t('payment_method'),
        reply_markup=get_payment_methods_keyboard(t)
    )


@router.callback_query(F.data.startswith('select_method_'))
async def select_payment_method(callback: CallbackQuery, t):
    await safe_answer_callback(callback)
    method = callback.data.replace('select_method_', '')
    await callback.message.edit_text(
        t('select_amount'),
        reply_markup=get_payment_amounts_keyboard(t, method)
    )


@router.callback_query(F.data.startswith('amount_'))
async def process_amount_selection(callback: CallbackQuery, t, state: FSMContext):
    await safe_answer_callback(callback)
    parts = callback.data.split('_')
    method_str = parts[1]
    amount_str = parts[2]

    if amount_str == 'custom':
        await state.set_state(PaymentState.waiting_custom_amount)
        await state.set_data({'method': method_str})
        await callback.message.edit_text(t('enter_amount'), reply_markup=back_balance(t))
        return

    # Validate preset amount
    try:
        amount = Decimal(amount_str)
        if amount <= 0 or amount < MIN_PAYMENT_AMOUNT or amount > MAX_PAYMENT_AMOUNT:
            raise ValueError("Invalid preset amount")
    except (ValueError, TypeError) as e:
        LOG.error(f"Invalid preset amount: {amount_str} - {e}")
        await callback.message.edit_text(t('invalid_amount'), reply_markup=balance_kb(t))
        return

    await process_payment(callback, t, method_str, amount)


@router.message(StateFilter(PaymentState.waiting_custom_amount))
async def process_custom_amount(message: Message, state: FSMContext, t):
    tg_id = message.from_user.id

    try:
        amount = Decimal(message.text)
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount < MIN_PAYMENT_AMOUNT or amount > MAX_PAYMENT_AMOUNT:
            raise ValueError("Amount out of range")
        if amount.as_tuple().exponent < -2:
            raise ValueError("Too many decimal places")
    except (ValueError, TypeError) as e:
        LOG.error(f"Invalid amount from user {tg_id}: {message.text} - {e}")
        await message.answer(t('invalid_amount'))
        return

    data = await state.get_data()
    method_str = data.get('method')
    if not method_str:
        await message.answer(t('error_creating_payment'))
        await state.clear()
        return
    await state.clear()
    await process_payment(message, t, method_str, amount)

def _build_payment_keyboard(t, method: PaymentMethod, result):
    """Build inline keyboard for payment based on method type"""
    if method == PaymentMethod.TON:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t('payment_sent'), callback_data=f'payment_sent_{result.payment_id}')]
        ])
    elif method == PaymentMethod.STARS and result.url:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t('pay_button'), url=result.url)]
        ])
    elif method == PaymentMethod.CRYPTOBOT and result.pay_url:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t('pay_button'), url=result.pay_url)]
        ])
    elif method == PaymentMethod.YOOKASSA:
        if not getattr(result, 'pay_url', None):
            LOG.error(f"No pay_url for YooKassa payment {getattr(result, 'payment_id', '?')}")
            return None
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t('pay_button'), url=result.pay_url)],
            [InlineKeyboardButton(text=t('payment_sent'), callback_data=f'payment_sent_{result.payment_id}')]
        ])

    return None


def _build_payment_text(t, method: PaymentMethod, result):
    """Build payment instruction text based on method type"""
    if method == PaymentMethod.TON:
        return t(
            'ton_payment_instruction',
            ton_amount=f'<b>{result.expected_crypto_amount} TON</b>',
            wallet=f"<pre><code>{result.wallet}</code></pre>",
            comment=f'<pre>{result.comment}</pre>'
        )
    return result.text


async def _send_message(msg_or_callback, text, keyboard=None, parse_mode=None):
    """Send message handling both callbacks and regular messages"""
    is_callback = isinstance(msg_or_callback, CallbackQuery)
    if is_callback:
        if text != msg_or_callback.message.text or keyboard:
            await msg_or_callback.message.edit_text(text, reply_markup=keyboard, parse_mode=parse_mode)
        else:
            await msg_or_callback.message.reply(text, reply_markup=keyboard, parse_mode=parse_mode)


async def process_payment(msg_or_callback, t, method_str: str, amount: Decimal):
    tg_id = msg_or_callback.from_user.id
    is_callback = isinstance(msg_or_callback, CallbackQuery)

    try:
        method = PaymentMethod(method_str)
    except ValueError:
        LOG.error(f"Invalid method for user {tg_id}: {method_str}")
        await _send_message(msg_or_callback, t('error_creating_payment'), balance_kb(t))
        return

    async with get_session() as session:
        try:
            redis_client = await get_redis()
            manager = PaymentManager(session, redis_client)
            chat_id = msg_or_callback.message.chat.id if is_callback else msg_or_callback.chat.id
            result = await manager.create_payment(t, tg_id=tg_id, method=method, amount=amount, chat_id=chat_id)

            text = _build_payment_text(t, method, result)
            kb = _build_payment_keyboard(t, method, result)
            parse_mode = "HTML" if method == PaymentMethod.TON else None

            await _send_message(msg_or_callback, text, kb, parse_mode)

        except (ValueError, OperationalError, SQLTimeoutError) as e:
            LOG.error(f"Payment error for user {tg_id}: {type(e).__name__}: {e}")
            await _send_message(msg_or_callback, t('error_creating_payment'), balance_kb(t))

        except Exception as e:
            LOG.error(f"Payment error for user {tg_id}: {type(e).__name__}: {e}")
            await _send_message(msg_or_callback, t('error_creating_payment'), balance_kb(t))


@router.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    payload = pre_checkout_query.invoice_payload

    if not payload.startswith("topup_"):
        await bot.answer_pre_checkout_query(
            pre_checkout_query.id,
            ok=False,
            error_message="Invalid payment format"
        )
        return

    try:
        parts = payload.split("_")
        if len(parts) != 3:
            raise ValueError("Invalid payload structure")
        tg_id = int(parts[1])
        amount = int(parts[2])

        if tg_id != pre_checkout_query.from_user.id:
            LOG.warning(f"User {pre_checkout_query.from_user.id} tried to pay for user {tg_id}")
            await bot.answer_pre_checkout_query(
                pre_checkout_query.id,
                ok=False,
                error_message="Invalid payment recipient"
            )
            return

        if amount < MIN_PAYMENT_AMOUNT or amount > MAX_PAYMENT_AMOUNT:
            await bot.answer_pre_checkout_query(
                pre_checkout_query.id,
                ok=False,
                error_message="Invalid payment amount"
            )
            return

        await bot.answer_pre_checkout_query(
            pre_checkout_query.id,
            ok=True
        )

    except (ValueError, IndexError) as e:
        LOG.error(f"Pre-checkout validation failed for payload {payload}: {e}")
        await bot.answer_pre_checkout_query(
            pre_checkout_query.id,
            ok=False,
            error_message="Invalid payment data"
        )


@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message, t):
    tg_id = message.from_user.id

    if not message.successful_payment:
        LOG.error(f"Successful payment message without payment data for user {tg_id}")
        return

    payment_id = message.successful_payment.telegram_payment_charge_id
    stars_paid = message.successful_payment.total_amount

    if not payment_id or not stars_paid:
        LOG.error(f"Invalid payment data for user {tg_id}: payment_id={payment_id}, stars={stars_paid}")
        await message.answer(t('error_creating_payment'))
        return

    rub_amount = Decimal(stars_paid) * Decimal(str(TELEGRAM_STARS_RATE))

    async with get_session() as session:
        try:
            from app.repo.models import Payment as PaymentModel, User
            from sqlalchemy import select

            # CRITICAL FIX: Acquire database lock FIRST to prevent race conditions
            # Lock user row to serialize all payment confirmations for this user
            result = await session.execute(
                select(User).where(User.tg_id == tg_id).with_for_update()
            )
            user = result.scalar_one_or_none()
            if not user:
                LOG.error(f"User {tg_id} not found for Stars payment")
                await message.answer(t('user_not_found'))
                return

            # Find pending Stars payment with lock
            result = await session.execute(
                select(PaymentModel).where(
                    PaymentModel.tg_id == tg_id,
                    PaymentModel.method == 'stars',
                    PaymentModel.status == 'pending',
                    PaymentModel.amount == rub_amount
                ).with_for_update()
            )
            payment = result.scalar_one_or_none()

            if not payment:
                # Check if already confirmed with this tx_hash (duplicate webhook)
                result = await session.execute(
                    select(PaymentModel).where(
                        PaymentModel.tx_hash == payment_id,
                        PaymentModel.status == 'confirmed'
                    )
                )
                existing = result.scalar_one_or_none()
                if existing:
                    LOG.warning(f"Stars payment {payment_id} already confirmed (duplicate webhook)")
                    await message.answer(t('payment_already_processed'))
                    return

                LOG.error(f"No pending Stars payment found for user {tg_id} with amount {rub_amount}")
                await message.answer(t('payment_not_found'))
                return

            # Check if payment expired
            if payment.expires_at and datetime.utcnow() > payment.expires_at:
                LOG.warning(f"Stars payment {payment.id} expired (expires_at: {payment.expires_at})")
                payment.status = 'expired'
                await session.commit()
                await message.answer(t('payment_expired'))
                return

            # Check if tx_hash already used (should be caught by unique constraint, but double-check)
            if payment.tx_hash is not None:
                LOG.warning(f"Payment {payment.id} already has tx_hash: {payment.tx_hash}")
                await message.answer(t('payment_already_processed'))
                return

            # Store old balance for logging
            old_balance = user.balance

            # ATOMIC UPDATE: Update payment status and balance in single transaction
            payment.status = 'confirmed'
            payment.tx_hash = payment_id
            payment.confirmed_at = datetime.utcnow()

            # Credit payment amount
            user.balance += rub_amount
            new_balance = user.balance

            # Commit transaction atomically
            await session.commit()

            LOG.info(f"Stars payment confirmed: payment_id={payment.id}, user={tg_id}, "
                    f"amount={rub_amount}, balance: {old_balance} → {new_balance}, tx_hash={payment_id}")

            # Invalidate cache after successful commit (tolerate Redis failures)
            try:
                user_repo, _ = await get_repositories(session)
                redis = await user_repo.get_redis()
                await redis.delete(f"user:{tg_id}:balance")
            except Exception as redis_err:
                LOG.warning(f"Redis error invalidating cache for user {tg_id}: {redis_err}")
                # Don't fail payment confirmation - balance was updated successfully

            has_active_sub = await user_repo.has_active_subscription(tg_id)

            # Build success message
            success_text = t('payment_success', amount=float(rub_amount))

            await message.answer(
                success_text,
                reply_markup=payment_success_actions(t, has_active_sub)
            )

        except Exception as e:
            await session.rollback()
            LOG.error(f"Error confirming Stars payment for user {tg_id}: {type(e).__name__}: {e}")
            await message.answer(t('error_creating_payment'))
            raise


@router.callback_query(F.data.startswith('payment_sent_'))
async def payment_sent_callback(callback: CallbackQuery, t):
    """Handle 'Payment Sent' button - check payment immediately"""
    await safe_answer_callback(callback, t('payment_checking'), show_alert=True)

    tg_id = callback.from_user.id
    payment_id = int(callback.data.replace('payment_sent_', ''))

    async with get_session() as session:
        try:
            redis_client = await get_redis()
            manager = PaymentManager(session, redis_client)

            # Get payment details first
            _, payment_repo = await get_repositories(session)
            payment = await payment_repo.get_payment(payment_id)

            if not payment:
                raise ValueError(f"Payment {payment_id} not found")

            # Check payment immediately when user clicks button
            confirmed = await manager.check_payment(payment_id)

            # Get updated balance
            user_repo, _ = await get_repositories(session)
            balance = await get_user_balance(user_repo, tg_id)
            has_active_sub = await user_repo.has_active_subscription(tg_id)

            if confirmed:
                # Payment confirmed successfully
                text = t('payment_success', amount=float(payment['amount'])) + "\n\n" + t('balance_text', balance=balance)
            else:
                # Payment not yet confirmed
                text = t('payment_not_found') + "\n\n" + t('balance_text', balance=balance)

            if has_active_sub:
                from .utils import format_expire_date
                sub_end = await user_repo.get_subscription_end(tg_id)
                expire_date = format_expire_date(sub_end)
                text += f"\n\n{t('subscription_active_until', expire_date=expire_date)}"
            else:
                from config import PLANS
                cheapest = min(PLANS.values(), key=lambda x: x['price'])
                text += f"\n\n{t('subscription_from', price=cheapest['price'])}"

            await callback.message.edit_text(text, reply_markup=balance_kb(t))

        except Exception as e:
            LOG.error(f"Error checking payment {payment_id}: {e}")
            # Fallback to showing balance screen
            user_repo, _ = await get_repositories(session)
            balance = await get_user_balance(user_repo, tg_id)
            text = t('balance_text', balance=balance)
            await callback.message.edit_text(text, reply_markup=balance_kb(t))


# ===== END FILE: app/core/handlers/payments.py =====



# ===== START FILE: app/core/handlers/subscriptions.py =====

from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.core.keyboards import sub_kb, myvpn_kb
from app.repo.db import get_session
from app.utils.logging import get_logger
from config import PLANS
from .utils import safe_answer_callback, get_repositories, get_user_balance, format_expire_date

router = Router()
LOG = get_logger(__name__)


@router.callback_query(F.data == "buy_sub")
async def buy_sub_callback(callback: CallbackQuery, t):
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    async with get_session() as session:
        user_repo, _ = await get_repositories(session)
        balance = await get_user_balance(user_repo, tg_id)

        sub_text = t("buy_sub_text")
        if await user_repo.has_active_subscription(tg_id):
            sub_end = await user_repo.get_subscription_end(tg_id)
            expire_date = format_expire_date(sub_end, '%Y-%m-%d %H:%M')
            sub_text += f"\n\n{t('current_sub_until', expire_date=expire_date)}"

        await callback.message.edit_text(
            f"{sub_text}\n\n{t('balance')}: {balance:.2f} RUB",
            reply_markup=sub_kb(t)
        )


@router.callback_query(F.data.in_({"sub_1m", "sub_3m", "sub_6m", "sub_12m"}))
async def sub_buy_callback(callback: CallbackQuery, t):
    plan = PLANS[callback.data]
    days, price = plan["days"], plan["price"]
    tg_id = callback.from_user.id

    async with get_session() as session:
        user_repo, _ = await get_repositories(session)
        balance = await user_repo.get_balance(tg_id)

        if balance < price:
            await safe_answer_callback(callback, t('low_balance'), show_alert=True)
            return

        if not await user_repo.buy_subscription(tg_id, days, price):
            LOG.error(f"Failed to buy subscription for user {tg_id}: plan {callback.data}")
            await safe_answer_callback(callback, t('error_buying_sub'), show_alert=True)
            return

        configs = await user_repo.get_configs(tg_id)
        await safe_answer_callback(
            callback,
            t('sub_purchased_create_config') if not configs else t('sub_purchased'),
            show_alert=True
        )

        if configs:
            sub_end = await user_repo.get_subscription_end(tg_id)
            expire_date = format_expire_date(sub_end, '%Y-%m-%d %H:%M')
            await callback.message.edit_text(
                t('sub_success_with_expire', expire_date=expire_date),
                reply_markup=myvpn_kb(t, configs, True)
            )
        else:
            await callback.message.edit_text(
                t('create_first_config'),
                reply_markup=myvpn_kb(t, [], True)
            )


@router.callback_query(F.data == "renew_subscription")
async def renew_subscription_callback(callback: CallbackQuery, t):
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    async with get_session() as session:
        user_repo, _ = await get_repositories(session)
        balance = await get_user_balance(user_repo, tg_id)
        sub_end = await user_repo.get_subscription_end(tg_id)
        has_active_sub = await user_repo.has_active_subscription(tg_id)

        if sub_end and has_active_sub:
            # Active subscription - show expiry date
            expire_date = format_expire_date(sub_end)
            text = f"{t('current_sub_until', expire_date=expire_date)}\n\n{t('extend_subscription')}\n\n{t('balance')}: {balance:.2f} RUB"
        else:
            # Expired or no subscription - show renewal message
            text = f"{t('extend_subscription')}\n\n{t('balance')}: {balance:.2f} RUB"

        await callback.message.edit_text(
            text,
            reply_markup=sub_kb(t, is_extension=True)
        )


# ===== END FILE: app/core/handlers/subscriptions.py =====



# ===== START FILE: app/core/handlers/utils.py =====

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


# ===== END FILE: app/core/handlers/utils.py =====



# ===== START FILE: app/utils/redis.py =====

import os
import redis.asyncio as redis

redis_client: redis.Redis = None

async def init_cache():
    global redis_client
    if redis_client is None:
        try:
            url = os.getenv("REDIS_URL", "redis://localhost")
            redis_client = await redis.from_url(
                url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30,
                retry_on_timeout=True,
                max_connections=10
            )
            await redis_client.ping()
            print("Redis connected")
        except Exception as e:
            print(f"Redis init error: {e}")
            raise

async def get_redis() -> redis.Redis:
    if redis_client is None:
        raise RuntimeError("Redis not initialized. Call init_cache() first.")
    return redis_client

async def close_cache():
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        print("Redis closed")
        redis_client = None


# ===== END FILE: app/utils/redis.py =====



# ===== START FILE: app/utils/payment_notifications.py =====

"""
Payment notification utilities for sending payment confirmation messages to users.
"""
import logging
from decimal import Decimal
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from app.locales.locales import get_translator
from app.core.keyboards import payment_success_actions

LOG = logging.getLogger(__name__)


async def send_payment_notification(
    bot: Bot,
    tg_id: int,
    amount: Decimal,
    lang: str = "ru",
    has_active_subscription: bool = False
):
    """
    Send payment confirmation notification to user.

    Args:
        bot: Aiogram Bot instance
        tg_id: User Telegram ID
        amount: Total amount credited
        lang: User language (ru/en)
        has_active_subscription: Whether user has active subscription

    Returns:
        True if sent successfully, False otherwise
    """
    try:
        t = get_translator(lang)

        # Build success message
        success_text = t('payment_success', amount=float(amount))

        await bot.send_message(
            chat_id=tg_id,
            text=success_text,
            reply_markup=payment_success_actions(t, has_active_subscription)
        )

        LOG.info(f"Payment notification sent to user {tg_id}: {amount} RUB")
        return True

    except TelegramForbiddenError:
        LOG.warning(f"User {tg_id} blocked the bot, cannot send payment notification")
        return False
    except TelegramBadRequest as e:
        LOG.warning(f"Bad request sending payment notification to {tg_id}: {e}")
        return False
    except Exception as e:
        LOG.error(f"Error sending payment notification to {tg_id}: {type(e).__name__}: {e}")
        return False


# ===== END FILE: app/utils/payment_notifications.py =====



# ===== START FILE: app/utils/notifications.py =====

import asyncio
import logging
import random
from datetime import datetime, timedelta
from sqlalchemy import select
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from app.repo.db import get_session
from app.repo.models import User
from app.utils.redis import get_redis
from app.locales.locales import get_translator
from app.core.keyboards import balance_button_kb, get_renewal_notification_keyboard

LOG = logging.getLogger(__name__)


class SubscriptionNotificationTask:
    """
    Background task that checks for expiring subscriptions and sends notifications.

    Runs every 3 hours and sends:
    - 3-day warning when subscription expires in <= 3 days
    - 1-day warning when subscription expires in <= 1 day
    - Expired notification when subscription expired within last 24 hours

    Uses Redis to track sent notifications and avoid spam.
    All notifications include a Balance button to encourage renewal.
    """

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
        """
        Get random notification message variant with pricing info.

        Args:
            lang: User language ('ru' or 'en')
            days: Days until expiry (3, 1) or 'expired'
            user_balance: User's current balance for 1-day warning

        Returns:
            Random message text
        """
        from config import PLANS
        t = get_translator(lang)

        if days == 3:
            variants = [
                t('sub_expiry_3days_1'),
                t('sub_expiry_3days_2'),
                t('sub_expiry_3days_3'),
            ]
        elif days == 1:
            # Add pricing info for last day warning
            monthly_price = PLANS['sub_1m']['price']
            needed = max(0, monthly_price - user_balance)

            variants = [
                t('sub_expiry_1day_1'),
                t('sub_expiry_1day_2'),
                t('sub_expiry_1day_3'),
            ]

            message = random.choice(variants)

            # Add quick renewal info
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
        """
        Send subscription expiry notification to user.

        Args:
            tg_id: Telegram user ID
            lang: User language
            days: Days until expiry (3, 1) or 'expired'
            user_balance: User's current balance

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            message = self._get_random_message(lang, days, user_balance)
            if not message:
                return False

            t = get_translator(lang)
            # Use renewal keyboard with both "Renew" and "Balance" buttons
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
        """
        Check if user needs notification and send if needed.

        Args:
            user: User model instance
            redis: Redis client
        """
        # Skip if notifications disabled
        if not user.notifications:
            return

        # Skip if no subscription
        if not user.subscription_end:
            return

        now = datetime.utcnow()
        time_left = user.subscription_end - now
        days_left = time_left.total_seconds() / 86400

        # Format subscription end date for Redis key
        sub_end_date = user.subscription_end.strftime('%Y%m%d')

        # Determine notification type based on days left
        if -1 <= days_left <= 0:
            # Subscription expired within last 24 hours
            notification_type = 'expired'
            days = 'expired'
            ttl = 86400 * 7  # 7 days TTL
        elif 0 < days_left <= 1:
            # 1 day warning
            notification_type = '1d'
            days = 1
            ttl = 86400 * 2  # 2 days TTL
        elif 1 < days_left <= 3:
            # 3 day warning
            notification_type = '3d'
            days = 3
            ttl = 86400 * 4  # 4 days TTL
        else:
            # Too far in future or expired too long ago
            return

        # Check if already sent
        redis_key = f"notif:{notification_type}:{user.tg_id}:{sub_end_date}"

        try:
            already_sent = await redis.get(redis_key)
            if already_sent:
                return  # Already sent this notification
        except Exception as e:
            LOG.warning(f"Redis error checking notification for {user.tg_id}: {e}")
            return

        # Send notification with user balance (for pricing info in 1-day warning)
        success = await self._send_notification(user.tg_id, user.lang, days, float(user.balance))

        # Mark as sent if successful
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
                # Get all users with subscriptions expiring soon or recently expired
                now = datetime.utcnow()
                future_threshold = now + timedelta(days=3)  # Check up to 3 days in future
                past_threshold = now - timedelta(days=1)  # Check up to 1 day in past

                result = await session.execute(
                    select(User).where(
                        User.subscription_end.isnot(None),
                        User.subscription_end >= past_threshold,  # Include recently expired
                        User.subscription_end <= future_threshold  # Include soon to expire
                    )
                )
                users = result.scalars().all()

                LOG.info(f"Checking {len(users)} users for expiring/expired subscriptions")

                # Check each user
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

            # Wait for next check
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


# ===== END FILE: app/utils/notifications.py =====



# ===== START FILE: app/utils/payment_cleanup.py =====

import asyncio
import logging
from datetime import datetime
from app.repo.db import get_session
from app.repo.payments import PaymentRepository
from app.utils.redis import get_redis

LOG = logging.getLogger(__name__)


class PaymentCleanupTask:
    def __init__(self, check_interval_seconds: int = 3600 * 2, cleanup_days: int = 7):
        self.check_interval = check_interval_seconds
        self.cleanup_days = cleanup_days
        self.task: asyncio.Task = None
        self._running = False

    async def run_once(self):
        """Run a single cleanup cycle"""
        try:
            async with get_session() as session:
                redis_client = await get_redis()
                payment_repo = PaymentRepository(session, redis_client)

                # Mark expired pending payments
                expired_count = await payment_repo.expire_old_payments()
                if expired_count > 0:
                    LOG.info(f"Marked {expired_count} payments as expired")

                # Clean up old expired/cancelled payments
                deleted_count = await payment_repo.cleanup_old_payments(days=self.cleanup_days)
                if deleted_count > 0:
                    LOG.info(f"Cleaned up {deleted_count} old expired/cancelled payments")

        except Exception as e:
            LOG.error(f"Payment cleanup error: {type(e).__name__}: {e}")

    async def run_loop(self):
        """Continuously run cleanup checks"""
        self._running = True
        LOG.info(f"Payment cleanup task started (interval: {self.check_interval}s, cleanup after: {self.cleanup_days} days)")

        while self._running:
            try:
                await self.run_once()
            except Exception as e:
                LOG.error(f"Error in payment cleanup loop: {type(e).__name__}: {e}")

            # Wait for next check
            await asyncio.sleep(self.check_interval)

        LOG.info("Payment cleanup task stopped")

    def start(self):
        """Start the background cleanup task"""
        if self.task is None or self.task.done():
            self.task = asyncio.create_task(self.run_loop())
            LOG.info("Payment cleanup task created")
        else:
            LOG.warning("Payment cleanup task already running")

    def stop(self):
        """Stop the background cleanup task"""
        self._running = False
        if self.task and not self.task.done():
            self.task.cancel()
            LOG.info("Payment cleanup task cancelled")


# ===== END FILE: app/utils/payment_cleanup.py =====



# ===== START FILE: app/utils/rates.py =====

from decimal import Decimal
from datetime import datetime, timedelta
import aiohttp

_ton_price_cache = {"price": None, "timestamp": None}
_usdt_price_cache = {"price": None, "timestamp": None}
_PRICE_CACHE_TTL_SECONDS = 60

async def get_ton_price() -> Decimal:
    now = datetime.utcnow()

    if (_ton_price_cache["price"] and
        _ton_price_cache["timestamp"] and
        (now - _ton_price_cache["timestamp"]).total_seconds() < _PRICE_CACHE_TTL_SECONDS):
        return _ton_price_cache["price"]

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "the-open-network", "vs_currencies": "rub"},
            timeout=aiohttp.ClientTimeout(total=5)
        ) as resp:
            data = await resp.json()
            price = Decimal(str(data["the-open-network"]["rub"]))

            _ton_price_cache["price"] = price
            _ton_price_cache["timestamp"] = now

            return price


async def get_usdt_rub_rate() -> Decimal:
    """Get USDT to RUB exchange rate from CoinGecko API with caching"""
    now = datetime.utcnow()

    if (_usdt_price_cache["price"] and
        _usdt_price_cache["timestamp"] and
        (now - _usdt_price_cache["timestamp"]).total_seconds() < _PRICE_CACHE_TTL_SECONDS):
        return _usdt_price_cache["price"]

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "tether", "vs_currencies": "rub"},
            timeout=aiohttp.ClientTimeout(total=5)
        ) as resp:
            data = await resp.json()
            price = Decimal(str(data["tether"]["rub"]))

            _usdt_price_cache["price"] = price
            _usdt_price_cache["timestamp"] = now

            return price

# ===== END FILE: app/utils/rates.py =====



# ===== START FILE: app/utils/__init__.py =====



# ===== END FILE: app/utils/__init__.py =====



# ===== START FILE: app/utils/rate_limit.py =====

import asyncio
import time
from typing import Any, Callable, Dict, Tuple
from collections import OrderedDict
from aiogram import BaseMiddleware


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, default_limit: float = 1.5, custom_limits: Dict[str, float] | None = None, max_cache_size: int = 10000):
        super().__init__()
        self.default_limit = default_limit
        self.custom_limits = custom_limits or {}
        self.last_time: OrderedDict[Tuple[int, str], float] = OrderedDict()
        self.max_cache_size = max_cache_size  # Prevent unbounded memory growth
        self._lock = asyncio.Lock()

    def _get_key(self, event: Any) -> str:
        # Handle message commands
        text = getattr(event, "text", None)
        if isinstance(text, str) and text.startswith("/"):
            return text.split()[0]

        # Handle callback queries (for financial operations rate limiting)
        callback_data = getattr(event, "data", None)
        if callback_data:
            return callback_data

        return event.__class__.__name__

    async def __call__(self, handler: Callable, event: Any, data: dict):
        user = getattr(event, "from_user", None)
        user_id = getattr(user, "id", None)
        if user_id is None:
            return await handler(event, data)

        key = self._get_key(event)
        limit = self.custom_limits.get(key, self.default_limit)
        now = time.monotonic()
        lk = (user_id, key)

        async with self._lock:
            last = self.last_time.get(lk)
            if last is not None and (now - last) < limit:
                msg = None
                try:
                    t = data.get("t")
                    msg = t("too_fast") if t else "⏳ Too fast"
                except Exception:
                    msg = "⏳ Too fast"

                if hasattr(event, "answer") and "callback" in event.__class__.__name__.lower():
                    try:
                        await event.answer(msg, show_alert=False)
                    except Exception:
                        pass
                else:
                    try:
                        m = await event.answer(msg)
                        asyncio.create_task(self._safe_delete(m, delay=2))
                    except Exception:
                        pass
                return

            self.last_time[lk] = now

            # Enforce max cache size to prevent memory leak
            if len(self.last_time) > self.max_cache_size:
                # Remove oldest 10% of entries when limit exceeded
                remove_count = self.max_cache_size // 10
                for _ in range(remove_count):
                    self.last_time.popitem(last=False)

        return await handler(event, data)

    @staticmethod
    async def _safe_delete(message, delay: float = 2.0):
        await asyncio.sleep(delay)
        try:
            await message.delete()
        except Exception:
            pass


async def cleanup_rate_limit(middleware: RateLimitMiddleware, interval: int = 600, max_age: int = 1800):
    """
    Periodically clean up old rate limit entries to prevent memory growth.

    Args:
        middleware: The RateLimitMiddleware instance to clean
        interval: How often to run cleanup (default: 600s = 10 minutes)
        max_age: Remove entries older than this (default: 1800s = 30 minutes)
    """
    try:
        while True:
            await asyncio.sleep(interval)
            cutoff = time.monotonic() - max_age
            async with middleware._lock:
                old_keys = [k for k, t in middleware.last_time.items() if t < cutoff]
                for k in old_keys:
                    middleware.last_time.pop(k, None)
    except asyncio.CancelledError:
        pass

# ===== END FILE: app/utils/rate_limit.py =====



# ===== START FILE: app/utils/logging.py =====

import logging
from config import IS_LOGGING, LOG_LEVEL, LOG_AIOGRAM


def get_logger(name: str):
    logger = logging.getLogger(name)

    if not IS_LOGGING:
        logger.disabled = True
        return logger

    root_logger = logging.getLogger()
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
        root_logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

    return logger


def setup_aiogram_logger():
    aiolog = logging.getLogger("aiogram")

    if not LOG_AIOGRAM:
        aiolog.disabled = True
        return

    aiolog.handlers.clear()

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] AIROUTER %(levelname)s: %(message)s"
    )
    handler.setFormatter(formatter)

    aiolog.addHandler(handler)
    aiolog.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

# ===== END FILE: app/utils/logging.py =====



# ===== START FILE: app/utils/auto_renewal.py =====

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import select
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from app.repo.db import get_session
from app.repo.models import User
from app.repo.user import UserRepository
from app.utils.redis import get_redis
from app.locales.locales import get_translator
from config import PLANS

LOG = logging.getLogger(__name__)


class AutoRenewalTask:
    """
    Background task that automatically renews subscriptions when:
    - Subscription expires in <= 1 day
    - User has sufficient balance
    - Balance >= cheapest plan price (1 month)

    Runs every 6 hours to check for users needing auto-renewal.
    """

    def __init__(self, bot: Bot, check_interval_seconds: int = 3600 * 6):
        """
        Args:
            bot: Aiogram Bot instance for sending notifications
            check_interval_seconds: How often to check (default: 6 hours)
        """
        self.bot = bot
        self.check_interval = check_interval_seconds
        self.task: asyncio.Task = None
        self._running = False

    async def _attempt_auto_renewal(self, user: User, redis) -> bool:
        """
        Attempt to auto-renew user subscription with 1-month plan.

        Args:
            user: User model instance
            redis: Redis client

        Returns:
            True if renewed successfully, False otherwise
        """
        try:
            # Get 1-month plan (most affordable)
            monthly_plan = PLANS['sub_1m']
            price = Decimal(str(monthly_plan['price']))
            days = monthly_plan['days']

            # Check if user has sufficient balance
            if user.balance < price:
                LOG.debug(f"User {user.tg_id} has insufficient balance for auto-renewal: {user.balance} < {price}")
                return False

            # Renew subscription
            async with get_session() as session:
                user_repo = UserRepository(session, redis)

                success = await user_repo.buy_subscription(
                    tg_id=user.tg_id,
                    days=days,
                    price=float(price)
                )

                if success:
                    LOG.info(f"Auto-renewed subscription for user {user.tg_id}: {days} days for {price} RUB")

                    # Send notification
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

                        await self.bot.send_message(chat_id=user.tg_id, text=message)
                    except (TelegramForbiddenError, TelegramBadRequest) as e:
                        LOG.warning(f"Could not notify user {user.tg_id} about auto-renewal: {e}")

                    return True
                else:
                    LOG.warning(f"Failed to auto-renew subscription for user {user.tg_id}")
                    return False

        except Exception as e:
            LOG.error(f"Error during auto-renewal for user {user.tg_id}: {type(e).__name__}: {e}")
            return False

    async def run_once(self):
        """Run a single auto-renewal check cycle"""
        try:
            redis = await get_redis()

            async with get_session() as session:
                # Get users whose subscription expires in <= 1 day
                now = datetime.utcnow()
                threshold = now + timedelta(days=1)

                result = await session.execute(
                    select(User).where(
                        User.subscription_end.isnot(None),
                        User.subscription_end <= threshold,  # Expires soon
                        User.subscription_end >= now  # Not yet expired
                    )
                )
                users = result.scalars().all()

                LOG.info(f"Checking {len(users)} users for auto-renewal eligibility")

                renewal_count = 0
                for user in users:
                    # Skip if balance too low (< monthly plan price)
                    monthly_price = Decimal(str(PLANS['sub_1m']['price']))
                    if user.balance < monthly_price:
                        continue

                    # Check if already auto-renewed today
                    redis_key = f"auto_renewal:{user.tg_id}:{now.strftime('%Y%m%d')}"
                    already_processed = await redis.get(redis_key)
                    if already_processed:
                        continue

                    # Attempt auto-renewal
                    success = await self._attempt_auto_renewal(user, redis)
                    if success:
                        renewal_count += 1
                        # Mark as processed for today
                        await redis.setex(redis_key, 86400, "1")

                LOG.info(f"Auto-renewal check completed: {renewal_count} subscriptions renewed")

        except Exception as e:
            LOG.error(f"Auto-renewal check error: {type(e).__name__}: {e}")

    async def run_loop(self):
        """Continuously run auto-renewal checks"""
        self._running = True
        LOG.info(f"Auto-renewal task started (interval: {self.check_interval}s)")

        while self._running:
            try:
                await self.run_once()
            except Exception as e:
                LOG.error(f"Error in auto-renewal loop: {type(e).__name__}: {e}")

            # Wait for next check
            await asyncio.sleep(self.check_interval)

        LOG.info("Auto-renewal task stopped")

    def start(self):
        """Start the background auto-renewal task"""
        if self.task is None or self.task.done():
            self.task = asyncio.create_task(self.run_loop())
            LOG.info("Auto-renewal task created")
        else:
            LOG.warning("Auto-renewal task already running")

    def stop(self):
        """Stop the background auto-renewal task"""
        self._running = False
        if self.task and not self.task.done():
            self.task.cancel()
            LOG.info("Auto-renewal task cancelled")


# ===== END FILE: app/utils/auto_renewal.py =====



# ===== START FILE: app/utils/config_cleanup.py =====

import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy import select, update, func
from app.repo.db import get_session
from app.repo.models import User, Config
from app.repo.marzban_client import MarzbanClient
from app.utils.redis import get_redis

LOG = logging.getLogger(__name__)


async def cleanup_expired_configs(days_threshold: int = 14) -> dict:
    """
    Clean up configs for users with expired subscriptions (> days_threshold days).

    Process:
    1. Find all configs where subscription_end < (now - days_threshold)
    2. Delete config from Marzban
    3. Mark config as deleted in DB
    4. Decrement user's config count
    5. Invalidate Redis cache

    Args:
        days_threshold: Number of days after subscription expiry to keep configs (default: 14)

    Returns:
        dict with statistics: {
            'total_checked': int,
            'deleted': int,
            'failed': int,
            'skipped': int
        }
    """
    stats = {
        'total_checked': 0,
        'deleted': 0,
        'failed': 0,
        'skipped': 0
    }

    try:
        async with get_session() as session:
            redis = await get_redis()
            marzban_client = MarzbanClient()

            # Calculate threshold date
            now = datetime.utcnow()
            threshold_date = now - timedelta(days=days_threshold)

            LOG.info(f"Starting expired config cleanup (threshold: {days_threshold} days, cutoff: {threshold_date})")

            # Find all non-deleted configs for users with expired subscriptions
            result = await session.execute(
                select(Config, User.subscription_end)
                .join(User, Config.tg_id == User.tg_id)
                .where(
                    Config.deleted == False,
                    User.subscription_end.isnot(None),
                    User.subscription_end < threshold_date
                )
            )
            configs_to_delete = result.all()

            stats['total_checked'] = len(configs_to_delete)
            LOG.info(f"Found {stats['total_checked']} expired configs to clean up")

            for config, subscription_end in configs_to_delete:
                try:
                    tg_id = config.tg_id
                    username = config.username
                    config_id = config.id
                    instance_id = config.server_id

                    # Skip if no username (shouldn't happen, but defensive)
                    if not username:
                        LOG.warning(f"Config {config_id} has no username, skipping")
                        stats['skipped'] += 1
                        continue

                    LOG.info(f"Cleaning up config {config_id} (user: {tg_id}, username: {username}, expired: {subscription_end})")

                    # 1. Delete from Marzban
                    try:
                        await marzban_client.remove_user(username, instance_id)
                        LOG.info(f"Deleted Marzban user {username} from instance {instance_id}")
                    except Exception as e:
                        LOG.warning(f"Failed to delete Marzban user {username}: {e} (continuing with DB cleanup)")

                    # 2. Mark as deleted in DB
                    config.deleted = True

                    # 3. Decrement user's config count
                    await session.execute(
                        update(User)
                        .where(User.tg_id == tg_id)
                        .values(configs=func.greatest(User.configs - 1, 0))
                    )

                    await session.commit()

                    # 4. Invalidate Redis cache
                    try:
                        await redis.delete(f"user:{tg_id}:configs")
                    except Exception as e:
                        LOG.warning(f"Failed to invalidate cache for user {tg_id}: {e}")

                    stats['deleted'] += 1
                    LOG.info(f"Successfully cleaned up config {config_id}")

                except Exception as e:
                    LOG.error(f"Error cleaning up config {config.id}: {type(e).__name__}: {e}")
                    stats['failed'] += 1
                    await session.rollback()

            LOG.info(f"Config cleanup completed: {stats}")
            return stats

    except Exception as e:
        LOG.error(f"Fatal error in cleanup_expired_configs: {type(e).__name__}: {e}")
        stats['failed'] = stats['total_checked']
        return stats


class ConfigCleanupTask:
    """
    Background task that periodically cleans up expired configs.

    Runs once per week by default and removes configs for users
    whose subscriptions expired more than 14 days ago.
    """

    def __init__(self, check_interval_seconds: int = 86400 * 7, days_threshold: int = 14):
        """
        Args:
            check_interval_seconds: How often to run cleanup (default: 7 days)
            days_threshold: Days after expiry to keep configs (default: 14)
        """
        self.check_interval = check_interval_seconds
        self.days_threshold = days_threshold
        self.task: asyncio.Task = None
        self._running = False

    async def run_once(self):
        """Run a single cleanup cycle"""
        try:
            stats = await cleanup_expired_configs(self.days_threshold)
            LOG.info(f"Expired config cleanup stats: {stats}")
        except Exception as e:
            LOG.error(f"Config cleanup error: {type(e).__name__}: {e}")

    async def run_loop(self):
        """Continuously run cleanup checks"""
        self._running = True
        LOG.info(f"Config cleanup task started (interval: {self.check_interval}s, threshold: {self.days_threshold} days)")

        while self._running:
            try:
                await self.run_once()
            except Exception as e:
                LOG.error(f"Error in config cleanup loop: {type(e).__name__}: {e}")

            # Wait for next check
            await asyncio.sleep(self.check_interval)

        LOG.info("Config cleanup task stopped")

    def start(self):
        """Start the background cleanup task"""
        if self.task is None or self.task.done():
            self.task = asyncio.create_task(self.run_loop())
            LOG.info("Config cleanup task created")
        else:
            LOG.warning("Config cleanup task already running")

    def stop(self):
        """Stop the background cleanup task"""
        self._running = False
        if self.task and not self.task.done():
            self.task.cancel()
            LOG.info("Config cleanup task cancelled")


# ===== END FILE: app/utils/config_cleanup.py =====



# ===== START FILE: app/utils/updater.py =====

import asyncio
import logging
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from pytonapi import AsyncTonapi
from pytonapi.utils import to_amount, raw_to_userfriendly
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.repo.db import get_session
from app.payments.manager import PaymentManager
from app.payments.models import PaymentMethod
from app.repo.models import TonTransaction
from app.utils.redis import get_redis
from config import TON_ADDRESS, TONAPI_KEY, PAYMENT_TIMEOUT_MINUTES

LOG = logging.getLogger(__name__)

class TonTransactionsUpdater:
    def __init__(self, ton_address: str = TON_ADDRESS, api_key: str = TONAPI_KEY):
        self.ton_address = ton_address
        self.last_lt = 0
        self.tonapi = AsyncTonapi(api_key=api_key)

    async def fetch_new_transactions(self, limit: int = 50):
        try:
            result = await self.tonapi.blockchain.get_account_transactions(
                account_id=self.ton_address,
                limit=limit
            )
            txs = []
            now = datetime.utcnow()
            min_time = now - timedelta(minutes=PAYMENT_TIMEOUT_MINUTES * 2)

            for tx in result.transactions:
                lt = int(tx.lt)
                try:
                    created_at = datetime.utcfromtimestamp(int(tx.utime))
                except Exception:
                    LOG.debug("Skipping tx with invalid utime: %s", getattr(tx, "hash", "<no-hash>"))
                    continue

                if lt <= self.last_lt or created_at < min_time:
                    continue
                self.last_lt = max(self.last_lt, lt)
                txs.append(tx)
            return txs
        except Exception as e:
            LOG.error(f"[TonTransactionsUpdater] fetch error: {e}")
            return []

    async def insert_transactions(self, txs):
        if not txs:
            return

        async with get_session() as session:
            for tx in txs:
                try:
                    tx_hash = tx.hash
                    amount = Decimal(to_amount(getattr(tx.in_msg, "value", 0))).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    comment = (
                        tx.in_msg.decoded_body.get("text", "")
                        if getattr(tx.in_msg, "decoded_op_name", "") == "text_comment"
                        else ""
                    )
                    source = getattr(tx.in_msg, "source", None)
                    sender = (
                        raw_to_userfriendly(source.address.root)
                        if source and hasattr(source, "address") and hasattr(source.address, "root")
                        else None
                    )
                    created_at = datetime.utcfromtimestamp(int(tx.utime))

                    txn = TonTransaction(
                        tx_hash=tx_hash,
                        amount=amount,
                        comment=comment,
                        sender=sender,
                        created_at=created_at,
                        processed_at=None
                    )
                    session.add(txn)
                except Exception as e:
                    LOG.error(f"[TonTransactionsUpdater] insert error: {e}")
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
            except Exception as e:
                LOG.error(f"[TonTransactionsUpdater] commit error: {e}")
                await session.rollback()

    async def process_pending_payments(self):
        async with get_session() as session:
            redis_client = await get_redis()
            manager = PaymentManager(session, redis_client)
            pendings = await manager.get_pending_payments(PaymentMethod.TON)
            for payment in pendings:
                try:
                    await manager.check_payment(payment['id'])
                except Exception as e:
                    LOG.error(f"[TonTransactionsUpdater] check_payment error: {e}")

    async def run_once(self):
        txs = await self.fetch_new_transactions()
        await self.insert_transactions(txs)
        await self.process_pending_payments()
        async with get_session() as session:
            redis_client = await get_redis()
            manager = PaymentManager(session, redis_client)
            try:
                await manager.payment_repo.mark_failed_old_payments()
            except Exception as e:
                LOG.error(f"[TonTransactionsUpdater] mark_failed_old_payments error: {e}")

# ===== END FILE: app/utils/updater.py =====

