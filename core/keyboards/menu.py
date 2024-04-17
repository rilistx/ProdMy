from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from core.utils.connector import connector


class MenuCallBack(CallbackData, prefix="main"):
    lang: str | None = None
    user_id: int | None = None
    method: str | None = None
    level: int | None = None
    key: str | None = None
    catalog_id: int | None = None
    subcatalog_id: int | None = None
    page: int = 1
    vacancy_id: int | None = None
    liked_id: int | None = None
    complaint_id: int | None = None


def get_menu_button(lang, level, sizes: tuple[int] = (1, 1, 1, 2, 2, )):
    keyboard = InlineKeyboardBuilder()

    for callback, text in connector[lang]['button']['menu'].items():
        if callback == 'catalog':
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    lang=lang, level=level + 1, key=callback,
                ).pack(),
            ))
        elif callback == 'browse':
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    lang=lang,
                    level=10,
                    key=callback,
                ).pack()
            ))
        elif callback == 'create':
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    lang=lang, level=20, key=callback,
                ).pack(),
            ))
        elif callback == 'favorite':
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    lang=lang, level=30, key=callback,
                ).pack(),
            ))
        else:
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    lang=lang, level=level, key=callback
                ).pack(),
            ))

    return keyboard.adjust(*sizes).as_markup()


def get_catalog_button(lang, level, catalog):
    keyboard = InlineKeyboardBuilder()

    for item in catalog:
        keyboard.add(InlineKeyboardButton(
            text=connector[lang]['catalog'][item.title]['logo'] + ' ' + connector[lang]['catalog'][item.title]['name'],
            callback_data=MenuCallBack(
                lang=lang, level=level + 1, key='subcatalog', catalog_id=item.id
            ).pack(),
        ))

    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['back'],
        callback_data=MenuCallBack(
            lang=lang, level=level - 1, key='menu'
        ).pack(),
    ))

    sizes = [2 for _ in range(len(catalog) // 2)] + [1, 1] if len(catalog) % 2 else [1]

    return keyboard.adjust(*sizes).as_markup()


def get_subcatalog_button(lang, level, catalog, subcatalog):
    keyboard = InlineKeyboardBuilder()

    for item in subcatalog:
        keyboard.add(InlineKeyboardButton(
            text=connector[lang]['catalog'][catalog.title]['subcatalog'][item.title],
            callback_data=MenuCallBack(
                lang=lang, level=level + 1, key=item.title, catalog_id=item.catalog_id, subcatalog_id=item.id
            ).pack(),
        ))

    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['back'],
        callback_data=MenuCallBack(
            lang=lang, level=level - 1, key='catalog'
        ).pack(),
    ))
    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['exit'],
        callback_data=MenuCallBack(
            lang=lang, level=0, key='menu'
        ).pack(),
    ))

    sizes = [2 for _ in range(len(subcatalog) // 2)] + [1, 2] if len(subcatalog) % 2 else [2]

    return keyboard.adjust(*sizes).as_markup()


def get_vacancy_button(lang, level, key, catalog_id, subcatalog_id, page, pagination_button, vacancy_id, counter: [int] = 0):
    keyboard = InlineKeyboardBuilder()

    for text, menu_name in pagination_button.items():
        if menu_name == "next":
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    lang=lang, level=level, key=key, catalog_id=catalog_id, subcatalog_id=subcatalog_id, page=page + 1
                ).pack(),
            ))
            counter += 1
        elif menu_name == "previous":
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    lang=lang, level=level, key=key, catalog_id=catalog_id, subcatalog_id=subcatalog_id, page=page - 1
                ).pack(),
            ))
            counter += 1

    if vacancy_id:
        keyboard.add(InlineKeyboardButton(
            text='Просмотреть',
            callback_data=MenuCallBack(
                lang=lang, level=level + 1, key=key, catalog_id=catalog_id, subcatalog_id=subcatalog_id, page=page, vacancy_id=vacancy_id,
            ).pack(),
        ))

    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['back'],
        callback_data=MenuCallBack(
            lang=lang, level=level - 1, key='subcatalog', catalog_id=catalog_id,
        ).pack(),
    ))
    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['exit'],
        callback_data=MenuCallBack(
            lang=lang, level=0, key='menu'
        ).pack(),
    ))

    if counter:
        sizes = [counter, 1, 2]
    elif vacancy_id:
        sizes = [1, 2]
    else:
        sizes = [2]

    return keyboard.adjust(*sizes).as_markup()


