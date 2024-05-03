from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton

from core.utils.connector import connector


def account_name_button(
        lang: str,
):
    keyboard = ReplyKeyboardBuilder()

    keyboard.add(
        KeyboardButton(
            text=f"↪️ {connector[lang]['button']['navigation']['cancel']}",
        )
    )

    sizes = [1]

    return keyboard.adjust(*sizes).as_markup(resize_keyboard=True, one_time_keyboard=True)
