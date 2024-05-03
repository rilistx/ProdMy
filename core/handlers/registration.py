from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from core.filters.registration import IsContactFilter
from core.handlers.menu import menu
from core.keyboards.registration import get_contact_button, get_support_button, get_channel_button
from core.database.querys import search_user, get_language_one, get_currency_one, get_country_one, create_user
from core.states.registration import StateRegistration
from core.utils.connector import connector
from core.utils.message import get_message_registration_start, get_text_registration_contact, \
    get_text_registration_support, get_text_registration_channel
from core.utils.phone import format_phone_number
from core.utils.settings import default_language, default_currency, default_country
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

    lang = message.from_user.language_code if message.from_user.language_code in connector.keys() else default_language

    await state.update_data({
        'lang': lang,
    })

    text = await get_message_registration_start(lang=lang)
    reply_markup = get_contact_button(lang=lang)

    await message.answer(
        text=text,
        reply_markup=reply_markup,
    )
    await state.set_state(StateRegistration.PHONE)


@registration_router.message(StateRegistration.PHONE, IsContactFilter())
async def contact(message: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = (await state.get_data())['lang']

    language = await get_language_one(session=session, language_abbreviation=lang)
    currency = await get_currency_one(session=session, currency_abbreviation=default_currency)
    country = await get_country_one(session=session, country_name=default_country)

    await create_user(
        session=session,
        user_id=message.from_user.id,
        username=await create_username(session=session),
        first_name=message.contact.first_name if message.contact.first_name else None,
        phone_number=format_phone_number(message.contact.phone_number),
        language_id=language.id,
        currency_id=currency.id,
        country_id=country.id,
    )

    success_test = await get_text_registration_contact(lang=lang)
    support_text = await get_text_registration_support(lang=lang)
    channel_text = await get_text_registration_channel(lang=lang)

    reply_markup_success = ReplyKeyboardRemove()
    reply_markup_support = get_support_button(lang=lang)
    reply_markup_channel = get_channel_button(lang=lang)

    await message.answer(
        text=success_test,
        reply_markup=reply_markup_success,
    )

    await message.answer(
        text=support_text,
        reply_markup=reply_markup_support,
    )

    await message.answer(
        text=channel_text,
        reply_markup=reply_markup_channel,
    )

    await state.clear()

    return await menu(
        message=message,
        session=session,
    )


@registration_router.message(StateRegistration.PHONE)
async def error(message: Message) -> None:
    await message.delete()
