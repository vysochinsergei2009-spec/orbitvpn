from typing import Any

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def build_keyboard(
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