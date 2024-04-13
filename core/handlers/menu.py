from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from core.filters.menu import IsUserFilter
from core.keyboards.menu import MenuCallBack
from core.models.querys import get_language_one, get_user_one
from core.processes.menu import menu_processing


menu_router = Router()
menu_router.message.filter(IsUserFilter())


@menu_router.message(Command(commands='menu'))
async def menu(message: Message, session: AsyncSession, level=None, key=None) -> None:
    user = await get_user_one(session, message.from_user.id)
    lang = await get_language_one(session, language_id=user.language_id)
    text, reply_markup = await menu_processing(
        session=session, lang=lang.abbreviation, level=level if level else 0, key=key if key else "menu"
    )

    await message.answer(text=text, reply_markup=reply_markup)


@menu_router.callback_query(MenuCallBack.filter(F.key != 'vacancy'))
async def redirector(callback: CallbackQuery, callback_data: MenuCallBack, session: AsyncSession) -> None:
    user = await get_user_one(session, callback.from_user.id)
    lang = await get_language_one(session, language_id=user.language_id)

    text, reply_markup = await menu_processing(
        session=session,
        lang=lang.abbreviation,
        level=callback_data.level,
        key=callback_data.key,
        catalog_id=callback_data.catalog_id,
        subcatalog_id=callback_data.subcatalog_id,
        page=callback_data.page,
        vacancy_id=callback_data.vacancy_id,
    )

    await callback.message.edit_text(text=text, reply_markup=reply_markup)
    await callback.answer()
