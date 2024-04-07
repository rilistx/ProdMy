from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from core.filters.contact import IsContactFilter
from core.handlers.menu import menu
from core.keyboards.registration import get_contact_button
from core.models.querys import search_user, create_username, create_user, get_language_one, get_language_id, \
    get_country_id
from core.states.registration import StateRegistration
from core.utils.connector import connector


registration_router = Router()


@registration_router.message(CommandStart())
async def start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user_exist = await search_user(session, message.from_user.id)
    if user_exist:
        lang = await get_language_one(session, user_exist.language_id)
        await message.answer(text=connector[lang.abbreviation]['message']['authorized'])
        await state.clear()

        return await menu(message=message, session=session)

    await message.answer(
        text=connector['uk']['start_message'],
        reply_markup=get_contact_button('uk'),
    )

    await state.set_state(StateRegistration.PHONE)


@registration_router.message(StateRegistration.PHONE, IsContactFilter())
async def contact(message: Message, state: FSMContext, session: AsyncSession) -> None:
    language_id = await get_language_id(session, 'uk')
    country_id = await get_country_id(session, 'ukraine')

    await create_user(
        session,
        user_id=message.from_user.id,
        uuid=await create_username(session),
        first_name=message.contact.first_name if message.contact.first_name else None,
        phone_number=message.contact.phone_number,
        language_id=language_id,
        country_id=country_id,
    )

    await message.answer(
        text=connector['uk']['message']['contact'],
        reply_markup=ReplyKeyboardRemove()
    )

    await state.clear()
    return await menu(message=message, session=session)


@registration_router.message(StateRegistration.PHONE)
async def error_contact(message: Message) -> None:
    await message.delete()
