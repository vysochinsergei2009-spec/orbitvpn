"""Callback data factories for panel navigation"""

from enum import Enum
from aiogram.filters.callback_data import CallbackData

from ._enums import Pages, Actions


class PageCB(CallbackData, prefix="pages"):
    """Callback data for page navigation
    
    Args:
        page: Page type (from Pages enum)
        action: Action type (from Actions enum)
        dataid: Optional ID of data object (user_id, server_id, etc)
        datatype: Optional type specification
        panel: Optional panel/server ID for context
        pagenumber: Optional page number for pagination
        filters: Optional filter string
    """
    page: Pages = Pages.HOME
    action: Actions = Actions.LIST
    dataid: int | str | None = None
    datatype: str | Enum | None = None
    panel: int | None = None
    pagenumber: int | None = None
    filters: str | None = None


class SelectCB(CallbackData, prefix="select"):
    """Callback data for selection interfaces
    
    Args:
        select: Selected item identifier
        types: Page type context
        action: Action being performed
        selected: Whether item is selected
        done: Whether selection is complete
        panel: Optional panel/server ID
        extra: Extra data string
    """
    select: str | int | Enum | None = None
    types: Pages
    action: Actions | None = None
    selected: bool | None = None
    done: bool = False
    panel: int | None = None
    extra: str | None = None
