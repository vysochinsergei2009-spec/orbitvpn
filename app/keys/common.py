from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def kb(
    buttons: list[tuple[str, str]],
    row: int = 2,
):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=text, callback_data=data)
                for text, data in buttons[i:i + row]
            ]
            for i in range(0, len(buttons), row)
        ]
    )


def back_kb(t, data: str = "back"):
    return kb([(t("back"), data)], row=1)


def cancel_kb(t, data: str = "cancel"):
    return kb([(t("cancel"), data)], row=1)
