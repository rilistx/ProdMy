from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from core.utils.connector import connector


class MenuCallBack(CallbackData, prefix="main"):
    lang: str
    level: int
    name: str
    catalog_id: int | None = None
    subcatalog_id: int | None = None
    page: int = 1
    vacancy: int | None = None


def get_menu_button(*, lang: str, level: int):
    keyboard = InlineKeyboardBuilder()
    button = {}

    for key, info in connector[lang]['button']['menu'].items():
        button[info] = key

    for text, name in button.items():
        if name == 'catalog':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(lang=lang, level=level + 1, name=name).pack()))
        elif name == 'create':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(lang=lang, level=6, name=name).pack()))
        # elif name == 'browse':
        #     keyboard.add(InlineKeyboardButton(text=text,
        #                                       callback_data=MenuCallBack(level=level + 1, name=name).pack()))
        else:
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(lang=lang, level=level, name=name).pack()))

    return keyboard.adjust(1, 1, 1, 2, 2).as_markup()


def get_catalog_button(*, lang: str, level: int, catalog: list):
    keyboard = InlineKeyboardBuilder()

    for item in catalog:
        keyboard.add(InlineKeyboardButton(
            text=connector[lang]['catalog'][item.name]['name'],
            callback_data=MenuCallBack(lang=lang, level=level + 1, name='subcatalog', catalog_id=item.id).pack()
        ))

    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['back'],
        callback_data=MenuCallBack(lang=lang, level=level - 1, name='menu').pack()
    ))

    sizes = [2 for _ in range(len(catalog) // 2)] + [1] + [1] \
        if len(catalog) % 2 else [2 for _ in range(len(catalog) // 2)] + [1]

    return keyboard.adjust(*sizes).as_markup()


def get_subcatalog_button(*, lang: str, level: int, catalog, subcatalog: list):
    keyboard = InlineKeyboardBuilder()

    for item in subcatalog:
        keyboard.add(InlineKeyboardButton(
            text=connector[lang]['catalog'][catalog.name]['sub_name'][item.name],
            callback_data=MenuCallBack(
                lang=lang,
                level=level + 1,
                name=item.name,
                catalog_id=item.catalog_id,
                subcatalog_id=item.id
            ).pack()
        ))

    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['back'],
        callback_data=MenuCallBack(lang=lang, level=level - 1, name='catalog').pack()
    ))
    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['exit'],
        callback_data=MenuCallBack(lang=lang, level=0, name='menu').pack()
    ))

    sizes = [2 for _ in range(len(subcatalog) // 2)] + [1] + [2] \
        if len(subcatalog) % 2 else [2 for _ in range(len(subcatalog) // 2)] + [2]

    return keyboard.adjust(*sizes).as_markup()


def get_create_button(lang: str):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['create'],
        callback_data=f'vacancy_{lang}')
    )
    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['exit'],
        callback_data=MenuCallBack(lang=lang, level=0, name='menu').pack()
    ))

    return keyboard.adjust(2, ).as_markup()
