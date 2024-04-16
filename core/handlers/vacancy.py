from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from core.filters.vacancy import CatalogFilter, SubcatalogFilter, NameFilter, ChoiceFilter, PriceFilter, RegionFilter, \
    CityFilter, DescriptionFilter, ExitFilter, BackFilter
from core.handlers.menu import menu
from core.keyboards.menu import MenuCallBack
from core.keyboards.vacancy import vacancy_profession_button, vacancy_keyboard_button, vacancy_location_button, vacancy_choice_button
from core.models.querys import get_catalog_all, get_subcatalog_all, get_catalog_one, get_subcatalog_one, \
    get_country_first, get_region_all, get_region_one, get_city_all, get_city_one, get_currency_one, create_vacancy
from core.states.vacancy import StateVacancy
from core.utils.connector import connector


vacancy_router = Router()


@vacancy_router.callback_query(StateFilter(None), MenuCallBack.filter(F.key == 'vacancy' and F.method == 'create'))
async def catalog_vacancy_create_callback(callback: CallbackQuery, callback_data: MenuCallBack, state: FSMContext, session: AsyncSession) -> None:
    await callback.message.delete()

    state_list = ['lang', 'catalog_id', 'catalog_title', 'currency_id', 'subcatalog_id',
                  'name', 'description', 'language', 'experience', 'disability', 'salary',
                  'country_id', 'country_name', 'region_id', 'region_name', 'city_id']

    await state.update_data({key: callback_data.lang if key == 'lang' else None for key in state_list})

    catalog = await get_catalog_all(session)

    reply_markup = vacancy_profession_button(callback_data.lang, 'catalog', catalog)

    await callback.message.answer(text=connector[callback_data.lang]['message']['vacancy']['catalog'], reply_markup=reply_markup)
    await callback.answer()
    await state.set_state(StateVacancy.CATALOG)


