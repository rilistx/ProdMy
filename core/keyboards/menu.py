from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from core.utils.connector import connector


class MenuCallBack(CallbackData, prefix="main"):
    lang: str
    level: int
    key: str
    catalog_id: int | None = None
    subcatalog_id: int | None = None
    page: int = 1
    vacancy: int | None = None


def get_menu_button(lang: str, level: int):
    keyboard = InlineKeyboardBuilder()

    button = {}

    for key, info in connector[lang]['button']['menu'].items():
        button[key] = info

    for callback, text in button.items():
        if callback == 'catalog':
            keyboard.add(InlineKeyboardButton(
                text=text, callback_data=MenuCallBack(lang=lang, level=level + 1, key=callback).pack()
            ))
        elif callback == 'create':
            keyboard.add(InlineKeyboardButton(
                text=text, callback_data=MenuCallBack(lang=lang, level=6, key=callback).pack()
            ))
        # elif callback == 'browse':
        #     keyboard.add(InlineKeyboardButton(text=text,
        #                                       callback_data=MenuCallBack(level=level + 1, key=callback).pack()))
        else:
            keyboard.add(InlineKeyboardButton(
                text=text, callback_data=MenuCallBack(lang=lang, level=level, key=callback).pack()
            ))

    sizes = [1, 1, 1, 2, 2]

    return keyboard.adjust(*sizes).as_markup()


def get_catalog_button(lang: str, level: int, catalog: list):
    keyboard = InlineKeyboardBuilder()

    for item in catalog:
        keyboard.add(InlineKeyboardButton(
            text=connector[lang]['catalog'][item.title]['logo'] + ' ' + connector[lang]['catalog'][item.title]['name'],
            callback_data=MenuCallBack(lang=lang, level=level + 1, key='subcatalog', catalog_id=item.id).pack()
        ))

    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['back'],
        callback_data=MenuCallBack(lang=lang, level=level - 1, key='menu').pack()
    ))

    sizes = [2 for _ in range(len(catalog) // 2)] + [1] + [1] \
        if len(catalog) % 2 else [2 for _ in range(len(catalog) // 2)] + [1]

    return keyboard.adjust(*sizes).as_markup()


def get_subcatalog_button(lang: str, level: int, catalog, subcatalog: list):
    keyboard = InlineKeyboardBuilder()

    for item in subcatalog:
        keyboard.add(InlineKeyboardButton(
            text=connector[lang]['catalog'][catalog.title]['subcatalog'][item.title],
            callback_data=MenuCallBack(
                lang=lang,
                level=level + 1,
                key=item.title,
                catalog_id=item.catalog_id,
                subcatalog_id=item.id
            ).pack()
        ))

    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['back'],
        callback_data=MenuCallBack(lang=lang, level=level - 1, key='catalog').pack()
    ))
    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['exit'],
        callback_data=MenuCallBack(lang=lang, level=0, key='menu').pack()
    ))

    sizes = [2 for _ in range(len(subcatalog) // 2)] + [1] + [2] \
        if len(subcatalog) % 2 else [2 for _ in range(len(subcatalog) // 2)] + [2]

    return keyboard.adjust(*sizes).as_markup()


def get_vacancy_button(lang: str, level: int, key: str, catalog_id: int, subcatalog_id: int, page: int, pagination_button: dict):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(
        text='Назад',
        callback_data=MenuCallBack(
            lang=lang, level=level - 1, key='subcatalog', catalog_id=catalog_id, subcatalog_id=subcatalog_id).pack()))
    keyboard.add(InlineKeyboardButton(text='Выход',
                                      callback_data=MenuCallBack(lang=lang, level=0, key='menu').pack()))

    keyboard.adjust(2)

    row = []
    for text, menu_name in pagination_button.items():
        if menu_name == "next":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallBack(
                                                lang=lang,
                                                level=level,
                                                key=key,
                                                catalog_id=catalog_id,
                                                subcatalog_id=subcatalog_id,
                                                page=page + 1).pack()))

        elif menu_name == "previous":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallBack(
                                                lang=lang,
                                                level=level,
                                                key=key,
                                                catalog_id=catalog_id,
                                                subcatalog_id=subcatalog_id,
                                                page=page - 1).pack()))

    return keyboard.row(*row).as_markup()


def get_create_button(lang: str, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['create'],
        callback_data=f'vacancy_create_{lang}')
    )
    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['exit'],
        callback_data=MenuCallBack(lang=lang, level=0, key='menu').pack()
    ))

    return keyboard.adjust(*sizes).as_markup()
