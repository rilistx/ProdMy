from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from core.filters.menu import IsUserFilter
from core.keyboards.menu import MenuCallBack
from core.models.querys import get_language_one, get_user_one, create_liked, get_liked_one, delete_liked_one, \
    get_complaint_one, delete_complaint_one, create_complaint
from core.processes.menu import menu_processing


menu_router = Router()
menu_router.message.filter(IsUserFilter())


@menu_router.message(Command(commands='menu'))
async def menu(message: Message, session: AsyncSession, level=None, method=None, key=None) -> None:
    user = await get_user_one(session, message.from_user.id)
    lang = await get_language_one(session, language_id=user.language_id)

    text, reply_markup = await menu_processing(
        session=session, lang=lang.abbreviation, level=level if level else 0, method=method, key=key if key else "menu",
    )

    await message.answer(text=text, reply_markup=reply_markup)


async def favorite(callback: CallbackQuery, callback_data: MenuCallBack, session: AsyncSession) -> None:
    liked = await get_liked_one(session, user_id=callback.from_user.id, vacancy_id=callback_data.vacancy_id)

    if liked:
        await delete_liked_one(session, user_id=callback.from_user.id, vacancy_id=callback_data.vacancy_id)
        await callback.answer("Вакансия убрана из избранного!.")
    else:
        await create_liked(session=session, user_id=callback.from_user.id, vacancy_id=callback_data.vacancy_id)
        await callback.answer("Вакансия добавлена в избранное!.")


async def complaint(callback: CallbackQuery, callback_data: MenuCallBack, session: AsyncSession) -> None:
    feedback = await get_complaint_one(session, user_id=callback.from_user.id, vacancy_id=callback_data.vacancy_id)

    if feedback:
        await delete_complaint_one(session, user_id=callback.from_user.id, vacancy_id=callback_data.vacancy_id)
        await callback.answer("Вы убрали жалобу!.")
    else:
        await create_complaint(session=session, user_id=callback.from_user.id, vacancy_id=callback_data.vacancy_id)
        await callback.answer("Вы пожаловались!.")


@menu_router.callback_query(MenuCallBack.filter(F.key != 'vacancy'))
async def redirector(callback: CallbackQuery, callback_data: MenuCallBack, session: AsyncSession) -> None:
    user = await get_user_one(session, callback.from_user.id)
    lang = await get_language_one(session, language_id=user.language_id)

    if callback_data.method == "favorite":
        await favorite(callback=callback, callback_data=callback_data, session=session)

    if callback_data.method == "feedback":
        await complaint(callback=callback, callback_data=callback_data, session=session)

    text, reply_markup = await menu_processing(
        session=session,
        lang=lang.abbreviation,
        user_id=callback.from_user.id,
        method=None,
        level=callback_data.level,
        key=callback_data.key,
        catalog_id=callback_data.catalog_id,
        subcatalog_id=callback_data.subcatalog_id,
        page=callback_data.page,
        vacancy_id=callback_data.vacancy_id,
        liked_id=callback_data.liked_id,
        complaint_id=callback_data.complaint_id,
    )

    await callback.message.edit_text(text=text, reply_markup=reply_markup)
    await callback.answer()
