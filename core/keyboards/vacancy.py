from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from core.commands.languages import json
from core.keyboards.menu import MenuCallBack


class ChoiceCallBack(CallbackData, prefix="choice"):
    name: str


def vacancy_profession_button(lang, data_name, data_list, catalog_name=None):
    keyboard = InlineKeyboardBuilder()

    if data_name == 'catalog':
        for item in data_list:
            keyboard.add(InlineKeyboardButton(
                text=json[lang][data_name][item.name]['name'],
                callback_data=f'catalog_{item.name}_{item.id}',
            ))
    else:
        for item in data_list:
            keyboard.add(InlineKeyboardButton(
                text=json[lang]['catalog'][catalog_name]['sub_name'][item.name],
                callback_data=f'subcatalog_{item.id}',
            ))

    keyboard.add(InlineKeyboardButton(
        text='Назад',
        callback_data=MenuCallBack(lang=lang, level=0, name='menu').pack()
    ))
    keyboard.add(InlineKeyboardButton(
        text='Выйти',
        callback_data=MenuCallBack(lang=lang, level=0, name='menu').pack()
    ))

    sizes = [2 for _ in range(len(data_list) // 2)] + [1] + [2] \
        if len(data_list) % 2 else [2 for _ in range(len(data_list) // 2)] + [2]

    return keyboard.adjust(*sizes).as_markup()


def vacancy_keyboard_button(lang):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(
        text='Назад',
        callback_data=MenuCallBack(lang=lang, level=0, name='menu').pack()
    ))
    keyboard.add(InlineKeyboardButton(
        text='Выйти',
        callback_data=MenuCallBack(lang=lang, level=0, name='menu').pack()))

    return keyboard.adjust(2, ).as_markup()


def vacancy_selection_button(lang, process, dict_data):
    keyboard = InlineKeyboardBuilder()

    for name, description in json[lang][process].items():
        for key, value in dict_data.items():
            if name == key and value:
                keyboard.add(InlineKeyboardButton(
                    text='✅ ' + description,
                    callback_data=ChoiceCallBack(name=key).pack(),
                ))
            if name == key and not value:
                keyboard.add(InlineKeyboardButton(
                    text='❌ ' + description,
                    callback_data=ChoiceCallBack(name=key).pack(),
                ))

    keyboard.add(InlineKeyboardButton(
        text='Далее',
        callback_data='next',
    ))
    keyboard.add(InlineKeyboardButton(
        text='Назад',
        callback_data=MenuCallBack(lang=lang, level=0, name='menu').pack(),
    ))
    keyboard.add(InlineKeyboardButton(
        text='Выйти',
        callback_data=MenuCallBack(lang=lang, level=0, name='menu').pack(),
    ))

    sizes = [1 for _ in range(len(dict_data))] + [1] + [2]

    return keyboard.adjust(*sizes).as_markup()


def vacancy_choice_button(lang):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='✅ С инвалидностью', callback_data='choice_true'))
    keyboard.add(InlineKeyboardButton(text='❌ Без инвалидности', callback_data='choice_false'))

    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=MenuCallBack(lang=lang, level=0, name='menu').pack()))
    keyboard.add(InlineKeyboardButton(text='Выйти', callback_data=MenuCallBack(lang=lang, level=0, name='menu').pack()))

    return keyboard.adjust(2, 2).as_markup()


def add_vacancy_city_button(city):
    keyboard = InlineKeyboardBuilder()

    for sub in city:
        keyboard.add(InlineKeyboardButton(
            text=sub.name,
            callback_data=f'city_{sub.id}'
        ))

    # if city
    keyboard.add(InlineKeyboardButton(text='Нет', callback_data=f'city_none'))

    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=MenuCallBack(level=0, name='menu').pack()))
    keyboard.add(InlineKeyboardButton(text='Выйти', callback_data=MenuCallBack(level=0, name='menu').pack()))

    sizes = [2 for _ in range((len(city) + 1) // 2)] + [1] + [2] if len(city) % 2 else [2 for _ in range((len(city) + 1) // 2)] + [2]

    return keyboard.adjust(*sizes).as_markup()
