"""Admin broadcast handlers"""

import asyncio
from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.keys import (
    admin_panel_kb,
    broadcast_settings_kb,
    broadcast_confirm_kb,
    broadcast_cancel_kb,
    Pages,
    Actions,
    PageCB
)
from app.db.db import get_session
from app.db.user import UserRepository
from app.utils.logging import get_logger
from app.routers.utils import safe_answer_callback
from config import ADMIN_TG_IDS

router = Router()
LOG = get_logger(__name__)


class BroadcastState(StatesGroup):
    """FSM states for broadcast functionality"""
    waiting_message = State()
    confirming = State()


@router.callback_query(PageCB.filter((F.page == Pages.ADMIN_BROADCAST) & (F.action == Actions.CREATE)))
async def admin_broadcast(callback: CallbackQuery, callback_data: PageCB, t, state: FSMContext):
    """Start broadcast - request message"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id not in ADMIN_TG_IDS:
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

    if tg_id not in ADMIN_TG_IDS:
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


@router.callback_query(PageCB.filter((F.page == Pages.ADMIN_BROADCAST) & (F.action == Actions.MODIFY)))
async def set_broadcast_options(callback: CallbackQuery, callback_data: PageCB, t, state: FSMContext):
    """Set broadcast target or time"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id not in ADMIN_TG_IDS:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    datatype = callback_data.datatype
    
    # Handle target selection
    if datatype and datatype.startswith('target_'):
        target = datatype.split('_')[1]  # 'all' or 'subscribed'
        await state.update_data(target=target)
        data = await state.get_data()
        current_time = data.get('schedule_time', 'now')
        
        await callback.message.edit_text(
            t('broadcast_settings_prompt'),
            reply_markup=broadcast_settings_kb(t, selected_target=target, selected_time=current_time)
        )
    
    # Handle time selection
    elif datatype and datatype.startswith('time_'):
        schedule_time = datatype.split('_')[1]  # 'now'
        await state.update_data(schedule_time=schedule_time)
        data = await state.get_data()
        current_target = data.get('target', 'all')
        
        await callback.message.edit_text(
            t('broadcast_settings_prompt'),
            reply_markup=broadcast_settings_kb(t, selected_target=current_target, selected_time=schedule_time)
        )


@router.callback_query(PageCB.filter((F.page == Pages.ADMIN_BROADCAST) & (F.action == Actions.INFO) & (F.datatype == 'confirm')))
async def confirm_broadcast(callback: CallbackQuery, callback_data: PageCB, t, state: FSMContext):
    """Show confirmation before executing broadcast"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id not in ADMIN_TG_IDS:
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


@router.callback_query(PageCB.filter((F.page == Pages.ADMIN_BROADCAST) & (F.action == Actions.EXECUTE)))
async def execute_broadcast(callback: CallbackQuery, callback_data: PageCB, t, state: FSMContext):
    """Execute the broadcast"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id not in ADMIN_TG_IDS:
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


@router.callback_query(PageCB.filter((F.page == Pages.ADMIN_BROADCAST) & (F.action == Actions.CANCEL)))
async def cancel_broadcast(callback: CallbackQuery, callback_data: PageCB, t, state: FSMContext):
    """Cancel broadcast"""
    await safe_answer_callback(callback)
    tg_id = callback.from_user.id

    if tg_id not in ADMIN_TG_IDS:
        await callback.answer(t('access_denied'), show_alert=True)
        return

    await state.clear()

    await callback.message.edit_text(
        t('broadcast_cancelled'),
        reply_markup=admin_panel_kb(t)
    )
