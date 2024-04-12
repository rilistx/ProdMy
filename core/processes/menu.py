from sqlalchemy.ext.asyncio import AsyncSession

from core.keyboards.menu import get_menu_button, get_catalog_button, get_subcatalog_button, get_create_button, \
    get_vacancy_button, get_description_button
from core.models.querys import get_catalog_all, get_catalog_one, get_subcatalog_all, get_vacancy_all, get_vacancy_one
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
    catalog = await get_catalog_all(session)
    button = get_catalog_button(lang=lang, level=level, catalog=catalog)

    return text, button


async def shaping_subcatalog(session, lang, level, key, catalog_id):
    text = connector[lang]['message']['menu'][key]
    catalog = await get_catalog_one(session, catalog_id=catalog_id)
    subcatalog = await get_subcatalog_all(session, catalog_id)
    button = get_subcatalog_button(lang=lang, level=level, catalog=catalog, subcatalog=subcatalog)

    return text, button


async def shaping_vacancy(session, lang, level, key, catalog_id, subcatalog_id, page):
    vacancy = await get_vacancy_all(session, subcatalog_id)
    pagination_button = {}
    vacancy_id = None

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
        vacancy_id=vacancy_id
    )

    return text, button


async def shaping_description(session, lang, level, key, catalog_id, subcatalog_id, page, vacancy_id):
    vacancy = await get_vacancy_one(session, vacancy_id)

    text = f"{vacancy.name}\n\n{vacancy.description}\n\n{vacancy.price}"

    button = get_description_button(
        lang=lang,
        level=level,
        key=key,
        catalog_id=catalog_id,
        subcatalog_id=subcatalog_id,
        page=page,
    )

    return text, button


async def shaping_create(lang, key):
    text = connector[lang]['message']['menu'][key]
    button = get_create_button(lang)

    return text, button


async def menu_processing(
        session: AsyncSession,
        lang: str,
        level: int | None = None,
        key: str | None = None,
        catalog_id: int | None = None,
        subcatalog_id: int | None = None,
        page: int | None = None,
        vacancy_id: int | None = None
):
    if level == 0:
        return await shaping_menu(lang, level, key)
    elif level == 1:
        return await shaping_catalog(session, lang, level, key)
    elif level == 2:
        return await shaping_subcatalog(session, lang, level, key, catalog_id)
    elif level == 3:
        return await shaping_vacancy(session, lang, level, key, catalog_id, subcatalog_id, page)
    elif level == 4:
        return await shaping_description(session, lang, level, key, catalog_id, subcatalog_id, page, vacancy_id)

    elif level == 6:
        return await shaping_create(lang, key)
