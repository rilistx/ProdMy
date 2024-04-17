from sqlalchemy.ext.asyncio import AsyncSession

from core.keyboards.menu import get_menu_button, get_catalog_button, get_subcatalog_button, get_create_button, \
    get_vacancy_button, get_description_button, get_your_description_button, get_your_vacation_button, \
    get_favorite_description_button, get_favorite_vacation_button
from core.models.querys import get_catalog_all, get_catalog_one, get_subcatalog_all, get_vacancy_all_active, \
    get_liked_one, get_complaint_one, get_vacancy_one, get_vacancy_user, get_favorite_vacancy
from core.utils.connector import connector
from core.utils.paginator import Paginator


def pages(paginator: Paginator):
    button = dict()
    if paginator.has_previous():
        button["◀ Пред."] = "previous"

    if paginator.has_next():
        button["След. ▶"] = "next"

    return button


async def shaping_menu(lang, level, key):
    text = connector[lang]['message']['menu'][key]
    button = get_menu_button(lang=lang, level=level)

    return text, button


async def shaping_catalog(session, lang, level, key):
    text = connector[lang]['message']['menu'][key]
    catalog = await get_catalog_all(session=session)
    button = get_catalog_button(lang=lang, level=level, catalog=catalog)

    return text, button


async def shaping_subcatalog(session, lang, level, key, catalog_id):
    text = connector[lang]['message']['menu'][key]
    catalog = await get_catalog_one(session=session, catalog_id=catalog_id)
    subcatalog = await get_subcatalog_all(session=session, catalog_id=catalog_id)
    button = get_subcatalog_button(lang=lang, level=level, catalog=catalog, subcatalog=subcatalog)

    return text, button


async def shaping_vacancy_all(session, lang, level, key, catalog_id, subcatalog_id, page, vacancy_id=None):
    vacancy = await get_vacancy_all_active(session=session, subcatalog_id=subcatalog_id)
    pagination_button = {}

    if vacancy:
        paginator = Paginator(vacancy, page=page)
        vacancy_page = paginator.get_page()[0]
        pagination_button = pages(paginator)
        vacancy_id = vacancy_page.id

        text = f"{vacancy_page.name}"
    else:
        text = connector[lang]['message']['menu']['vacancy']

    button = get_vacancy_button(
        lang=lang,
        level=level,
        key=key,
        catalog_id=catalog_id,
        subcatalog_id=subcatalog_id,
        page=page,
        pagination_button=pagination_button,
        vacancy_id=vacancy_id,
    )

    return text, button


async def shaping_description_all(session, lang, user_id, level, key, catalog_id, subcatalog_id, page, vacancy_id):
    vacancy = await get_vacancy_one(session=session, vacancy_id=vacancy_id)
    your_vacancy = await get_vacancy_one(session=session, vacancy_id=vacancy_id, user_id=user_id)

    liked = await get_liked_one(session=session, user_id=user_id, vacancy_id=vacancy_id)
    liked_id = liked.id if liked else None

    complaint = await get_complaint_one(session=session, user_id=user_id, vacancy_id=vacancy_id)
    complaint_id = complaint.id if complaint else None

    text = f"{vacancy.name}\n\n{vacancy.description}\n\n{vacancy.salary}"

    button = get_description_button(
        lang=lang,
        user_id=user_id,
        level=level,
        key=key,
        catalog_id=catalog_id,
        subcatalog_id=subcatalog_id,
        page=page,
        vacancy_id=vacancy_id,
        liked_id=liked_id,
        complaint_id=complaint_id,
        user_vacancy=your_vacancy,
    )

    return text, button


