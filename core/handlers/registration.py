from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from core.commands.languages import json
from core.filters.registration import IsLanguageFilter, IsContactFilter
from core.handlers.menu import menu
from core.keyboards import delete, registration
from core.models.querys import search_user, create_user, create_username, get_language_id, get_country_id
from core.states.registration import StateRegistration


registration_router = Router()


@registration_router.message(CommandStart())
async def start(message: Message, state: FSMContext, session: AsyncSession):
    user_exist = await search_user(session, message.from_user.id)
    if user_exist:
        await message.answer('Оффф!!! Вы уже зарегестрированы!')
        await state.clear()
        return await menu(message=message, session=session)

    language_list = []
    for key, value in json['ua']['language'].items():
        text = value['flag'] + ' ' + value['name']
        language_list.append(text)

    await message.answer(
        text=json['ua']['message']['start_msg'],
        reply_markup=registration.get_language_button(lang=language_list),
    )

    await state.set_state(StateRegistration.LANGUAGE)


@registration_router.message(StateRegistration.LANGUAGE, IsLanguageFilter())
async def language(message: Message, state: FSMContext):
    lang = 'ua'

    for name, info in json['ua']['language'].items():
        if info['name'] == message.text.split(' ')[-1]:
            lang = name

    await state.update_data(language=lang)

    await message.answer(text=json[lang]['message']['language_msg'], reply_markup=registration.get_contact_button(lang))

    await state.set_state(StateRegistration.PHONE)


@registration_router.message(StateRegistration.LANGUAGE)
async def error_language(message: Message) -> None:
    await message.answer('Ошибка: Такого языка не существует!')


@registration_router.message(StateRegistration.PHONE, IsContactFilter())
async def contact(message: Message, state: FSMContext, session: AsyncSession):
    lang = await state.get_data()

    language_id = await get_language_id(session, lang['language'])
    country_id = await get_country_id(session, lang['language'])

    await create_user(
        session,
        user_id=message.from_user.id,
        uuid=await create_username(session),
        first_name=message.contact.first_name if message.contact else None,
        phone_number=message.contact.phone_number if message.contact else message.text,
        language_id=language_id,
        country_id=country_id,
    )

    await message.answer('Ура!!! Поздравляем вас с успешной регестрацией!', reply_markup=delete.delete_keyboard())
    await state.clear()
    return await menu(message=message, session=session)


@registration_router.message(StateRegistration.PHONE)
async def error_contact(message: Message) -> None:
    await message.answer('Ошибка: Номер не является действителен!')
