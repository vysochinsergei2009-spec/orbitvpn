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
