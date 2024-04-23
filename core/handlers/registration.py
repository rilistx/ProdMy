from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from core.filters.registration import IsContactFilter
from core.handlers.menu import menu
from core.keyboards.registration import get_contact_button
from core.database.querys import search_user, get_language_one, get_currency_one, get_country_one, create_user
from core.states.registration import StateRegistration
from core.utils.connector import connector
from core.utils.username import create_username


registration_router = Router()


@registration_router.message(CommandStart())
async def start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user_exist = await search_user(
        session=session,
        user_id=message.from_user.id,
    )

    if user_exist:
        await message.delete()
        await state.clear()

        return await menu(
            message=message,
            session=session,
        )

    lang = message.from_user.language_code if message.from_user.language_code in connector.keys() else 'uk'

    await state.update_data({
        'lang': lang,
    })

    await message.answer(
        text=connector[lang]['start_message'],
        reply_markup=get_contact_button(lang),
    )
    await state.set_state(StateRegistration.PHONE)


@registration_router.message(StateRegistration.PHONE, IsContactFilter())
async def contact(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()

    lang = await get_language_one(
        session=session,
        language_abbreviation=state_data['lang'],
    )
    currency = await get_currency_one(
        session=session,
        currency_abbreviation='UAH',
    )
    country = await get_country_one(
        session=session,
        country_name=state_data['lang'],
    )

    await create_user(
        session=session,
        user_id=message.from_user.id,
        username=await create_username(session=session),
        first_name=message.contact.first_name if message.contact.first_name else None,
        phone_number=message.contact.phone_number,
        language_id=lang.id,
        currency_id=currency.id,
        country_id=country.id,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['start']['contact'],
        reply_markup=ReplyKeyboardRemove(),
    )

    await state.clear()

    return await menu(
        message=message,
        session=session,
    )


@registration_router.message(StateRegistration.PHONE)
async def error(message: Message) -> None:
    await message.delete()
