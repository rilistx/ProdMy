from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton

from core.commands.languages import json


def get_language_button(*, lang: list, sizes: tuple[int] = (2,)):
    keyboard = ReplyKeyboardBuilder()

    for item in lang:
        keyboard.add(KeyboardButton(text=item))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_contact_button(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=json[lang]['button']['contact'], request_contact=True))

    return keyboard.adjust(1).as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        # input_field_placeholder='Введи свой номер телефона!',
    )
