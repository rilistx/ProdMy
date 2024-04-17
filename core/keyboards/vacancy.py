from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton

from core.utils.connector import connector


class VacancyCallBack(CallbackData, prefix="vacancy"):
    lang: str | None = None
    key: str | None = None
    method: str | None = None


def vacancy_profession_button(lang: str, data_name: str, data_list: list, change=None, catalog_title=None):
    keyboard = ReplyKeyboardBuilder()

    if change:
        keyboard.add(KeyboardButton(text='Не менять!'))

    for item in data_list:
        if data_name == 'catalog':
            keyboard.add(KeyboardButton(
                text=connector[lang][data_name][item.title]['logo'] + ' ' + connector[lang][data_name][item.title]['name']
            ))
        else:
            keyboard.add(KeyboardButton(
                text=connector[lang]['catalog'][catalog_title][data_name][item.title]
            ))

    if data_name == 'subcatalog':
        keyboard.add(KeyboardButton(text=connector[lang]['button']['back']))

    keyboard.add(KeyboardButton(text=connector[lang]['button']['exit']))

    sizes = ([1] if change else []) + [2 for _ in range(len(data_list) // 2)] + ([1] if len(data_list) % 2 else []) + ([2] if data_name == 'subcatalog' else [1])

    return keyboard.adjust(*sizes).as_markup(resize_keyboard=True, one_time_keyboard=True)


def vacancy_keyboard_button(lang: str, change=None):
    keyboard = ReplyKeyboardBuilder()

    if change:
        keyboard.add(KeyboardButton(text='Не менять!'))

    keyboard.add(KeyboardButton(text=connector[lang]['button']['back']))
    keyboard.add(KeyboardButton(text=connector[lang]['button']['exit']))

    sizes = ([1] if change else []) + [2]

    return keyboard.adjust(*sizes).as_markup(resize_keyboard=True, one_time_keyboard=True)


def vacancy_choice_button(lang: str, change=None):
    keyboard = ReplyKeyboardBuilder()

    if change:
        keyboard.add(KeyboardButton(text='Не менять!'))

    keyboard.add(KeyboardButton(text='✅ ' + connector[lang]['button']['yes']))
    keyboard.add(KeyboardButton(text='❎ ' + connector[lang]['button']['not']))

    keyboard.add(KeyboardButton(text=connector[lang]['button']['back']))
    keyboard.add(KeyboardButton(text=connector[lang]['button']['exit']))

    sizes = ([1] if change else []) + [2, 2]

    return keyboard.adjust(*sizes).as_markup(resize_keyboard=True, one_time_keyboard=True)


def vacancy_location_button(lang: str, country_name: str, data_name: str, data_list: list, change=None, region_name=None):
    keyboard = ReplyKeyboardBuilder()

    if change:
        keyboard.add(KeyboardButton(text='Не менять!'))

    for item in data_list:
        if data_name == 'region':
            keyboard.add(KeyboardButton(text=connector[lang]['country'][country_name][data_name][item.name]['name']))
        else:
            keyboard.add(
                KeyboardButton(text=connector[lang]['country'][country_name]['region'][region_name][data_name][item.name])
            )

    if data_name == 'city':
        keyboard.add(KeyboardButton(text=connector[lang]['button']['skip']))

    keyboard.add(KeyboardButton(text=connector[lang]['button']['back']))
    keyboard.add(KeyboardButton(text=connector[lang]['button']['exit']))

    sizes = ([1] if change else []) + [2 for _ in range(len(data_list) // 2)] + ([1] if len(data_list) % 2 else []) + ([1] if data_name == 'city' else []) + [2]

    return keyboard.adjust(*sizes).as_markup(resize_keyboard=True, one_time_keyboard=True)
