from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from core.filters.menu import IsUserFilter
from core.keyboards.menu import MenuCallBack
from core.database.querys import create_liked, get_liked_one, get_complaint_one, create_complaint, delete_liked, \
    delete_complaint, get_vacancy_one, get_language_user, get_complaint_count
from core.processes.menu import menu_processing


menu_router = Router()
menu_router.message.filter(IsUserFilter())


@menu_router.message(Command(commands='menu'))
async def menu(
        message: Message,
        session: AsyncSession,
        method: str | None = None,
        view: str | None = None,
        level: int | None = None,
        key: str | None = None,
        page: int | None = None,
        catalog_id: int | None = None,
        subcatalog_id: int | None = None,
        vacancy_id: int | None = None,
) -> None:
    lang = await get_language_user(
        session=session,
        user_id=message.from_user.id,
    )

    text, reply_markup = await menu_processing(
        session=session,
        lang=lang.language.abbreviation,
        user_id=message.from_user.id,
        method=method if method else None,
        view=view if view else None,
        level=level if level else 0,
        key=key if key else "menu",
        page=page if page else 1,
        catalog_id=catalog_id if catalog_id else None,
        subcatalog_id=subcatalog_id if subcatalog_id else None,
        vacancy_id=vacancy_id if vacancy_id else None,
    )

    await message.answer(
        text=text,
        reply_markup=reply_markup,
    )


async def favorite(
        callback: CallbackQuery,
        callback_data: MenuCallBack,
        session: AsyncSession,
) -> None:
    vacancy = await get_vacancy_one(
        session=session,
        vacancy_id=callback_data.vacancy_id,
    )

    if vacancy:
        liked = await get_liked_one(
            session=session,
            user_id=callback.from_user.id,
            vacancy_id=callback_data.vacancy_id,
        )

        if liked:
            await delete_liked(
                session=session,
                user_id=callback.from_user.id,
                vacancy_id=callback_data.vacancy_id,
            )
            await callback.answer(
                text="Вакансия убрана из избранного!.",
            )
        else:
            await create_liked(
                session=session,
                user_id=callback.from_user.id,
                vacancy_id=callback_data.vacancy_id,
            )
            await callback.answer(
                text="Вакансия добавлена в избранное!.",
            )


async def complaint(
        callback: CallbackQuery,
        callback_data: MenuCallBack,
        session: AsyncSession,
) -> None:
    vacancy = await get_vacancy_one(
        session=session,
        vacancy_id=callback_data.vacancy_id,
    )

    if vacancy:
        feedback = await get_complaint_one(
            session=session,
            user_id=callback.from_user.id,
            vacancy_id=callback_data.vacancy_id,
        )

        if feedback:
            await delete_complaint(
                session=session,
                user_id=callback.from_user.id,
                vacancy_id=callback_data.vacancy_id,
            )
            await callback.answer(
                text="Вы убрали жалобу!.",
            )
        else:
            await create_complaint(
                session=session,
                user_id=callback.from_user.id,
                vacancy_id=callback_data.vacancy_id,
            )

            if await get_complaint_count(session=session, vacancy_id=callback_data.vacancy_id) == 5:
                pass

            await callback.answer(
                text="Вы пожаловались!.",
            )


@menu_router.callback_query(
    MenuCallBack.filter(F.key != 'vacancy'),
    MenuCallBack.filter(F.key != 'change'),
    MenuCallBack.filter(F.key != 'moderation'),
)
async def redirector(
        callback: CallbackQuery,
        callback_data: MenuCallBack,
        session: AsyncSession,
        view: str | None = None,
        level: int | None = None,
        key: str | None = None,
        page: int | None = None,
        catalog_id: int | None = None,
        subcatalog_id: int | None = None,
        vacancy_id: int | None = None,
) -> None:
    if callback_data.method == "favorite":
        await favorite(
            callback=callback,
            callback_data=callback_data,
            session=session,
        )

    if callback_data.method == "feedback":
        await complaint(
            callback=callback,
            callback_data=callback_data,
            session=session,
        )

    lang = await get_language_user(
        session=session,
        user_id=callback.from_user.id
    )

    text, reply_markup = await menu_processing(
        session=session,
        lang=lang.language.abbreviation,
        user_id=callback.from_user.id,
        method=callback_data.method,
        view=view if view else callback_data.view,
        level=level if level else callback_data.level,
        key=key if key else callback_data.key,
        page=page if page else callback_data.page,
        catalog_id=catalog_id if catalog_id else callback_data.catalog_id,
        subcatalog_id=subcatalog_id if subcatalog_id else callback_data.subcatalog_id,
        vacancy_id=vacancy_id if vacancy_id else callback_data.vacancy_id,
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=reply_markup,
    )
    await callback.answer()
