from sqlalchemy.ext.asyncio import AsyncSession

from core.commands.languages import json
from core.keyboards.menu import get_menu_button, get_catalog_button, get_subcatalog_button, get_create_button
from core.models.querys import get_informer, get_catalog_all, get_catalog_one, get_subcatalog_all


async def shaping_menu(session, lang, level, name):
    informer = await get_informer(session, name)
    text = json[lang]['informer'][informer.name]

    button = get_menu_button(lang=lang, level=level)

    return text, button


async def shaping_catalog(session, lang, level, name):
    informer = await get_informer(session, name)
    text = json[lang]['informer'][informer.name]

    catalog = await get_catalog_all(session)
    button = get_catalog_button(lang=lang, level=level, catalog=catalog)

    return text, button


async def shaping_subcatalog(session, lang, level, name, catalog_id):
    informer = await get_informer(session, name)
    text = json[lang]['informer'][informer.name]

    catalog = await get_catalog_one(session, catalog_id)
    subcatalog = await get_subcatalog_all(session, catalog_id)
    button = get_subcatalog_button(lang=lang, level=level, catalog=catalog, subcatalog=subcatalog)

    return text, button


async def shaping_vacancy(session, lang, level, name, subcatalog_id, page):
    # vacancy = get_vacancy_all(session, subcatalog_id)
    pass


async def shaping_create(session, lang, name):
    informer = await get_informer(session, name)
    text = json[lang]['informer'][informer.name]

    button = get_create_button(lang)

    return text, button


async def menu_processing(
        session: AsyncSession,
        lang: str,
        level: int | None = None,
        name: str | None = None,
        catalog_id: int | None = None,
        subcatalog_id: int | None = None,
        page: int | None = None,
        vacancy: int | None = None
):
    if level == 0:
        return await shaping_menu(session, lang, level, name)
    elif level == 1:
        return await shaping_catalog(session, lang, level, name)
    elif level == 2:
        return await shaping_subcatalog(session, lang, level, name, catalog_id)
    elif level == 3:
        return await shaping_vacancy(session, lang, level, name, subcatalog_id, page)

    elif level == 6:
        return await shaping_create(session, lang, name)
