from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from core.filters.user import IsUserFilter
from core.keyboards.menu import MenuCallBack
from core.models.querys import get_language_one, get_user_one
from core.processes.menu import menu_processing


menu_router = Router()


@menu_router.message(Command(commands='menu'), IsUserFilter())
async def menu(message: Message, session: AsyncSession):
    user = await get_user_one(session, message.from_user.id)
    language = await get_language_one(session, user.language_id)
    text, reply_markup = await menu_processing(session, lang=language, level=0, name="menu")

    await message.answer(text=text, reply_markup=reply_markup)


@menu_router.callback_query(MenuCallBack.filter(), IsUserFilter())
async def redirector(callback: CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    user = await get_user_one(session, callback.from_user.id)
    language = await get_language_one(session, user.language_id)

    text, reply_markup = await menu_processing(
        session,
        lang=language,
        level=callback_data.level,
        name=callback_data.name,
        catalog_id=callback_data.catalog_id,
        subcatalog_id=callback_data.subcatalog_id,
    )

    await callback.message.edit_text(text=text, reply_markup=reply_markup)
    await callback.answer()
