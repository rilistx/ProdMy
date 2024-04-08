from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from core.filters.contact import IsContactFilter
from core.handlers.menu import menu
from core.keyboards.registration import get_contact_button
from core.models.querys import search_user, create_username, create_user, get_language_one, get_language_id, \
    get_country_id, get_country_one
from core.states.registration import StateRegistration
from core.utils.connector import connector


registration_router = Router()


@registration_router.message(CommandStart())
async def start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user_exist = await search_user(session, message.from_user.id)

    if user_exist:
        lang = await get_language_one(session, language_id=user_exist.language_id)
        await message.answer(text=connector[lang.abbreviation]['message']['authorized'])
        await state.clear()

        return await menu(message=message, session=session)

    lang = message.from_user.language_code if message.from_user.language_code in connector.keys() else 'uk'
    await state.update_data(lang=lang)

    await message.answer(text=connector[lang]['start_message'], reply_markup=get_contact_button(lang))
    await state.set_state(StateRegistration.PHONE)


@registration_router.message(StateRegistration.PHONE, IsContactFilter())
async def contact(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()

    language = await get_language_one(session, language_abbreviation=state_data['lang'])
    country = await get_country_one(session, country_name=state_data['lang'])

    await create_user(
        session,
        user_id=message.from_user.id,
        uuid=await create_username(session),
        first_name=message.contact.first_name if message.contact.first_name else None,
        phone_number=message.contact.phone_number,
        language_id=language.id,
        country_id=country.id,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['contact'],
        reply_markup=ReplyKeyboardRemove()
    )

    await state.clear()
    return await menu(message=message, session=session)


@registration_router.message(StateRegistration.PHONE)
async def error_contact(message: Message) -> None:
    await message.delete()
