from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton

from core.utils.connector import connector


def get_contact_button(lang, sizes: tuple[int] = (2,)):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
        KeyboardButton(
            text=connector[lang]['button']['registration']['contact'],
            request_contact=True
        )
    )

    return keyboard.adjust(*sizes).as_markup(resize_keyboard=True, one_time_keyboard=True)
