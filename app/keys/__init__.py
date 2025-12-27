"""Keyboard management system"""

from ._callbacks import PageCB, SelectCB
from ._enums import Pages, Actions, YesOrNot, SelectAll, JsonHandler, RandomHandler
from .manager import KeyboardManager
from .admin import (
    admin_panel_kb,
    admin_servers_kb,
    admin_clear_configs_confirm_kb,
    broadcast_cancel_kb,
    broadcast_settings_kb,
    broadcast_confirm_kb,
    admin_users_kb,
    admin_user_detail_kb,
    admin_user_list_kb,
    admin_payments_kb,
    admin_instance_detail_kb,
)

# Initialize keyboard manager
BotKeys = KeyboardManager()

__all__ = [
    "BotKeys",
    "Pages",
    "Actions",
    "PageCB",
    "SelectCB",
    "YesOrNot",
    "SelectAll",
    "JsonHandler",
    "RandomHandler",
    # Admin keyboards
    "admin_panel_kb",
    "admin_servers_kb",
    "admin_clear_configs_confirm_kb",
    "broadcast_cancel_kb",
    "broadcast_settings_kb",
    "broadcast_confirm_kb",
    "admin_users_kb",
    "admin_user_detail_kb",
    "admin_user_list_kb",
    "admin_payments_kb",
    "admin_instance_detail_kb",
]
