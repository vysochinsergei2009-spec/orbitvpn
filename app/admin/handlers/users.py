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