async def shaping_vacation_your(session, lang, user_id, level, key, page, vacancy_id=None):
    user_vacancy = await get_vacancy_user(session=session, user_id=user_id)
    pagination_button = {}

    if user_vacancy:
        paginator = Paginator(user_vacancy, page=page)
        vacancy_page = paginator.get_page()[0]
        pagination_button = pages(paginator)
        vacancy_id = vacancy_page.id

        text = f"{vacancy_page.name}"
    else:
        text = connector[lang]['message']['menu']['browse']

    button = get_your_vacation_button(
        lang=lang,
        level=level,
        key=key,
        page=page,
        pagination_button=pagination_button,
        vacancy_id=vacancy_id,
    )

    return text, button


async def shaping_description_your(session, lang, user_id, level, key, page, vacancy_id):
    user_vacancy = await get_vacancy_one(session=session, vacancy_id=vacancy_id, user_id=user_id)

    text = f"{user_vacancy.name}\n\n{user_vacancy.description}\n\n{user_vacancy.salary}"

    button = get_your_description_button(
        lang=lang,
        level=level,
        key=key,
        page=page,
        vacancy_id=vacancy_id,
    )

    return text, button


async def shaping_vacation_favorite(session, lang, user_id, level, key, page, vacancy_id=None):
    user_favorite = await get_favorite_vacancy(session=session, user_id=user_id)

    pagination_button = {}

    if user_favorite:
        paginator = Paginator(user_favorite, page=page)
        vacancy_page = paginator.get_page()[0]
        pagination_button = pages(paginator)
        vacancy_id = vacancy_page.vacancy.id

        text = f"{vacancy_page.vacancy.name}"
    else:
        text = connector[lang]['message']['menu']['favorite']

    button = get_favorite_vacation_button(
        lang=lang,
        level=level,
        key=key,
        page=page,
        pagination_button=pagination_button,
        vacancy_id=vacancy_id,
    )

    return text, button


async def shaping_description_favorite(session, lang, user_id, level, key, page, vacancy_id):
    user_favorite = await get_vacancy_one(session=session, vacancy_id=vacancy_id)

    liked = await get_liked_one(session=session, user_id=user_id, vacancy_id=vacancy_id)
    liked_id = liked.id if liked else None

    complaint = await get_complaint_one(session=session, user_id=user_id, vacancy_id=vacancy_id)
    complaint_id = complaint.id if complaint else None

    text = f"{user_favorite.name}\n\n{user_favorite.description}\n\n{user_favorite.salary}"

    button = get_favorite_description_button(
        lang=lang,
        user_id=user_id,
        level=level,
        key=key,
        page=page,
        vacancy_id=vacancy_id,
        liked_id=liked_id,
        complaint_id=complaint_id,
    )

    return text, button


async def shaping_create_vacation(lang, key):
    text = connector[lang]['message']['menu'][key]
    button = get_create_button(lang)

    return text, button


async def menu_processing(
        session: AsyncSession,
        lang: str | None = None,
        user_id: int | None = None,
        method: str | None = None,
        level: int | None = None,
        key: str | None = None,
        catalog_id: int | None = None,
        subcatalog_id: int | None = None,
        page: int | None = None,
        vacancy_id: int | None = None,
        liked_id: int | None = None,
        complaint_id: int | None = None,
):
    if level == 0:
        return await shaping_menu(lang, level, key)
    elif level == 1:
        return await shaping_catalog(session, lang, level, key)
    elif level == 2:
        return await shaping_subcatalog(session, lang, level, key, catalog_id)
    elif level == 3:
        return await shaping_vacancy_all(session, lang, level, key, catalog_id, subcatalog_id, page)
    elif level == 4:
        return await shaping_description_all(session, lang, user_id, level, key, catalog_id, subcatalog_id, page, vacancy_id)

    elif level == 10:
        return await shaping_vacation_your(session, lang, user_id, level, key, page)
    elif level == 11:
        return await shaping_description_your(session, lang, user_id, level, key, page, vacancy_id)
    elif level == 20:
        return await shaping_create_vacation(lang, key)
    elif level == 30:
        return await shaping_vacation_favorite(session, lang, user_id, level, key, page)
    elif level == 31:
        return await shaping_description_favorite(session, lang, user_id, level, key, page, vacancy_id)
