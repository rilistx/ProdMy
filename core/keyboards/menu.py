from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from core.utils.connector import connector


class MenuCallBack(CallbackData, prefix="main"):
    lang: str | None = None
    user_id: int | None = None
    view: str | None = None
    level: int | None = None
    key: str | None = None
    catalog_id: int | None = None
    subcatalog_id: int | None = None
    page: int = 1
    vacancy_id: int | None = None


def get_menu_button(lang, level, sizes: tuple[int] = (1, 1, 1, 2, 2, )):
    keyboard = InlineKeyboardBuilder()

    for callback, text in connector[lang]['button']['menu'].items():
        if callback == 'catalog':
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    lang=lang,
                    level=level + 1,
                    key=callback,
                ).pack(),
            ))
        elif callback == 'browse':
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    lang=lang,
                    view='your',
                    level=3,
                    key='view',
                ).pack()
            ))
        elif callback == 'create':
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    lang=lang,
                    level=20,
                    key=callback,
                ).pack(),
            ))
        elif callback == 'favorite':
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    lang=lang,
                    view='liked',
                    level=3,
                    key='view',
                ).pack(),
            ))
        else:
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    lang=lang,
                    level=level,
                    key=callback,
                ).pack(),
            ))

    return keyboard.adjust(*sizes).as_markup()


def get_profession_button(*, lang: str, level: int, data_name: str, data_list: list, catalog_title=None):
    keyboard = InlineKeyboardBuilder()

    for item in data_list:
        if data_name == 'catalog':
            keyboard.add(InlineKeyboardButton(
                text=connector[lang][data_name][item.title]['logo'] + ' ' + connector[lang][data_name][item.title]['name'],
                callback_data=MenuCallBack(
                    lang=lang,
                    level=level + 1,
                    key='subcatalog',
                    catalog_id=item.id,
                ).pack(),
            ))
        else:
            keyboard.add(InlineKeyboardButton(
                text=connector[lang]['catalog'][catalog_title][data_name][item.title],
                callback_data=MenuCallBack(
                    lang=lang,
                    view='all',
                    level=level + 1,
                    key='view',
                    catalog_id=item.catalog_id,
                    subcatalog_id=item.id,
                ).pack(),
            ))

    if data_name == 'subcatalog':
        keyboard.add(InlineKeyboardButton(
            text=connector[lang]['button']['back'],
            callback_data=MenuCallBack(
                lang=lang,
                level=level - 1,
                key='catalog',
            ).pack(),
        ))

    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['exit'],
        callback_data=MenuCallBack(
            lang=lang,
            level=0,
            key='menu',
        ).pack(),
    ))

    sizes = [2 for _ in range(len(data_list) // 2)] + ([1] if len(data_list) % 2 else []) + ([2] if data_name == 'subcatalog' else [1])

    return keyboard.adjust(*sizes).as_markup()


def get_vacancy_button(lang, view, level, key, catalog_id, subcatalog_id, page, pagination_button, vacancy_id, counter: [int] = 0):
    keyboard = InlineKeyboardBuilder()

    for text, menu_name in pagination_button.items():
        if menu_name == "next":
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    lang=lang,
                    view=view,
                    level=level,
                    key=key,
                    catalog_id=catalog_id,
                    subcatalog_id=subcatalog_id,
                    page=page + 1,
                ).pack(),
            ))
            counter += 1
        elif menu_name == "previous":
            keyboard.add(InlineKeyboardButton(
                text=text,
                callback_data=MenuCallBack(
                    lang=lang,
                    view=view,
                    level=level,
                    key=key,
                    catalog_id=catalog_id,
                    subcatalog_id=subcatalog_id,
                    page=page - 1,
                ).pack(),
            ))
            counter += 1

    if vacancy_id:
        keyboard.add(InlineKeyboardButton(
            text='Просмотреть',
            callback_data=MenuCallBack(
                lang=lang,
                view=view,
                level=level + 1,
                key='description',
                catalog_id=catalog_id,
                subcatalog_id=subcatalog_id,
                page=page,
                vacancy_id=vacancy_id,
            ).pack(),
        ))

    if view == 'all':
        keyboard.add(InlineKeyboardButton(
            text=connector[lang]['button']['back'],
            callback_data=MenuCallBack(
                lang=lang,
                level=level - 1,
                key='subcatalog',
                catalog_id=catalog_id,
            ).pack(),
        ))

    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['exit'],
        callback_data=MenuCallBack(
            lang=lang,
            level=0,
            key='menu',
        ).pack(),
    ))

    sizes = ([counter] if counter else []) + ([1] if vacancy_id else []) + ([2] if view == 'all' else [1])

    return keyboard.adjust(*sizes).as_markup()


def get_description_button(lang, user_id, view, level, key, catalog_id, subcatalog_id, page, vacancy_id, liked_id, complaint_id, your_vacancy):
    keyboard = InlineKeyboardBuilder()

    if not your_vacancy and view == 'all' or not your_vacancy and view == 'liked':
        keyboard.add(InlineKeyboardButton(
            text='Убрать из избранного' if liked_id else 'В избранное',
            callback_data=MenuCallBack(
                lang=lang,
                method='favorite',
                view=view,
                level=level,
                key=key,
                catalog_id=catalog_id,
                subcatalog_id=subcatalog_id,
                page=page,
                vacancy_id=vacancy_id,
            ).pack(),
        ))
        keyboard.add(InlineKeyboardButton(
            text='Убарть жалобу' if complaint_id else 'Пожаловаться',
            callback_data=MenuCallBack(
                lang=lang,
                method='feedback',
                view=view,
                level=level,
                key=key,
                catalog_id=catalog_id,
                subcatalog_id=subcatalog_id,
                page=page,
                vacancy_id=vacancy_id,
            ).pack(),
        ))

        sizes = [1, 1]
    else:
        keyboard.add(InlineKeyboardButton(
            text='Изменить',
            callback_data=MenuCallBack(
                lang=lang,
                method='update',
                key='vacancy',
                vacancy_id=vacancy_id,
            ).pack(),
        ))

        keyboard.add(InlineKeyboardButton(
            text='Удалить',
            callback_data=MenuCallBack(
                lang=lang,
                user_id=user_id,
                method='delete',
                view=view,
                level=level - 1,
                key='view',
                catalog_id=catalog_id,
                subcatalog_id=subcatalog_id,
                page=page,
                vacancy_id=vacancy_id,
            ).pack(),
        ))

        sizes = [2]

    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['back'],
        callback_data=MenuCallBack(
            lang=lang,
            user_id=user_id,
            view=view,
            level=level - 1,
            key='view',
            catalog_id=catalog_id,
            subcatalog_id=subcatalog_id,
            page=page,
        ).pack(),
    ))
    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['exit'],
        callback_data=MenuCallBack(
            lang=lang,
            level=0,
            key='menu',
        ).pack(),
    ))

    sizes += [2]

    return keyboard.adjust(*sizes).as_markup()


def get_create_button(lang: str, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['create'],
        callback_data=MenuCallBack(
            lang=lang,
            method='create',
            key='vacancy',
        ).pack(),
    ))
    keyboard.add(InlineKeyboardButton(
        text=connector[lang]['button']['exit'],
        callback_data=MenuCallBack(
            lang=lang,
            level=0,
            key='menu',
        ).pack(),
    ))

    return keyboard.adjust(*sizes).as_markup()
