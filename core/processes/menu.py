from sqlalchemy.ext.asyncio import AsyncSession

from core.keyboards.menu import get_menu_button, get_vacancy_button, get_description_button, get_profession_button, \
    get_profile_button, get_confirm_button, get_settings_button, get_about_button, get_admin_button, get_donate_button
from core.database.querys import get_catalog_all, get_catalog_one, get_subcatalog_all, get_vacancy_all_active, \
    get_vacancy_one, get_vacancy_user, get_vacancy_favorite, get_liked_one, get_complaint_one, search_user, \
    get_preview_one, create_preview, get_vacancy_admin, get_complaint_count
from core.utils.message import get_text_vacancy_show, get_text_about_info, get_text_about_donate, \
    get_text_menu_main, get_text_menu_catalog, get_text_menu_subcatalog, get_text_vacancy_none, \
    get_text_profile_info, get_text_profile_settings, get_text_menu_admin, get_text_menu_confirm
from core.utils.paginator import Paginator
from core.utils.settings import complaint_limit


def pages(
        *,
        paginator: Paginator,
):
    button = dict()
    if paginator.has_previous():
        button["◀️"] = "previous"

    if paginator.has_next():
        button["▶️"] = "next"

    return button


async def shaping_menu(
        session: AsyncSession,
        lang: str,
        user_id: int,
        level: int,
):
    user = await search_user(
        session=session,
        user_id=user_id,
    )

    text = await get_text_menu_main(
        lang=lang,
        blocked=user.blocked,
    )
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
):
    catalog = await get_catalog_all(
        session=session,
    )

    text = await get_text_menu_catalog(
        lang=lang,
    )
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

    text = await get_text_menu_subcatalog(
        lang=lang,
    )
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
        all_vacancy = await get_vacancy_admin(
            session=session,
            complaint_limit=complaint_limit,
        )
    elif view == 'all':
        all_vacancy = await get_vacancy_all_active(
            session=session,
            subcatalog_id=subcatalog_id,
            complaint_limit=complaint_limit,
        )
    elif view == 'your':
        all_vacancy = await get_vacancy_user(
            session=session,
            user_id=user_id,
        )
    else:
        all_vacancy = await get_vacancy_favorite(
            session=session,
            user_id=user_id,
            complaint_limit=complaint_limit,
        )

    pagination_button = {}

    if all_vacancy:
        paginator = Paginator(
            array=all_vacancy,
            page=page,
        )
        vacancy = paginator.get_page()[0]
        pagination_button = pages(
            paginator=paginator,
        )
        vacancy_id = vacancy.id

        complaint_count = await get_complaint_count(
            session=session,
            vacancy_id=vacancy_id,
        )

        text = await get_text_vacancy_show(
            session=session,
            lang=lang,
            vacancy_id=vacancy_id,
            preview='partial',
            complaint=True if complaint_count.complaint_count == complaint_limit else False,
        )
    else:
        text = await get_text_vacancy_none(
            lang=lang,
            view=view,
        )

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
        liked: bool = False,
        complaint: bool = False,
):
    if view == 'all' or view == 'liked' or view == 'complaint':
        vacancy = await get_vacancy_one(
            session=session,
            vacancy_id=vacancy_id,
        )

        if view == 'all':
            preview = await get_preview_one(
                session=session,
                user_id=user_id,
                vacancy_id=vacancy_id,
            )

            if not preview and vacancy.user_id != user_id:
                await create_preview(
                    session=session,
                    user_id=user_id,
                    vacancy_id=vacancy_id,
                )

        liked: bool = await get_liked_one(
            session=session,
            user_id=user_id,
            vacancy_id=vacancy_id,
        )
        complaint: bool = await get_complaint_one(
            session=session,
            user_id=user_id,
            vacancy_id=vacancy_id,
        )
    else:
        vacancy = await get_vacancy_one(
            session=session,
            vacancy_id=vacancy_id,
            user_id=user_id,
        )

    complaint_count = await get_complaint_count(
        session=session,
        vacancy_id=vacancy_id,
    )

    text = await get_text_vacancy_show(
        session=session,
        lang=lang,
        vacancy_id=vacancy_id,
        preview='full',
        complaint=True if complaint_count.complaint_count == complaint_limit else False,
    )
    button = get_description_button(
        lang=lang,
        view=view,
        level=level,
        key=key,
        page=page,
        catalog_id=catalog_id,
        subcatalog_id=subcatalog_id,
        vacancy_id=vacancy_id,
        liked=liked,
        complaint=complaint,
        active=vacancy.active,
        your_vacancy=True if vacancy.user_id == user_id else False,
        blocked_vacancy=True if complaint_count.complaint_count == complaint_limit else False,
    )

    return text, button


