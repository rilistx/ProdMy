from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton

from core.utils.connector import connector  # noqa


def account_name_button(
        lang: str,
):
    keyboard = ReplyKeyboardBuilder()

    keyboard.add(KeyboardButton(
        text='Вихід',
    ))

    sizes = [1]

    return keyboard.adjust(*sizes).as_markup(resize_keyboard=True, one_time_keyboard=True)
