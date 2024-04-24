from sqlalchemy.ext.asyncio import AsyncSession

from core.keyboards.menu import get_menu_button, get_vacancy_button, get_description_button, get_profession_button, \
    get_profile_button, get_confirm_button, get_setting_button, get_about_button, get_admin_button
from core.database.querys import get_catalog_all, get_catalog_one, get_subcatalog_all, get_vacancy_all_active, \
    get_vacancy_one, get_vacancy_user, get_vacancy_favorite, get_liked_one, get_complaint_one, search_user, \
    get_preview_one, create_preview, get_vacancy_admin
from core.utils.connector import connector
from core.utils.paginator import Paginator


def pages(
        paginator: Paginator,
):
    button = dict()
    if paginator.has_previous():
        button["◀ Пред."] = "previous"

    if paginator.has_next():
        button["След. ▶"] = "next"

    return button


async def shaping_menu(
        session: AsyncSession,
        lang: str,
        user_id: int,
        level: int,
        key: str,
):
    user = await search_user(
        session=session,
        user_id=user_id,
    )

    text = connector[lang]['message']['menu'][key]
    button = get_menu_button(
        lang=lang,
        level=level,
        blocked=user.blocked,
        admin=user.is_admin,
    )

    return text, button


async def shaping_catalog(
        session: AsyncSession,
        lang: str,
        level: int,
        key: str,
):
    catalog = await get_catalog_all(session=session)

    text = connector[lang]['message']['menu'][key]
    button = get_profession_button(
        lang=lang,
        level=level,
        data_name='catalog',
        data_list=catalog,
    )

    return text, button


async def shaping_subcatalog(
        session: AsyncSession,
        lang: str,
        level: int,
        key: str,
        catalog_id: int,
):
    catalog = await get_catalog_one(
        session=session,
        catalog_id=catalog_id,
    )
    subcatalog = await get_subcatalog_all(
        session=session,
        catalog_id=catalog_id,
    )

    text = connector[lang]['message']['menu'][key]
    button = get_profession_button(
        lang=lang,
        level=level,
        data_name='subcatalog',
        data_list=subcatalog,
        catalog_title=catalog.title,
    )

    return text, button


async def shaping_vacancy(
        session: AsyncSession,
        lang: str,
        user_id: int,
        view: str,
        level: int,
        key: str,
        page: int,
        catalog_id: int,
        subcatalog_id: int,
        vacancy_id: int | None = None,
):
    if view == 'complaint':
        vacancy = await get_vacancy_admin(
            session=session,
        )
    elif view == 'all':
        vacancy = await get_vacancy_all_active(
            session=session,
            subcatalog_id=subcatalog_id,
        )
    elif view == 'your':
        vacancy = await get_vacancy_user(
            session=session,
            user_id=user_id,
        )
    else:
        vacancy = await get_vacancy_favorite(
            session=session,
            user_id=user_id,
        )

    pagination_button = {}

    if vacancy:
        paginator = Paginator(vacancy, page=page)
        vacancy_page = paginator.get_page()[0]
        pagination_button = pages(paginator)
        vacancy_id = vacancy_page.id

        text = f"{vacancy_page.name}"
    else:
        text = connector[lang]['message']['menu'][view]

    button = get_vacancy_button(
        lang=lang,
        view=view,
        level=level,
        key=key,
        page=page,
        catalog_id=catalog_id,
        subcatalog_id=subcatalog_id,
        pagination_button=pagination_button,
        vacancy_id=vacancy_id,
    )

    return text, button


