from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from core.filters.vacancy import CatalogFilter, SubcatalogFilter, NameFilter, ChoiceFilter, PriceFilter, RegionFilter, \
    CityFilter, DescriptionFilter, ExitFilter, BackFilter
from core.handlers.menu import menu
from core.keyboards.vacancy import vacancy_profession_button, vacancy_keyboard_button, vacancy_location_button, \
    vacancy_choice_button
from core.models.querys import get_catalog_all, get_subcatalog_all, get_catalog_one, get_subcatalog_one, \
    get_country_first, get_region_all, get_region_one, get_city_all, get_city_one, get_currency_first, create_vacancy
from core.states.vacancy import StateVacancy
from core.utils.connector import connector


vacancy_router = Router()


@vacancy_router.callback_query(F.data.startswith('vacancy_'))
async def catalog_vacancy_callback(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await callback.message.delete()

    state_list = ['catalog_id', 'catalog_title', 'currency_id', 'subcatalog_id', 'name', 'description', 'language',
                  'experience', 'disability', 'price', 'country_id', 'country_name', 'region_id', 'region_name', 'city_id']

    await state.update_data({key: None for key in state_list})

    lang = callback.data.split('_')[-1]
    catalog = await get_catalog_all(session)
    reply_markup = vacancy_profession_button(lang, 'catalog', catalog)

    await callback.message.answer(text=connector[lang]['message']['vacancy']['catalog'], reply_markup=reply_markup)
    await callback.answer()
    await state.set_state(StateVacancy.CATALOG)


@vacancy_router.message(StateFilter("*"), ExitFilter())
async def exit_vacancy(message: Message, state: FSMContext, session: AsyncSession, lang: str) -> None:
    await state.clear()
    await message.answer(text=connector[lang]['message']['vacancy']['exit'])
    return await menu(message=message, session=session, level=6, key='create')


@vacancy_router.message(StateFilter("*"), BackFilter())
async def back_vacancy(message: Message, state: FSMContext, session: AsyncSession, lang: str) -> None:
    current_state = await state.get_state()

    if current_state == StateVacancy.SUBCATALOG:
        await state.update_data({'catalog_id': None, 'catalog_title': None, 'currency_id': None})
        await state.set_state(StateVacancy.CATALOG)
        return await catalog_vacancy_message(message=message, state=state, session=session, lang=lang)
    elif current_state == StateVacancy.NAME:
        await state.update_data({'subcatalog_id': None})
        await state.set_state(StateVacancy.SUBCATALOG)
        return await subcatalog_vacancy(message=message, state=state, session=session, lang=lang)
    elif current_state == StateVacancy.DESCRIPTION:
        await state.update_data({'name': None})
        await state.set_state(StateVacancy.NAME)
        return await name_vacancy(message=message, state=state, session=session, lang=lang)
    elif current_state == StateVacancy.EXPERIENCE:
        await state.update_data({'description': None})
        await state.set_state(StateVacancy.DESCRIPTION)
        return await description_vacancy(message=message, state=state, lang=lang)
    elif current_state == StateVacancy.LANGUAGE:
        await state.update_data({'experience': None})
        await state.set_state(StateVacancy.EXPERIENCE)
        return await experience_vacancy(message=message, state=state, lang=lang)
    elif current_state == StateVacancy.DISABILITY:
        await state.update_data({'language': None})
        await state.set_state(StateVacancy.LANGUAGE)
        return await language_vacancy(message=message, state=state, lang=lang)
    elif current_state == StateVacancy.PRICE:
        await state.update_data({'disability': None})
        await state.set_state(StateVacancy.DISABILITY)
        return await disability_vacancy(message=message, state=state, lang=lang)
    elif current_state == StateVacancy.REGION:
        await state.update_data({'price': None})
        await state.set_state(StateVacancy.PRICE)
        return await price_vacancy(message=message, state=state, lang=lang)
    elif current_state == StateVacancy.CITY:
        await state.update_data({'country_id': None, 'country_name': None, 'region_id': None, 'region_name': None})
        await state.set_state(StateVacancy.REGION)
        return await region_vacancy(message=message, state=state, session=session, lang=lang)


@vacancy_router.message(StateVacancy.CATALOG, CatalogFilter())
async def subcatalog_vacancy(message: Message, state: FSMContext, session: AsyncSession, lang: str) -> None:
    state_data = await state.get_data()

    if not state_data['catalog_id'] and not state_data['catalog_title'] and not state_data['currency_id']:
        catalog_logo = message.text.split(' ')[0]
        catalog = await get_catalog_one(session, catalog_logo=catalog_logo)
        currency = await get_currency_first(session)
        await state.update_data({'catalog_id': catalog.id, 'catalog_title': catalog.title, 'currency_id': currency.id})
        state_data = await state.get_data()

    subcatalog = await get_subcatalog_all(session, state_data['catalog_id'])
    reply_markup = vacancy_profession_button(lang, 'subcatalog', subcatalog, state_data['catalog_title'])

    await message.answer(text=connector[lang]['message']['vacancy']['subcatalog'], reply_markup=reply_markup)
    await state.set_state(StateVacancy.SUBCATALOG)


@vacancy_router.message(StateVacancy.CATALOG)
async def error_catalog(message: Message) -> None:
    await message.delete()


@vacancy_router.message(StateVacancy.SUBCATALOG, SubcatalogFilter())
async def name_vacancy(message: Message, state: FSMContext, session: AsyncSession, lang: str) -> None:
    state_data = await state.get_data()

    if not state_data['subcatalog_id']:
        subcatalog_name = ''
        for key, value in connector[lang]['catalog'][state_data['catalog_title']]['subcatalog'].items():
            if value == message.text:
                subcatalog_name = key
                break

        subcatalog = await get_subcatalog_one(session, subcatalog_name, state_data['catalog_id'])
        await state.update_data({'subcatalog_id': subcatalog.id})

    reply_markup = vacancy_keyboard_button(lang)

    await message.answer(text=connector[lang]['message']['vacancy']['name'], reply_markup=reply_markup)
    await state.set_state(StateVacancy.NAME)


@vacancy_router.message(StateVacancy.SUBCATALOG)
async def error_subcatalog(message: Message) -> None:
    await message.delete()


@vacancy_router.message(StateVacancy.NAME, NameFilter())
async def description_vacancy(message: Message, state: FSMContext, lang: str) -> None:
    state_data = await state.get_data()

    if not state_data['name']:
        await state.update_data({'name': message.text})

    reply_markup = vacancy_keyboard_button(lang)

    await message.answer(text=connector[lang]['message']['vacancy']['description'], reply_markup=reply_markup)
    await state.set_state(StateVacancy.DESCRIPTION)


@vacancy_router.message(StateVacancy.NAME)
async def error_name(message: Message) -> None:
    await message.delete()


@vacancy_router.message(StateVacancy.DESCRIPTION, DescriptionFilter())
async def experience_vacancy(message: Message, state: FSMContext, lang: str) -> None:
    state_data = await state.get_data()

    if not state_data['description']:
        await state.update_data({'description': message.text})

    reply_markup = vacancy_choice_button(lang)

    await message.answer(text=connector[lang]['message']['vacancy']['experience'], reply_markup=reply_markup)
    await state.set_state(StateVacancy.EXPERIENCE)


@vacancy_router.message(StateVacancy.DESCRIPTION)
async def error_description(message: Message) -> None:
    await message.delete()


@vacancy_router.message(StateVacancy.EXPERIENCE, ChoiceFilter())
async def language_vacancy(message: Message, state: FSMContext, lang: str) -> None:
    state_data = await state.get_data()

    if not state_data['experience']:
        await state.update_data({'experience': True if message.text.split(' ')[0] == '✅' else False})

    reply_markup = vacancy_choice_button(lang)

    await message.answer(text=connector[lang]['message']['vacancy']['language'], reply_markup=reply_markup)
    await state.set_state(StateVacancy.LANGUAGE)


@vacancy_router.message(StateVacancy.EXPERIENCE)
async def error_experience(message: Message) -> None:
    await message.delete()


@vacancy_router.message(StateVacancy.LANGUAGE, ChoiceFilter())
async def disability_vacancy(message: Message, state: FSMContext, lang: str) -> None:
    state_data = await state.get_data()

    if not state_data['language']:
        await state.update_data({'language': True if message.text.split(' ')[0] == '✅' else False})

    reply_markup = vacancy_choice_button(lang)

    await message.answer(text=connector[lang]['message']['vacancy']['disability'], reply_markup=reply_markup)
    await state.set_state(StateVacancy.DISABILITY)


@vacancy_router.message(StateVacancy.LANGUAGE)
async def error_language(message: Message) -> None:
    await message.delete()


@vacancy_router.message(StateVacancy.DISABILITY, ChoiceFilter())
async def price_vacancy(message: Message, state: FSMContext, lang: str) -> None:
    state_data = await state.get_data()

    if not state_data['disability']:
        await state.update_data({'disability': True if message.text.split(' ')[0] == '✅' else False})

    reply_markup = vacancy_keyboard_button(lang)

    await message.answer(text=connector[lang]['message']['vacancy']['price'], reply_markup=reply_markup)
    await state.set_state(StateVacancy.PRICE)


@vacancy_router.message(StateVacancy.DISABILITY)
async def error_disability(message: Message) -> None:
    await message.delete()


@vacancy_router.message(StateVacancy.PRICE, PriceFilter())
async def region_vacancy(message: Message, state: FSMContext, session: AsyncSession, lang: str) -> None:
    state_data = await state.get_data()

    if not state_data['price']:
        await state.update_data({'price': int(message.text)})

    country = await get_country_first(session)
    region = await get_region_all(session)

    reply_markup = vacancy_location_button(lang, country.name, 'region', region)

    await message.answer(text=connector[lang]['message']['vacancy']['region'], reply_markup=reply_markup)
    await state.set_state(StateVacancy.REGION)


@vacancy_router.message(StateVacancy.PRICE)
async def error_price(message: Message) -> None:
    await message.delete()


@vacancy_router.message(StateVacancy.REGION, RegionFilter())
async def city_vacancy(message: Message, state: FSMContext, session: AsyncSession, lang: str) -> None:
    state_data = await state.get_data()

    if (not state_data['country_id'] and not state_data['country_name']
            and not state_data['region_id'] and not state_data['region_name']):
        country = await get_country_first(session)
        region_name = ''
        for key, value in connector[lang]['country'][country.name]['region'].items():
            if value['name'] == message.text:
                region_name = key
                break

        region = await get_region_one(session, region_name=region_name)
        await state.update_data({
            'country_id': country.id, 'country_name': country.name, 'region_id': region.id, 'region_name': region.name
        })
        state_data = await state.get_data()

    city = await get_city_all(session, state_data['region_id'])

    reply_markup = vacancy_location_button(lang, state_data['country_name'], 'city', city, state_data['region_name'])

    await message.answer(text=connector[lang]['message']['vacancy']['city'], reply_markup=reply_markup)
    await state.set_state(StateVacancy.CITY)


@vacancy_router.message(StateVacancy.REGION)
async def error_region(message: Message) -> None:
    await message.delete()


@vacancy_router.message(StateVacancy.CITY, CityFilter())
async def finish_vacancy(message: Message, state: FSMContext, session: AsyncSession, lang: str) -> None:
    if message.text != connector[lang]['button']['skip']:
        country = await get_country_first(session)
        region_data = await state.get_data()
        region = await get_region_one(session=session, region_id=region_data['region_id'])
        city_name = ''
        for key, value in connector[lang]['country'][country.name]['region'][region.name]['city'].items():
            if value == message.text:
                city_name = key
                break

        city = await get_city_one(session, city_name, region.id)
        await state.update_data({'city_id': city.id})

    vacancy = await state.get_data()

    await create_vacancy(
        session=session,
        name=vacancy['name'],
        description=vacancy['description'],
        experience=vacancy['experience'],
        language=vacancy['language'],
        disability=vacancy['disability'],
        price=vacancy['price'],
        currency_id=vacancy['currency_id'],
        subcatalog_id=vacancy['subcatalog_id'],
        country_id=vacancy['country_id'],
        region_id=vacancy['region_id'],
        city_id=vacancy['city_id'],
        user_id=message.from_user.id,
    )

    await message.answer(text=connector[lang]['message']['vacancy']['finish'], reply_markup=ReplyKeyboardRemove())
    await state.clear()
    return await menu(message=message, session=session)


@vacancy_router.message(StateVacancy.CITY)
async def error_city(message: Message) -> None:
    await message.delete()


@vacancy_router.message()
async def catalog_vacancy_message(message: Message, state: FSMContext, session: AsyncSession, lang: str) -> None:
    catalog = await get_catalog_all(session)

    reply_markup = vacancy_profession_button(lang, 'catalog', catalog)

    await message.answer(text=connector[lang]['message']['vacancy']['catalog'], reply_markup=reply_markup)
    await state.set_state(StateVacancy.CATALOG)
