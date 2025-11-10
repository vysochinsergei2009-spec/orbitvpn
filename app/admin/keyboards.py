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