async def shaping_description(
        session: AsyncSession,
        lang: str,
        user_id: int,
        view: str,
        level: int,
        key: str,
        page: int,
        catalog_id: int,
        subcatalog_id: int,
        vacancy_id: int,
        liked_id: int | None = None,
        complaint_id: int | None = None,
        your_vacancy: bool | None = None,
):
    if view == 'all' or view == 'liked' or view == 'complaint':
        vacancy = await get_vacancy_one(
            session=session,
            vacancy_id=vacancy_id,
        )

        if view == 'all':
            preview = await get_preview_one(session=session, user_id=user_id, vacancy_id=vacancy_id)

            your_vacancy = await get_vacancy_one(
                session=session,
                vacancy_id=vacancy_id,
                user_id=user_id,
            )

            if not preview and not your_vacancy:
                await create_preview(session=session, user_id=user_id, vacancy_id=vacancy_id)

        liked = await get_liked_one(
            session=session,
            user_id=user_id,
            vacancy_id=vacancy_id,
        )
        complaint = await get_complaint_one(
            session=session,
            user_id=user_id,
            vacancy_id=vacancy_id,
        )

        liked_id = liked.id if liked else None
        complaint_id = complaint.id if complaint else None
    else:
        vacancy = await get_vacancy_one(
            session=session,
            vacancy_id=vacancy_id,
            user_id=user_id,
        )

    text = f"{vacancy.name}\n\n{vacancy.description}\n\n{vacancy.salary}"
    button = get_description_button(
        lang=lang,
        view=view,
        level=level,
        key=key,
        page=page,
        catalog_id=catalog_id,
        subcatalog_id=subcatalog_id,
        vacancy_id=vacancy_id,
        liked_id=liked_id,
        complaint_id=complaint_id,
        your_vacancy=True if your_vacancy else False,
        deactivate=vacancy.active,
    )

    return text, button


async def shaping_confirm(
        lang: str,
        method: str,
        view: str,
        key: str,
        page: int,
        catalog_id: int,
        subcatalog_id: int,
        vacancy_id: int,
):
    if key == 'confirm_user':
        text = connector[lang]['message'][key][method]
    else:
        text = connector[lang]['message'][key][method]

    button = get_confirm_button(
        lang=lang,
        method=method,
        view=view,
        key=key,
        page=page,
        catalog_id=catalog_id,
        subcatalog_id=subcatalog_id,
        vacancy_id=vacancy_id,
    )

    return text, button


async def shaping_profile(
        lang: str,
        level: int,
        key: str,
):

    text = connector[lang]['message']['menu'][key]
    button = get_profile_button(
        lang=lang,
        level=level,
    )

    return text, button


async def shaping_setting(
        session: AsyncSession,
        lang: str,
        user_id: int,
        level: int,
):
    user = await search_user(session=session, user_id=user_id)

    text = 'Основные настройки профиля'
    button = get_setting_button(
        lang=lang,
        level=level,
        first_name=user.first_name
    )

    return text, button


async def shaping_about(
        lang: str,
        key: str,
):
    text = connector[lang]['message']['menu'][key]
    button = get_about_button(
        lang=lang,
    )

    return text, button


async def shaping_admin(
        lang: str,
        key: str,
):
    text = connector[lang]['message']['menu'][key]
    button = get_admin_button(
        lang=lang,
    )

    return text, button


async def menu_processing(
        session: AsyncSession,
        lang: str | None = None,
        user_id: int | None = None,
        method: str | None = None,
        view: str | None = None,
        level: int | None = None,
        key: str | None = None,
        page: int | None = None,
        catalog_id: int | None = None,
        subcatalog_id: int | None = None,
        vacancy_id: int | None = None,
):
    if level == 0:
        return await shaping_menu(session, lang, user_id, level, key)
    elif level == 1:
        return await shaping_catalog(session, lang, level, key)
    elif level == 2:
        return await shaping_subcatalog(session, lang, level, key, catalog_id)
    elif level == 3:
        return await shaping_vacancy(session, lang, user_id, view, level, key, page, catalog_id, subcatalog_id)
    elif level == 4:
        return await shaping_description(session, lang, user_id, view, level, key, page, catalog_id, subcatalog_id, vacancy_id)

    elif level == 10:
        return await shaping_confirm(lang, method, view, key, page, catalog_id, subcatalog_id, vacancy_id)

    elif level == 20:
        return await shaping_profile(lang, level, key)
    elif level == 21:
        return await shaping_setting(session, lang, user_id, level)

    elif level == 30:
        return await shaping_about(lang, key)

    elif level == 40:
        return await shaping_admin(lang, key)
