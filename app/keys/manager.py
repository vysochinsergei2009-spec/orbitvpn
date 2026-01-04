from enum import Enum
from typing import Callable
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ._enums import Pages, Actions, SelectAll
from ._callbacks import PageCB, SelectCB


class KeyboardManager:

    def home(self, servers: list = None, t: Callable[[str], str] = None) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        servers = servers or []

        for server in servers:
            emoji = getattr(server, 'emoji', '') or ''
            remark = getattr(server, 'remark', f'Server {server.id}')
            kb.button(
                text=f"{emoji}{remark}",
                callback_data=PageCB(
                    page=Pages.MENU, 
                    action=Actions.LIST, 
                    panel=server.id
                ).pack(),
            )

        kb.adjust(2)

        if t:
            kb.row(
                InlineKeyboardButton(
                    text=t('admin_panel'),
                    callback_data=PageCB(
                        page=Pages.ADMIN_PANEL, 
                        action=Actions.INFO
                    ).pack(),
                ),
                width=1,
            )

        return kb.as_markup()

    def menu(self, panel: int, t: Callable[[str], str]) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()

        items = {
            t('menu_users'): Pages.USERS,
            t('menu_actions'): Pages.ACTIONS,
            t('menu_stats'): Pages.STATS,
        }

        for text, page in items.items():
            kb.button(
                text=text,
                callback_data=PageCB(
                    page=page, 
                    action=Actions.LIST, 
                    panel=panel
                ).pack(),
            )

        kb.button(
            text=t('create_user'),
            callback_data=PageCB(
                page=Pages.USERS, 
                action=Actions.CREATE, 
                panel=panel
            ).pack(),
        )
        kb.button(
            text=t('search_user'),
            callback_data=PageCB(
                page=Pages.USERS, 
                action=Actions.SEARCH, 
                panel=panel
            ).pack(),
        )

        kb.adjust(2)

        kb.row(
            InlineKeyboardButton(
                text=t('server_info'),
                callback_data=PageCB(
                    page=Pages.SERVERS, 
                    action=Actions.INFO, 
                    panel=panel
                ).pack(),
            ),
            InlineKeyboardButton(
                text=t('back_home'),
                callback_data=PageCB(page=Pages.HOME).pack(),
            ),
            width=2,
        )

        return kb.as_markup()

    def admin_panel(self, t: Callable[[str], str]) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()

        kb.button(
            text=t('admin_stats'),
            callback_data=PageCB(
                page=Pages.ADMIN_STATS, 
                action=Actions.INFO
            ).pack(),
        )
        kb.button(
            text=t('admin_users'),
            callback_data=PageCB(
                page=Pages.ADMIN_USERS, 
                action=Actions.LIST
            ).pack(),
        )
        kb.button(
            text=t('admin_payments'),
            callback_data=PageCB(
                page=Pages.ADMIN_PAYMENTS, 
                action=Actions.LIST
            ).pack(),
        )
        kb.button(
            text=t('admin_servers'),
            callback_data=PageCB(
                page=Pages.ADMIN_SERVERS, 
                action=Actions.LIST
            ).pack(),
        )
        kb.button(
            text=t('admin_broadcast'),
            callback_data=PageCB(
                page=Pages.ADMIN_BROADCAST, 
                action=Actions.CREATE
            ).pack(),
        )
        kb.button(
            text=t('back_main'),
            callback_data=PageCB(page=Pages.HOME).pack(),
        )

        kb.adjust(2, 2, 1, 1)
        return kb.as_markup()

    def lister(
        self,
        items: list,
        page: Pages,
        panel: int | None = None,
        control: tuple[int, int] | None = None,
        filters: list[str] | None = None,
        select_filters: str | None = None,
        search: bool = False,
        server_back: int | None = None,
        user_back: int | None = None,
        t: Callable[[str], str] = None,
    ) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()

        for item in items:
            emoji = getattr(item, 'emoji', '') or ''
            remark = getattr(item, 'remark', getattr(item, 'username', str(item.id)))
            kb.button(
                text=f"{emoji}{remark}",
                callback_data=PageCB(
                    page=page,
                    action=Actions.INFO,
                    dataid=item.id,
                    panel=panel,
                    filters=select_filters,
                ).pack(),
            )

        kb.adjust(2)

        if filters and t:
            buttons = []
            for f in filters:
                buttons.append(
                    InlineKeyboardButton(
                        text=f,
                        callback_data=PageCB(
                            page=page,
                            action=Actions.LIST,
                            panel=panel,
                            filters=f,
                        ).pack(),
                    )
                )
            if buttons:
                kb.row(*buttons, width=len(filters))

        if control:
            left, right = control
            buttons = []
            if left != 0 and t:
                buttons.append(
                    InlineKeyboardButton(
                        text=t('left'),
                        callback_data=PageCB(
                            page=page,
                            action=Actions.LIST,
                            pagenumber=left,
                            panel=panel,
                            filters=select_filters,
                        ).pack(),
                    )
                )
            if right != 0 and t:
                buttons.append(
                    InlineKeyboardButton(
                        text=t('right'),
                        callback_data=PageCB(
                            page=page,
                            action=Actions.LIST,
                            pagenumber=right,
                            panel=panel,
                            filters=select_filters,
                        ).pack(),
                    )
                )
            if buttons:
                kb.row(*buttons, width=2)

        if search and t:
            kb.row(
                InlineKeyboardButton(
                    text=t('search_user'),
                    callback_data=PageCB(
                        page=Pages.USERS, 
                        action=Actions.SEARCH, 
                        panel=panel
                    ).pack(),
                ),
                width=1,
            )

        if t:
            kb.row(
                InlineKeyboardButton(
                    text=t('create'),
                    callback_data=PageCB(
                        page=page, 
                        action=Actions.CREATE, 
                        panel=panel
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text=t('back_home'),
                    callback_data=PageCB(page=Pages.HOME).pack(),
                ),
                width=2,
            )

            if server_back and not user_back:
                kb.row(
                    InlineKeyboardButton(
                        text=t('back'),
                        callback_data=PageCB(
                            page=Pages.MENU, 
                            action=Actions.LIST, 
                            panel=server_back
                        ).pack(),
                    ),
                    width=1,
                )
            elif server_back and user_back:
                kb.row(
                    InlineKeyboardButton(
                        text=t('back'),
                        callback_data=PageCB(
                            page=Pages.USERS,
                            action=Actions.INFO,
                            dataid=user_back,
                            panel=server_back,
                        ).pack(),
                    ),
                    width=1,
                )

        return kb.as_markup()

    def selector(
        self,
        data: list[str | tuple[str, str] | Enum],
        types: Pages,
        action: Actions | None = None,
        selects: list[str] | None = None,
        width: int = 2,
        panel: int | None = None,
        extra: str | None = None,
        all_selects: bool = False,
        user_back: int | None = None,
        server_back: int | None = None,
        t: Callable[[str], str] = None,
    ) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()

        for d in data:
            text = d.value if isinstance(d, Enum) else d
            if isinstance(d, tuple):
                display_name, value = d
            else:
                display_name = value = d.value if isinstance(d, Enum) else d
            
            selected = False
            if selects is not None:
                selected = value in selects
                display_name = f"✅ {text}" if selected else f"❌ {text}"

            kb.button(
                text=display_name,
                callback_data=SelectCB(
                    select=value,
                    types=types,
                    action=action,
                    selected=selected,
                    panel=panel,
                    extra=extra,
                ).pack(),
            )

        kb.adjust(width)

        if all_selects and selects is not None and t:
            select_buttons = []
            if len(selects) != len(data) and len(selects) > 0:
                select_buttons.extend([
                    InlineKeyboardButton(
                        text=t('select_all'),
                        callback_data=SelectCB(
                            types=types,
                            action=action,
                            panel=panel,
                            extra=extra,
                            select=SelectAll.SELECT,
                        ).pack(),
                    ),
                    InlineKeyboardButton(
                        text=t('deselect_all'),
                        callback_data=SelectCB(
                            types=types,
                            action=action,
                            panel=panel,
                            extra=extra,
                            select=SelectAll.DESELECT,
                        ).pack(),
                    ),
                ])
            elif len(selects) == len(data):
                select_buttons.append(
                    InlineKeyboardButton(
                        text=t('deselect_all'),
                        callback_data=SelectCB(
                            types=types,
                            action=action,
                            panel=panel,
                            extra=extra,
                            select=SelectAll.DESELECT,
                        ).pack(),
                    )
                )
            elif len(selects) == 0:
                select_buttons.append(
                    InlineKeyboardButton(
                        text=t('select_all'),
                        callback_data=SelectCB(
                            types=types,
                            action=action,
                            panel=panel,
                            extra=extra,
                            select=SelectAll.SELECT,
                        ).pack(),
                    )
                )
            
            if select_buttons:
                kb.row(*select_buttons, width=len(select_buttons))

        if t:
            if selects is not None:
                kb.row(
                    InlineKeyboardButton(
                        text=t('done'),
                        callback_data=SelectCB(
                            types=types,
                            action=action,
                            done=True,
                            panel=panel,
                            extra=extra,
                        ).pack(),
                    ),
                    InlineKeyboardButton(
                        text=t('back_home'),
                        callback_data=PageCB(page=Pages.HOME).pack(),
                    ),
                    width=2,
                )
            else:
                kb.row(
                    InlineKeyboardButton(
                        text=t('back_home'),
                        callback_data=PageCB(page=Pages.HOME).pack(),
                    ),
                    width=1,
                )

            if server_back and not user_back:
                kb.row(
                    InlineKeyboardButton(
                        text=t('back'),
                        callback_data=PageCB(
                            page=Pages.MENU, 
                            action=Actions.LIST, 
                            panel=server_back
                        ).pack(),
                    ),
                    width=1,
                )
            elif server_back and user_back:
                kb.row(
                    InlineKeyboardButton(
                        text=t('back'),
                        callback_data=PageCB(
                            page=Pages.USERS,
                            action=Actions.INFO,
                            dataid=user_back,
                            panel=server_back,
                        ).pack(),
                    ),
                    width=1,
                )

        return kb.as_markup()

    def cancel(
        self,
        server_back: int | None = None,
        user_back: int | None = None,
        t: Callable[[str], str] = None,
    ) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()

        if t:
            kb.button(
                text=t('back_home'),
                callback_data=PageCB(page=Pages.HOME).pack()
            )

            if server_back and not user_back:
                kb.row(
                    InlineKeyboardButton(
                        text=t('back'),
                        callback_data=PageCB(
                            page=Pages.MENU, 
                            action=Actions.LIST, 
                            panel=server_back
                        ).pack(),
                    ),
                    width=1,
                )
            elif server_back and user_back:
                kb.row(
                    InlineKeyboardButton(
                        text=t('back'),
                        callback_data=PageCB(
                            page=Pages.USERS,
                            action=Actions.INFO,
                            dataid=user_back,
                            panel=server_back,
                        ).pack(),
                    ),
                    width=1,
                )

        return kb.as_markup()