@vacancy_router.message(StateFilter("*"), ExitFilter())
async def exit_vacancy(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()

    await state.clear()
    await message.answer(text=connector[state_data['lang']]['message']['vacancy']['exit'])

    return await menu(message=message, session=session, level=20, method='create', key='create')


@vacancy_router.message(StateFilter("*"), BackFilter())
async def back_vacancy(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_state()

    if state_data == StateVacancy.SUBCATALOG:
        await state.update_data({'catalog_id': None, 'catalog_title': None, 'currency_id': None})
        await state.set_state(StateVacancy.CATALOG)
        return await catalog_vacancy_message(message=message, state=state, session=session)
    elif state_data == StateVacancy.NAME:
        await state.update_data({'subcatalog_id': None})
        await state.set_state(StateVacancy.SUBCATALOG)
        return await subcatalog_vacancy(message=message, state=state, session=session)
    elif state_data == StateVacancy.DESCRIPTION:
        await state.update_data({'name': None})
        await state.set_state(StateVacancy.NAME)
        return await name_vacancy(message=message, state=state, session=session)
    elif state_data == StateVacancy.EXPERIENCE:
        await state.update_data({'description': None})
        await state.set_state(StateVacancy.DESCRIPTION)
        return await description_vacancy(message=message, state=state)
    elif state_data == StateVacancy.LANGUAGE:
        await state.update_data({'experience': None})
        await state.set_state(StateVacancy.EXPERIENCE)
        return await experience_vacancy(message=message, state=state)
    elif state_data == StateVacancy.DISABILITY:
        await state.update_data({'language': None})
        await state.set_state(StateVacancy.LANGUAGE)
        return await language_vacancy(message=message, state=state)
    elif state_data == StateVacancy.SALARY:
        await state.update_data({'disability': None})
        await state.set_state(StateVacancy.DISABILITY)
        return await disability_vacancy(message=message, state=state)
    elif state_data == StateVacancy.REGION:
        await state.update_data({'salary': None})
        await state.set_state(StateVacancy.SALARY)
        return await salary_vacancy(message=message, state=state)
    elif state_data == StateVacancy.CITY:
        await state.update_data({'country_id': None, 'country_name': None, 'region_id': None, 'region_name': None})
        await state.set_state(StateVacancy.REGION)
        return await region_vacancy(message=message, state=state, session=session)


@vacancy_router.message(StateVacancy.CATALOG, CatalogFilter())
async def subcatalog_vacancy(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()

    if not state_data['catalog_id'] and not state_data['catalog_title'] and not state_data['currency_id']:
        catalog_logo = message.text.split(' ')[0]
        catalog, currency = await get_catalog_one(session, catalog_logo=catalog_logo), await get_currency_one(session, currency_abbreviation='UAH')
        await state.update_data({'catalog_id': catalog.id, 'catalog_title': catalog.title, 'currency_id': currency.id})
        state_data = await state.get_data()

    subcatalog = await get_subcatalog_all(session, state_data['catalog_id'])

    reply_markup = vacancy_profession_button(state_data['lang'], 'subcatalog', subcatalog, state_data['catalog_title'])

    await message.answer(text=connector[state_data['lang']]['message']['vacancy']['subcatalog'], reply_markup=reply_markup)
    await state.set_state(StateVacancy.SUBCATALOG)


@vacancy_router.message(StateVacancy.SUBCATALOG, SubcatalogFilter())
async def name_vacancy(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()

    if not state_data['subcatalog_id']:
        subcatalog_name = ''

        for key, value in connector[state_data['lang']]['catalog'][state_data['catalog_title']]['subcatalog'].items():
            if value == message.text:
                subcatalog_name = key
                break

        subcatalog = await get_subcatalog_one(session, subcatalog_name, state_data['catalog_id'])
        await state.update_data({'subcatalog_id': subcatalog.id})

    reply_markup = vacancy_keyboard_button(state_data['lang'])

    await message.answer(text=connector[state_data['lang']]['message']['vacancy']['name'], reply_markup=reply_markup)
    await state.set_state(StateVacancy.NAME)


@vacancy_router.message(StateVacancy.NAME, NameFilter())
async def description_vacancy(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()

    if not state_data['name']:
        await state.update_data({'name': message.text})

    reply_markup = vacancy_keyboard_button(state_data['lang'])

    await message.answer(text=connector[state_data['lang']]['message']['vacancy']['description'], reply_markup=reply_markup)
    await state.set_state(StateVacancy.DESCRIPTION)


@vacancy_router.message(StateVacancy.DESCRIPTION, DescriptionFilter())
async def experience_vacancy(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()

    if not state_data['description']:
        await state.update_data({'description': message.text})

    reply_markup = vacancy_choice_button(state_data['lang'])

    await message.answer(text=connector[state_data['lang']]['message']['vacancy']['experience'], reply_markup=reply_markup)
    await state.set_state(StateVacancy.EXPERIENCE)


@vacancy_router.message(StateVacancy.EXPERIENCE, ChoiceFilter())
async def language_vacancy(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()

    if not state_data['experience']:
        await state.update_data({'experience': True if message.text.split(' ')[0] == '✅' else False})

    reply_markup = vacancy_choice_button(state_data['lang'])

    await message.answer(text=connector[state_data['lang']]['message']['vacancy']['language'], reply_markup=reply_markup)
    await state.set_state(StateVacancy.LANGUAGE)


@vacancy_router.message(StateVacancy.LANGUAGE, ChoiceFilter())
async def disability_vacancy(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()

    if not state_data['language']:
        await state.update_data({'language': True if message.text.split(' ')[0] == '✅' else False})

    reply_markup = vacancy_choice_button(state_data['lang'])

    await message.answer(text=connector[state_data['lang']]['message']['vacancy']['disability'], reply_markup=reply_markup)
    await state.set_state(StateVacancy.DISABILITY)


@vacancy_router.message(StateVacancy.DISABILITY, ChoiceFilter())
async def salary_vacancy(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()

    if not state_data['disability']:
        await state.update_data({'disability': True if message.text.split(' ')[0] == '✅' else False})

    reply_markup = vacancy_keyboard_button(state_data['lang'])

    await message.answer(text=connector[state_data['lang']]['message']['vacancy']['salary'], reply_markup=reply_markup)
    await state.set_state(StateVacancy.SALARY)


@vacancy_router.message(StateVacancy.SALARY, PriceFilter())
async def region_vacancy(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()

    if not state_data['salary']:
        await state.update_data({'salary': int(message.text)})

    country, region = await get_country_first(session), await get_region_all(session)

    reply_markup = vacancy_location_button(state_data['lang'], country.name, 'region', region)

    await message.answer(text=connector[state_data['lang']]['message']['vacancy']['region'], reply_markup=reply_markup)
    await state.set_state(StateVacancy.REGION)


@vacancy_router.message(StateVacancy.REGION, RegionFilter())
async def city_vacancy(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()

    if not state_data['country_id'] and not state_data['country_name'] and not state_data['region_id'] and not state_data['region_name']:
        country = await get_country_first(session)
        region_name = ''

        for key, value in connector[state_data['lang']]['country'][country.name]['region'].items():
            if value['name'] == message.text:
                region_name = key
                break

        region = await get_region_one(session, region_name=region_name)

        await state.update_data({'country_id': country.id, 'country_name': country.name, 'region_id': region.id, 'region_name': region.name})
        state_data = await state.get_data()

    city = await get_city_all(session, state_data['region_id'])

    reply_markup = vacancy_location_button(state_data['lang'], state_data['country_name'], 'city', city, state_data['region_name'])

    await message.answer(text=connector[state_data['lang']]['message']['vacancy']['city'], reply_markup=reply_markup)
    await state.set_state(StateVacancy.CITY)


@vacancy_router.message(StateVacancy.CITY, CityFilter())
async def finish_vacancy(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()

    if message.text != connector[state_data['lang']]['button']['skip']:
        country, region = await get_country_first(session), await get_region_one(session=session, region_id=state_data['region_id'])
        city_name = ''

        for key, value in connector[state_data['lang']]['country'][country.name]['region'][region.name]['city'].items():
            if value == message.text:
                city_name = key
                break

        city = await get_city_one(session, city_name, region.id)
        await state.update_data({'city_id': city.id})

    state_data = await state.get_data()

    await create_vacancy(
        session=session,
        name=state_data['name'],
        description=state_data['description'],
        experience=state_data['experience'],
        language=state_data['language'],
        disability=state_data['disability'],
        salary=state_data['salary'],
        subcatalog_id=state_data['subcatalog_id'],
        currency_id=state_data['currency_id'],
        country_id=state_data['country_id'],
        region_id=state_data['region_id'],
        city_id=state_data['city_id'],
        user_id=message.from_user.id,
    )

    await message.answer(text=connector[state_data['lang']]['message']['vacancy']['finish'], reply_markup=ReplyKeyboardRemove())
    await state.clear()

    return await menu(message=message, session=session)


@vacancy_router.message(StateFilter("*"))
async def error_vacancy(message: Message) -> None:
    await message.delete()


@vacancy_router.message()
async def catalog_vacancy_message(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()
    catalog = await get_catalog_all(session)

    reply_markup = vacancy_profession_button(state_data['lang'], 'catalog', catalog)

    await message.answer(text=connector[state_data['lang']]['message']['vacancy']['catalog'], reply_markup=reply_markup)
    await state.set_state(StateVacancy.CATALOG)
