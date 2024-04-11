from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton

from core.utils.connector import connector


def vacancy_profession_button(lang: str, data_name: str, data_list: list, catalog_title=None):
    keyboard = ReplyKeyboardBuilder()

    if data_name == 'catalog':
        for item in data_list:
            keyboard.add(KeyboardButton(
                text=connector[lang][data_name][item.title]['logo'] + ' ' + connector[lang][data_name][item.title]['name']))

        keyboard.add(KeyboardButton(text=connector[lang]['button']['exit']))

        sizes = [2 for _ in range(len(data_list) // 2)] + [1] + [1]\
            if len(data_list) % 2 else [2 for _ in range(len(data_list) // 2)] + [1]
    else:
        for item in data_list:
            keyboard.add(KeyboardButton(text=connector[lang]['catalog'][catalog_title][data_name][item.title]))

        keyboard.add(KeyboardButton(text=connector[lang]['button']['back']))
        keyboard.add(KeyboardButton(text=connector[lang]['button']['exit']))

        sizes = [2 for _ in range(len(data_list) // 2)] + [1] + [2]\
            if len(data_list) % 2 else [2 for _ in range(len(data_list) // 2)] + [2]

    return keyboard.adjust(*sizes).as_markup(resize_keyboard=True, one_time_keyboard=True)


def vacancy_keyboard_button(lang: str, sizes: tuple[int] = (2,)):
    keyboard = ReplyKeyboardBuilder()

    keyboard.add(KeyboardButton(text=connector[lang]['button']['back']))
    keyboard.add(KeyboardButton(text=connector[lang]['button']['exit']))

    return keyboard.adjust(*sizes).as_markup(resize_keyboard=True, one_time_keyboard=True)


def vacancy_choice_button(lang: str, sizes: tuple[int] = (2,)):
    keyboard = ReplyKeyboardBuilder()

    keyboard.add(KeyboardButton(text='✅ ' + connector[lang]['button']['yes']))
    keyboard.add(KeyboardButton(text='❎ ' + connector[lang]['button']['not']))

    keyboard.add(KeyboardButton(text=connector[lang]['button']['back']))
    keyboard.add(KeyboardButton(text=connector[lang]['button']['exit']))

    return keyboard.adjust(*sizes).as_markup(resize_keyboard=True, one_time_keyboard=True)


def vacancy_location_button(lang: str, country_name: str, data_name: str, data_list: list, region_name=None):
    keyboard = ReplyKeyboardBuilder()

    if data_name == 'region':
        for item in data_list:
            keyboard.add(KeyboardButton(text=connector[lang]['country'][country_name]['region'][item.name]['name']))

        sizes = [2 for _ in range(len(data_list) // 2)] + [1] + [2] \
            if len(data_list) % 2 else [2 for _ in range(len(data_list) // 2)] + [2]
    else:
        for item in data_list:
            keyboard.add(
                KeyboardButton(text=connector[lang]['country'][country_name]['region'][region_name]['city'][item.name])
            )

        keyboard.add(KeyboardButton(text=connector[lang]['button']['skip']))

        sizes = [2 for _ in range((len(data_list) + 1) // 2)] + [1] \
            if len(data_list) % 2 else [2 for _ in range((len(data_list) + 1) // 2)]

    keyboard.add(KeyboardButton(text=connector[lang]['button']['back']))
    keyboard.add(KeyboardButton(text=connector[lang]['button']['exit']))

    sizes.append(2)

    return keyboard.adjust(*sizes).as_markup(resize_keyboard=True, one_time_keyboard=True)