async def shaping_confirm(
        session: AsyncSession,
        lang: str,
        user_id: int,
        method: str,
        view: str,
        level: int,
        key: str,
        page: int,
        catalog_id: int,
        subcatalog_id: int,
        vacancy_id: int,
        first_name: bool = True,
):
    if key == 'confirm_user':
        user = await search_user(
            session=session,
            user_id=user_id,
        )

        if method == 'create' and not user.first_name:
            first_name = False
            method = 'error'

        text = await get_text_menu_confirm(
            lang=lang,
            func_name=key,
            method=method,
            first_name=True if user.first_name else False,
        )
    else:
        text = await get_text_menu_confirm(
            lang=lang,
            func_name=key,
            method=method,
        )

    button = get_confirm_button(
        lang=lang,
        method=method,
        view=view,
        level=level,
        key=key,
        page=page,
        first_name=first_name,
        catalog_id=catalog_id,
        subcatalog_id=subcatalog_id,
        vacancy_id=vacancy_id,
    )

    return text, button


async def shaping_profile(
        session: AsyncSession,
        lang: str,
        user_id: int,
        level: int,
):
    text = await get_text_profile_info(
        session=session,
        lang=lang,
        user_id=user_id,
    )
    button = get_profile_button(
        lang=lang,
        level=level,
    )

    return text, button


async def shaping_settings(
        session: AsyncSession,
        lang: str,
        user_id: int,
        level: int,
):
    user = await search_user(
        session=session,
        user_id=user_id,
    )

    text = await get_text_profile_settings(
        lang=lang,
    )
    button = get_settings_button(
        lang=lang,
        level=level,
        first_name=True if user.first_name else False,
    )

    return text, button


async def shaping_about(
        lang: str,
):
    text = await get_text_about_info(
        lang=lang,
    )
    button = get_about_button(
        lang=lang,
    )

    return text, button


async def shaping_donate(
        lang: str,
        level: int,
):
    text = await get_text_about_donate(
        lang=lang,
    )
    button = get_donate_button(
        lang=lang,
        level=level,
    )

    return text, button


async def shaping_admin(
        lang: str,
):
    text = await get_text_menu_admin(
        lang=lang,
    )
    button = get_admin_button(
        lang=lang,
    )

    return text, button


async def menu_processing(
        *,
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
        return await shaping_menu(session, lang, user_id, level)
    elif level == 1:
        return await shaping_catalog(session, lang, level)
    elif level == 2:
        return await shaping_subcatalog(session, lang, level, catalog_id)
    elif level == 3:
        return await shaping_vacancy(session, lang, user_id, view, level, key, page, catalog_id, subcatalog_id)
    elif level == 4:
        return await shaping_description(session, lang, user_id, view, level, key, page, catalog_id, subcatalog_id, vacancy_id)

    elif level == 10:
        return await shaping_confirm(session, lang, user_id, method, view, level, key, page, catalog_id, subcatalog_id, vacancy_id)

    elif level == 20:
        return await shaping_profile(session, lang, user_id, level)
    elif level == 21:
        return await shaping_settings(session, lang, user_id, level)

    elif level == 30:
        return await shaping_about(lang)
    elif level == 31:
        return await shaping_donate(lang, level)

    elif level == 40:
        return await shaping_admin(lang)
