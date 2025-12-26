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