def get_description_button(lang, user_id, level, key, catalog_id, subcatalog_id, page, vacancy_id, liked_id, complaint_id, user_vacancy):
    keyboard = InlineKeyboardBuilder()

    sizes = []

    if not user_vacancy:
        keyboard.add(InlineKeyboardButton(
            text='Убрать из избранного' if liked_id else 'В избранное',
            callback_data=MenuCallBack(
                lang=lang, user_id=user_id, method='favorite', level=level, key=key, catalog_id=catalog_id, subcatalog_id=subcatalog_id, page=page, vacancy_id=vacancy_id,
            ).pack(),
        ))

        keyboard.add(InlineKeyboardButton(
            text='Убарть жалобу' if complaint_id else 'Пожаловаться',
            callback_data=MenuCallBack(
                lang=lang, user_id=user_id, method='feedback', level=level, key=key, catalog_id=catalog_id, subcatalog_id=subcatalog_id, page=page, vacancy_id=vacancy_id,
            ).pack(),
        ))

        sizes = [1, 1]
    else:
        keyboard.add(InlineKeyboardButton(
            text='Изменить',
            callback_data=MenuCallBack(
                lang=lang, method='update', key='vacancy', vacancy_id=vacancy_id,
            ).pack(),
        ))

        keyboard.add(InlineKeyboardButton(
            text='Удалить',
            callback_data=MenuCallBack(
                lang=lang, method='delete', level=level - 1, key=key, catalog_id=catalog_id, subcatalog_id=subcatalog_id, page=page, vacancy_id=vacancy_id,
            ).pack(),
        ))

        sizes = [2]

    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['back'],
        callback_data=MenuCallBack(
            lang=lang, level=level - 1, key=key, catalog_id=catalog_id, subcatalog_id=subcatalog_id, page=page
        ).pack(),
    ))
    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['exit'],
        callback_data=MenuCallBack(
            lang=lang, level=0, key='menu'
        ).pack(),
    ))

    sizes += [2]

    return keyboard.adjust(*sizes).as_markup()


def get_your_vacation_button(lang, level, key, page, pagination_button, vacancy_id, counter: [int] = 0):
    keyboard = InlineKeyboardBuilder()

    for text, menu_name in pagination_button.items():
        if menu_name == "next":
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    lang=lang, level=level, key=key, page=page + 1
                ).pack(),
            ))
            counter += 1
        elif menu_name == "previous":
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    lang=lang, level=level, key=key, page=page - 1
                ).pack(),
            ))
            counter += 1

    if vacancy_id:
        keyboard.add(InlineKeyboardButton(
            text='Просмотреть',
            callback_data=MenuCallBack(
                lang=lang, level=level + 1, key=key, page=page, vacancy_id=vacancy_id,
            ).pack(),
        ))

    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['exit'],
        callback_data=MenuCallBack(
            lang=lang, level=0, key='menu'
        ).pack(),
    ))

    if counter:
        sizes = [counter, 1, 1]
    elif vacancy_id:
        sizes = [1, 1]
    else:
        sizes = [1]

    return keyboard.adjust(*sizes).as_markup()


def get_your_description_button(lang, level, key, page, vacancy_id):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(
        text='Изменить',
        callback_data=MenuCallBack(
            lang=lang, method='update', key='vacancy', vacancy_id=vacancy_id,
        ).pack(),
    ))

    keyboard.add(InlineKeyboardButton(
        text='Удалить',
        callback_data=MenuCallBack(
            lang=lang, method='delete', level=level - 1, key=key, page=page, vacancy_id=vacancy_id,
        ).pack(),
    ))

    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['back'],
        callback_data=MenuCallBack(
            lang=lang, level=level - 1, key=key, page=page
        ).pack(),
    ))
    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['exit'],
        callback_data=MenuCallBack(
            lang=lang, level=0, key='menu'
        ).pack(),
    ))

    sizes = [2, 2]

    return keyboard.adjust(*sizes).as_markup()


def get_favorite_vacation_button(lang, level, key, page, pagination_button, vacancy_id, counter: [int] = 0):
    keyboard = InlineKeyboardBuilder()

    for text, menu_name in pagination_button.items():
        if menu_name == "next":
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    lang=lang, level=level, key=key, page=page + 1
                ).pack(),
            ))
            counter += 1
        elif menu_name == "previous":
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    lang=lang, level=level, key=key, page=page - 1
                ).pack(),
            ))
            counter += 1

    if vacancy_id:
        keyboard.add(InlineKeyboardButton(
            text='Просмотреть',
            callback_data=MenuCallBack(
                lang=lang, level=level + 1, key=key, page=page, vacancy_id=vacancy_id,
            ).pack(),
        ))

    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['exit'],
        callback_data=MenuCallBack(
            lang=lang, level=0, key='menu'
        ).pack(),
    ))

    if counter:
        sizes = [counter, 1, 1]
    elif vacancy_id:
        sizes = [1, 1]
    else:
        sizes = [1]

    return keyboard.adjust(*sizes).as_markup()


def get_favorite_description_button(lang, user_id, level, key, page, vacancy_id, liked_id, complaint_id):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(
        text='Убрать из избранного' if liked_id else 'В избранное',
        callback_data=MenuCallBack(
            lang=lang, user_id=user_id, method='favorite', level=level, key=key, page=page, vacancy_id=vacancy_id,
        ).pack(),
    ))

    keyboard.add(InlineKeyboardButton(
        text='Убарть жалобу' if complaint_id else 'Пожаловаться',
        callback_data=MenuCallBack(
            lang=lang, user_id=user_id, method='feedback', level=level, key=key, page=page, vacancy_id=vacancy_id,
        ).pack(),
    ))

    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['back'],
        callback_data=MenuCallBack(
            lang=lang, level=level - 1, key=key, page=page
        ).pack(),
    ))
    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['exit'],
        callback_data=MenuCallBack(
            lang=lang, level=0, key='menu'
        ).pack(),
    ))

    sizes = [1, 1, 2]

    return keyboard.adjust(*sizes).as_markup()


def get_create_button(lang: str, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['create'],
        callback_data=MenuCallBack(
            lang=lang, method='create', key='vacancy'
        ).pack(),
    ))
    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['exit'],
        callback_data=MenuCallBack(
            lang=lang, level=0, key='menu'
        ).pack(),
    ))

    return keyboard.adjust(*sizes).as_markup()
