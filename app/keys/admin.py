"""Admin panel keyboards - now using panel system"""

from typing import Callable
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ._enums import Pages, Actions
from ._callbacks import PageCB


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
    """Admin panel keyboard with panel-based navigation"""
    return _build_keyboard([
        {
            'text': t('admin_stats'),
            'callback_data': PageCB(page=Pages.ADMIN_STATS, action=Actions.INFO).pack()
        },
        {
            'text': t('admin_users'),
            'callback_data': PageCB(page=Pages.ADMIN_USERS, action=Actions.LIST).pack()
        },
        {
            'text': t('admin_payments'),
            'callback_data': PageCB(page=Pages.ADMIN_PAYMENTS, action=Actions.LIST).pack()
        },
        {
            'text': t('admin_servers'),
            'callback_data': PageCB(page=Pages.ADMIN_SERVERS, action=Actions.LIST).pack()
        },
        {
            'text': t('admin_broadcast'),
            'callback_data': PageCB(page=Pages.ADMIN_BROADCAST, action=Actions.CREATE).pack()
        },
        {
            'text': t('back_main'),
            'callback_data': PageCB(page=Pages.HOME).pack()
        },
    ], adjust=[2, 2, 1, 1])


def admin_servers_kb(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    """Server management keyboard"""
    return _build_keyboard([
        {
            'text': t('admin_clear_configs'),
            'callback_data': PageCB(
                page=Pages.ADMIN_SERVERS, 
                action=Actions.DELETE,
                datatype='configs'
            ).pack()
        },
        {
            'text': t('back'),
            'callback_data': PageCB(page=Pages.ADMIN_PANEL, action=Actions.INFO).pack()
        },
    ])


def admin_clear_configs_confirm_kb(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    """Confirmation keyboard for config cleanup"""
    return _build_keyboard([
        {
            'text': t('confirm_yes'),
            'callback_data': PageCB(
                page=Pages.ADMIN_SERVERS, 
                action=Actions.EXECUTE,
                datatype='clear_configs'
            ).pack()
        },
        {
            'text': t('confirm_no'),
            'callback_data': PageCB(page=Pages.ADMIN_SERVERS, action=Actions.LIST).pack()
        },
    ])


def broadcast_cancel_kb(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    """Cancel broadcast keyboard"""
    return _build_keyboard([
        {
            'text': t('cancel'),
            'callback_data': PageCB(
                page=Pages.ADMIN_BROADCAST, 
                action=Actions.CANCEL
            ).pack()
        },
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
        {
            'text': f"{all_marker}{t('broadcast_target_all')}",
            'callback_data': PageCB(
                page=Pages.ADMIN_BROADCAST,
                action=Actions.MODIFY,
                datatype='target_all'
            ).pack()
        },
        {
            'text': f"{subscribed_marker}{t('broadcast_target_subscribed')}",
            'callback_data': PageCB(
                page=Pages.ADMIN_BROADCAST,
                action=Actions.MODIFY,
                datatype='target_subscribed'
            ).pack()
        },
    ])

    # Time selection
    now_marker = '✓ ' if selected_time == 'now' else ''
    buttons.append({
        'text': f"{now_marker}{t('broadcast_time_now')}",
        'callback_data': PageCB(
            page=Pages.ADMIN_BROADCAST,
            action=Actions.MODIFY,
            datatype='time_now'
        ).pack()
    })

    # Action buttons
    buttons.extend([
        {
            'text': t('broadcast_send'),
            'callback_data': PageCB(
                page=Pages.ADMIN_BROADCAST,
                action=Actions.INFO,
                datatype='confirm'
            ).pack()
        },
        {
            'text': t('cancel'),
            'callback_data': PageCB(
                page=Pages.ADMIN_BROADCAST,
                action=Actions.CANCEL
            ).pack()
        },
    ])

    return _build_keyboard(buttons, adjust=[2, 1, 1, 1])


def broadcast_confirm_kb(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    """Final confirmation keyboard for broadcast"""
    return _build_keyboard([
        {
            'text': t('broadcast_execute'),
            'callback_data': PageCB(
                page=Pages.ADMIN_BROADCAST,
                action=Actions.EXECUTE
            ).pack()
        },
        {
            'text': t('cancel'),
            'callback_data': PageCB(
                page=Pages.ADMIN_BROADCAST,
                action=Actions.CANCEL
            ).pack()
        },
    ], adjust=[1, 1])


def admin_users_kb(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    """User management keyboard"""
    return _build_keyboard([
        {
            'text': t('admin_search_user'),
            'callback_data': PageCB(
                page=Pages.ADMIN_USERS,
                action=Actions.SEARCH
            ).pack()
        },
        {
            'text': t('admin_user_list'),
            'callback_data': PageCB(
                page=Pages.ADMIN_USERS,
                action=Actions.LIST
            ).pack()
        },
        {
            'text': t('back'),
            'callback_data': PageCB(page=Pages.ADMIN_PANEL, action=Actions.INFO).pack()
        },
    ], adjust=[2, 1])


def admin_user_detail_kb(t: Callable[[str], str], user_id: int) -> InlineKeyboardMarkup:
    """User detail management keyboard"""
    return _build_keyboard([
        {
            'text': t('admin_grant_sub'),
            'callback_data': PageCB(
                page=Pages.ADMIN_USERS,
                action=Actions.MODIFY,
                dataid=user_id,
                datatype='grant_sub'
            ).pack()
        },
        {
            'text': t('admin_revoke_sub'),
            'callback_data': PageCB(
                page=Pages.ADMIN_USERS,
                action=Actions.MODIFY,
                dataid=user_id,
                datatype='revoke_sub'
            ).pack()
        },
        {
            'text': t('admin_add_balance'),
            'callback_data': PageCB(
                page=Pages.ADMIN_USERS,
                action=Actions.MODIFY,
                dataid=user_id,
                datatype='add_balance'
            ).pack()
        },
        {
            'text': t('admin_view_configs'),
            'callback_data': PageCB(
                page=Pages.ADMIN_USERS,
                action=Actions.INFO,
                dataid=user_id,
                datatype='configs'
            ).pack()
        },
        {
            'text': t('admin_search_user'),
            'callback_data': PageCB(
                page=Pages.ADMIN_USERS,
                action=Actions.SEARCH
            ).pack()
        },
        {
            'text': t('back'),
            'callback_data': PageCB(page=Pages.ADMIN_USERS, action=Actions.LIST).pack()
        },
    ], adjust=[2, 2, 1, 1])


def admin_user_list_kb(t: Callable[[str], str], page: int, total_pages: int) -> InlineKeyboardMarkup:
    """User list pagination keyboard"""
    buttons = []

    # Navigation buttons
    if page > 0:
        buttons.append({
            'text': t('admin_prev_page'),
            'callback_data': PageCB(
                page=Pages.ADMIN_USERS,
                action=Actions.LIST,
                pagenumber=page-1
            ).pack()
        })
    if page < total_pages - 1:
        buttons.append({
            'text': t('admin_next_page'),
            'callback_data': PageCB(
                page=Pages.ADMIN_USERS,
                action=Actions.LIST,
                pagenumber=page+1
            ).pack()
        })

    # Add back button
    buttons.append({
        'text': t('back'),
        'callback_data': PageCB(page=Pages.ADMIN_USERS, action=Actions.INFO).pack()
    })

    # Adjust layout: navigation buttons in one row, back button in another
    if len(buttons) == 3:
        return _build_keyboard(buttons, adjust=[2, 1])
    else:
        return _build_keyboard(buttons, adjust=[1, 1])


def admin_payments_kb(t: Callable[[str], str]) -> InlineKeyboardMarkup:
    """Payments statistics keyboard"""
    return _build_keyboard([
        {
            'text': t('admin_recent_payments'),
            'callback_data': PageCB(
                page=Pages.ADMIN_PAYMENTS,
                action=Actions.LIST,
                datatype='recent'
            ).pack()
        },
        {
            'text': t('back'),
            'callback_data': PageCB(page=Pages.ADMIN_PANEL, action=Actions.INFO).pack()
        },
    ])


def admin_instance_detail_kb(t: Callable[[str], str], instance_id: str) -> InlineKeyboardMarkup:
    """Instance detail keyboard"""
    return _build_keyboard([
        {
            'text': t('admin_view_nodes'),
            'callback_data': PageCB(
                page=Pages.ADMIN_SERVERS,
                action=Actions.INFO,
                dataid=instance_id,
                datatype='nodes'
            ).pack()
        },
        {
            'text': t('back'),
            'callback_data': PageCB(page=Pages.ADMIN_SERVERS, action=Actions.LIST).pack()
        },
    ])
