from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from core.filters.vacancy import CatalogFilter, SubcatalogFilter, ChoiceFilter, PriceFilter, RegionFilter, CityFilter
from core.handlers.menu import menu
from core.keyboards.vacancy import vacancy_profession_button, vacancy_keyboard_button, vacancy_location_button, \
    vacancy_choice_button
from core.models.querys import get_catalog_all, get_subcatalog_all, get_catalog_one, get_subcatalog_one, \
    get_country_first, get_region_all, get_region_one, get_city_all, get_city_one, get_currency_first, create_vacancy
from core.states.vacancy import StateVacancy
from core.utils.connector import connector


vacancy_router = Router()


@vacancy_router.callback_query(F.data.startswith('vacancy_'))
async def catalog_vacancy(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.delete()

    lang = callback.data.split('_')[-1]
    catalog = await get_catalog_all(session)

    reply_markup = vacancy_profession_button(lang, 'catalog', catalog)

    await callback.message.answer(text='Давай выберем направление твоей работы:', reply_markup=reply_markup)
    await callback.answer()

    await state.set_state(StateVacancy.CATALOG)


@vacancy_router.message(StateVacancy.CATALOG, CatalogFilter())
async def subcatalog_vacancy(message: Message, state: FSMContext, session: AsyncSession, lang):
    catalog_logo = message.text.split(' ')[0]
    catalog = await get_catalog_one(session=session, catalog_logo=catalog_logo)
    currency = await get_currency_first(session)

    await state.update_data({'catalog_id': catalog.id, 'catalog_title': catalog.title, 'currency_id': currency.id})

    subcatalog = await get_subcatalog_all(session, catalog.id)
    reply_markup = vacancy_profession_button(lang, 'subcatalog', subcatalog, catalog.title)

    await message.answer(text='Давай выберем тип твоей работы:', reply_markup=reply_markup)
    await state.set_state(StateVacancy.SUBCATALOG)


@vacancy_router.message(StateVacancy.CATALOG)
async def error_catalog(message: Message) -> None:
    await message.delete()


@vacancy_router.message(StateVacancy.SUBCATALOG, SubcatalogFilter())
async def name_vacancy(message: Message, state: FSMContext, session: AsyncSession, lang):
    catalog = await state.get_data()
    subcatalog_name = ''

    for key, value in connector[lang]['catalog'][catalog['catalog_title']]['subcatalog'].items():
        if value == message.text:
            subcatalog_name = key
            break

    subcatalog = await get_subcatalog_one(session, catalog['catalog_id'], subcatalog_name)
    reply_markup = vacancy_keyboard_button(lang)

    await state.update_data({'subcatalog_id': subcatalog.id})

    await message.answer(text='Дай название своей вакансии', reply_markup=reply_markup)
    await state.set_state(StateVacancy.NAME)


@vacancy_router.message(StateVacancy.SUBCATALOG)
async def error_subcatalog(message: Message) -> None:
    await message.delete()


@vacancy_router.message(StateVacancy.NAME)
async def description_vacancy(message: Message, state: FSMContext, lang):
    await state.update_data({'name': message.text})

    reply_markup = vacancy_keyboard_button(lang)

    await message.answer(text='Опиши свою вакансию: ', reply_markup=reply_markup)
    await state.set_state(StateVacancy.DESCRIPTION)


@vacancy_router.message(StateVacancy.DESCRIPTION)
async def remote_vacancy(message: Message, state: FSMContext, lang):
    await state.update_data({'description': message.text})

    reply_markup = vacancy_choice_button(lang)

    await message.answer(text='Возможность работать удалённо', reply_markup=reply_markup)
    await state.set_state(StateVacancy.REMOTE)


@vacancy_router.message(StateVacancy.REMOTE, ChoiceFilter())
async def disability_vacancy(message: Message, state: FSMContext, lang):
    await state.update_data({'remote': True if message.text.split(' ')[0] == '✅' else False})

    reply_markup = vacancy_choice_button(lang)

    await message.answer(text='Возможность работать инвалиду', reply_markup=reply_markup)
    await state.set_state(StateVacancy.DISABILITY)


@vacancy_router.message(StateVacancy.REMOTE)
async def error_remote(message: Message) -> None:
    await message.delete()


@vacancy_router.message(StateVacancy.DISABILITY, ChoiceFilter())
async def price_vacancy(message: Message, state: FSMContext, lang):
    await state.update_data({'disability': True if message.text.split(' ')[0] == '✅' else False})

    reply_markup = vacancy_keyboard_button(lang)

    await message.answer(text='Какова ваша зарплата:', reply_markup=reply_markup)
    await state.set_state(StateVacancy.PRICE)


@vacancy_router.message(StateVacancy.DISABILITY)
async def error_disability(message: Message) -> None:
    await message.delete()


@vacancy_router.message(StateVacancy.PRICE, PriceFilter())
async def region_vacancy(message: Message, state: FSMContext, session: AsyncSession, lang):
    await state.update_data({'price': int(message.text)})

    country = await get_country_first(session)
    region = await get_region_all(session)
    reply_markup = vacancy_location_button(lang, country.name, 'region', region)

    await message.answer(text='Выберете свой регион: ', reply_markup=reply_markup)
    await state.set_state(StateVacancy.REGION)


@vacancy_router.message(StateVacancy.PRICE)
async def error_price(message: Message) -> None:
    await message.delete()


@vacancy_router.message(StateVacancy.REGION, RegionFilter())
async def city_vacancy(message: Message, state: FSMContext, session: AsyncSession, lang):
    country = await get_country_first(session)
    region_name = ''

    for key, value in connector[lang]['country'][country.name]['region'].items():
        if value['name'] == message.text:
            region_name = key
            break

    region = await get_region_one(session=session, region_name=region_name)

    await state.update_data({'country_id': country.id, 'region_id': region.id})

    city = await get_city_all(session, region.id)
    reply_markup = vacancy_location_button(lang, country.name, 'city', city, region_name)

    await message.answer(text='Выберете свой город: ', reply_markup=reply_markup)
    await state.set_state(StateVacancy.CITY)


@vacancy_router.message(StateVacancy.REGION)
async def error_region(message: Message) -> None:
    await message.delete()


@vacancy_router.message(StateVacancy.CITY, CityFilter())
async def finish_vacancy(message: Message, state: FSMContext, session: AsyncSession, lang):
    if message.text == connector[lang]['button']['skip']:
        await state.update_data({'city_id': None})
    else:
        country = await get_country_first(session)
        region_data = await state.get_data()
        region = await get_region_one(session=session, region_id=region_data['region_id'])
        city_name = ''
        for key, value in connector[lang]['country'][country.name]['region'][region.name]['city'].items():
            if value == message.text:
                city_name = key
                break

        city = await get_city_one(session, region.id, city_name)

        await state.update_data({'city_id': city.id})

    vacancy = await state.get_data()

    await create_vacancy(
        session,
        name=vacancy['name'],
        description=vacancy['description'],
        remote=vacancy['remote'],
        disability=vacancy['disability'],
        price=vacancy['price'],
        currency_id=vacancy['currency_id'],
        subcatalog_id=vacancy['subcatalog_id'],
        country_id=vacancy['country_id'],
        region_id=vacancy['region_id'],
        city_id=vacancy['city_id'],
        user_id=message.from_user.id,
    )

    await message.answer(text='THE END', reply_markup=ReplyKeyboardRemove())
    await state.clear()
    return await menu(message=message, session=session)


@vacancy_router.message(StateVacancy.CITY)
async def error_city(message: Message) -> None:
    await message.delete()
