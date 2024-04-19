from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from core.filters.vacancy import CatalogFilter, SubcatalogFilter, NameFilter, ChoiceFilter, PriceFilter, RegionFilter, \
    CityFilter, DescriptionFilter, ExitFilter, BackFilter
from core.handlers.menu import menu, redirector
from core.keyboards.menu import MenuCallBack
from core.keyboards.vacancy import vacancy_profession_button, vacancy_keyboard_button, vacancy_location_button, vacancy_choice_button
from core.models.querys import get_catalog_all, get_subcatalog_all, get_catalog_one, get_subcatalog_one, get_country_first, get_region_all, \
    get_region_one, get_city_all, get_city_one, create_vacancy, get_vacancy_one, update_vacancy, get_currency_first, deactivate_vacancy
from core.states.vacancy import StateVacancy
from core.utils.connector import connector


vacancy_router = Router()


@vacancy_router.callback_query(MenuCallBack.filter(F.key == 'vacancy'))
async def catalog_vacancy_callback(callback: CallbackQuery, callback_data: MenuCallBack, state: FSMContext, session: AsyncSession) -> None:
    if callback_data.method == 'delete':
        await deactivate_vacancy(
            session=session,
            vacancy_id=callback_data.vacancy_id,
        )
        await callback.answer("Вакансия деактивирована!.")

        return await redirector(
            callback=callback,
            callback_data=callback_data,
            session=session,
            view=callback_data.view,
            level=3,
            key='view',
            page=callback_data.page - 1 if callback_data.page - 1 != 0 else 1,
        )

    await callback.message.delete()

    state_list = ['lang', 'catalog_id', 'catalog_title', 'currency_id', 'subcatalog_id',
                  'name', 'description', 'language', 'experience', 'disability', 'salary',
                  'country_id', 'country_name', 'region_id', 'region_name', 'city_id']

    await state.update_data({key: callback_data.lang if key == 'lang' else None for key in state_list})

    if callback_data.method == 'update':
        await state.update_data({
            'update_view': callback_data.view,
            'update_page': callback_data.page,
            'update_catalog_id': callback_data.catalog_id,
            'update_subcatalog_id': callback_data.subcatalog_id,
            'update_vacancy_id': callback_data.vacancy_id,
        })
        StateVacancy.change = await get_vacancy_one(
            session=session,
            vacancy_id=callback_data.vacancy_id,
        )

    catalog = await get_catalog_all(session=session)

    reply_markup = vacancy_profession_button(
        lang=callback_data.lang,
        data_name='catalog',
        data_list=catalog,
        change=StateVacancy.change,
    )

    await callback.message.answer(
        text=connector[callback_data.lang]['message']['vacancy']['update' if StateVacancy.change else 'create']['catalog'],
        reply_markup=reply_markup,
    )
    await callback.answer()
    await state.set_state(StateVacancy.CATALOG)


@vacancy_router.message(StateFilter("*"), ExitFilter())
async def exit_vacancy(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['update' if StateVacancy.change else 'create']['exit'],
    )

    if StateVacancy.change:
        StateVacancy.change = None
        await state.clear()

        return await menu(
            message=message,
            session=session,
            view=state_data['update_view'],
            level=4,
            key='description',
            page=state_data['update_page'],
            catalog_id=state_data['update_catalog_id'],
            subcatalog_id=state_data['update_subcatalog_id'],
            vacancy_id=state_data['update_vacancy_id'],
        )
    else:
        StateVacancy.change = None
        await state.clear()

        return await menu(
            message=message,
            session=session,
            method='create',
            level=10,
            key='confirm',
        )


@vacancy_router.message(StateFilter("*"), BackFilter())
async def back_vacancy(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_state()

    if state_data == StateVacancy.SUBCATALOG:
        await state.update_data({
            'catalog_id': None,
            'catalog_title': None,
            'currency_id': None,
        })
        await state.set_state(StateVacancy.CATALOG)
        return await catalog_vacancy_message(message=message, state=state, session=session)
    elif state_data == StateVacancy.NAME:
        await state.update_data({
            'subcatalog_id': None,
        })
        await state.set_state(StateVacancy.SUBCATALOG)
        return await subcatalog_vacancy(message=message, state=state, session=session)
    elif state_data == StateVacancy.DESCRIPTION:
        await state.update_data({
            'name': None,
        })
        await state.set_state(StateVacancy.NAME)
        return await name_vacancy(message=message, state=state, session=session)
    elif state_data == StateVacancy.EXPERIENCE:
        await state.update_data({
            'description': None,
        })
        await state.set_state(StateVacancy.DESCRIPTION)
        return await description_vacancy(message=message, state=state)
    elif state_data == StateVacancy.LANGUAGE:
        await state.update_data({
            'experience': None,
        })
        await state.set_state(StateVacancy.EXPERIENCE)
        return await experience_vacancy(message=message, state=state)
    elif state_data == StateVacancy.DISABILITY:
        await state.update_data({
            'language': None,
        })
        await state.set_state(StateVacancy.LANGUAGE)
        return await language_vacancy(message=message, state=state)
    elif state_data == StateVacancy.SALARY:
        await state.update_data({
            'disability': None,
        })
        await state.set_state(StateVacancy.DISABILITY)
        return await disability_vacancy(message=message, state=state)
    elif state_data == StateVacancy.REGION:
        await state.update_data({
            'salary': None,
        })
        await state.set_state(StateVacancy.SALARY)
        return await salary_vacancy(message=message, state=state)
    elif state_data == StateVacancy.CITY:
        await state.update_data({
            'country_id': None,
            'country_name': None,
            'region_id': None,
            'region_name': None,
        })
        await state.set_state(StateVacancy.REGION)
        return await region_vacancy(
            message=message,
            state=state,
            session=session,
        )


@vacancy_router.message(StateVacancy.CATALOG, CatalogFilter())
async def subcatalog_vacancy(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()

    if not state_data['catalog_id'] and not state_data['catalog_title'] and not state_data['currency_id']:
        if message.text == 'Не менять!':
            catalog = await get_catalog_one(
                session=session,
                catalog_id=StateVacancy.change.catalog_id,
            )
        else:
            catalog = await get_catalog_one(
                session=session,
                catalog_logo=message.text.split(' ')[0],
            )

        currency = await get_currency_first(session=session)

        await state.update_data({
            'catalog_id': catalog.id,
            'catalog_title': catalog.title,
            'currency_id': currency.id,
        })
        state_data = await state.get_data()

    subcatalog = await get_subcatalog_all(
        session=session,
        catalog_id=state_data['catalog_id'],
    )

    reply_markup = vacancy_profession_button(
        lang=state_data['lang'],
        data_name='subcatalog',
        data_list=subcatalog,
        change=StateVacancy.change if message.text == 'Не менять!' else None,
        catalog_title=state_data['catalog_title'],
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['update' if StateVacancy.change else 'create']['subcatalog'],
        reply_markup=reply_markup,
    )
    await state.set_state(StateVacancy.SUBCATALOG)


@vacancy_router.message(StateVacancy.SUBCATALOG, SubcatalogFilter())
async def name_vacancy(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()

    if not state_data['subcatalog_id']:
        if message.text == 'Не менять!':
            subcatalog = await get_subcatalog_one(
                session=session,
                subcatalog_id=StateVacancy.change.subcatalog_id,
                catalog_id=state_data['catalog_id'],
            )
        else:
            subcatalog_title = ''
            for key, value in connector[state_data['lang']]['catalog'][state_data['catalog_title']]['subcatalog'].items():
                if value == message.text:
                    subcatalog_title = key
                    break

            subcatalog = await get_subcatalog_one(
                session=session,
                subcatalog_title=subcatalog_title,
                catalog_id=state_data['catalog_id'],
            )

        await state.update_data({
            'subcatalog_id': subcatalog.id,
        })

    reply_markup = vacancy_keyboard_button(
        lang=state_data['lang'],
        change=StateVacancy.change,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['update' if StateVacancy.change else 'create']['name'],
        reply_markup=reply_markup,
    )
    await state.set_state(StateVacancy.NAME)


@vacancy_router.message(StateVacancy.NAME, NameFilter())
async def description_vacancy(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()

    if not state_data['name']:
        await state.update_data({
            'name': StateVacancy.change.name if message.text == 'Не менять!' else message.text,
        })

    reply_markup = vacancy_keyboard_button(
        lang=state_data['lang'],
        change=StateVacancy.change,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['update' if StateVacancy.change else 'create']['description'],
        reply_markup=reply_markup,
    )
    await state.set_state(StateVacancy.DESCRIPTION)


@vacancy_router.message(StateVacancy.DESCRIPTION, DescriptionFilter())
async def experience_vacancy(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()

    if not state_data['description']:
        await state.update_data({
            'description': StateVacancy.change.description if message.text == 'Не менять!' else message.text,
        })

    reply_markup = vacancy_choice_button(
        lang=state_data['lang'],
        change=StateVacancy.change,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['update' if StateVacancy.change else 'create']['experience'],
        reply_markup=reply_markup,
    )
    await state.set_state(StateVacancy.EXPERIENCE)


@vacancy_router.message(StateVacancy.EXPERIENCE, ChoiceFilter())
async def language_vacancy(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()

    if not state_data['experience']:
        await state.update_data({
            'experience': StateVacancy.change.experience if message.text == 'Не менять!' else (True if message.text.split(' ')[0] == '✅' else False),
        })

    reply_markup = vacancy_choice_button(
        lang=state_data['lang'],
        change=StateVacancy.change,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['update' if StateVacancy.change else 'create']['language'],
        reply_markup=reply_markup,
    )
    await state.set_state(StateVacancy.LANGUAGE)


@vacancy_router.message(StateVacancy.LANGUAGE, ChoiceFilter())
async def disability_vacancy(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()

    if not state_data['language']:
        await state.update_data({
            'language': StateVacancy.change.language if message.text == 'Не менять!' else (True if message.text.split(' ')[0] == '✅' else False),
        })

    reply_markup = vacancy_choice_button(
        lang=state_data['lang'],
        change=StateVacancy.change,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['update' if StateVacancy.change else 'create']['disability'],
        reply_markup=reply_markup,
    )
    await state.set_state(StateVacancy.DISABILITY)


@vacancy_router.message(StateVacancy.DISABILITY, ChoiceFilter())
async def salary_vacancy(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()

    if not state_data['disability']:
        await state.update_data({
            'disability': StateVacancy.change.disability if message.text == 'Не менять!' else (True if message.text.split(' ')[0] == '✅' else False),
        })

    reply_markup = vacancy_keyboard_button(
        lang=state_data['lang'],
        change=StateVacancy.change,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['update' if StateVacancy.change else 'create']['salary'],
        reply_markup=reply_markup,
    )
    await state.set_state(StateVacancy.SALARY)


@vacancy_router.message(StateVacancy.SALARY, PriceFilter())
async def region_vacancy(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()

    if not state_data['salary']:
        await state.update_data({
            'salary': StateVacancy.change.salary if message.text == 'Не менять!' else int(message.text),
        })

    country = await get_country_first(session=session)
    region = await get_region_all(
        session=session,
        country_id=country.id,
    )

    reply_markup = vacancy_location_button(
        lang=state_data['lang'],
        country_name=country.name,
        data_name='region',
        data_list=region,
        change=StateVacancy.change,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['update' if StateVacancy.change else 'create']['region'],
        reply_markup=reply_markup,
    )
    await state.set_state(StateVacancy.REGION)


@vacancy_router.message(StateVacancy.REGION, RegionFilter())
async def city_vacancy(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()

    if not state_data['country_id'] and not state_data['country_name'] and not state_data['region_id'] and not state_data['region_name']:
        country = await get_country_first(session=session)
        if message.text == 'Не менять!':
            region = await get_region_one(
                session=session,
                region_id=StateVacancy.change.region_id,
            )
        else:
            region_name = ''
            for key, value in connector[state_data['lang']]['country'][country.name]['region'].items():
                if value['name'] == message.text:
                    region_name = key
                    break

            region = await get_region_one(
                session=session,
                region_name=region_name,
            )

        await state.update_data({
            'country_id': country.id,
            'country_name': country.name,
            'region_id': region.id,
            'region_name': region.name,
        })
        state_data = await state.get_data()

    city = await get_city_all(
        session=session,
        region_id=state_data['region_id'],
    )

    reply_markup = vacancy_location_button(
        lang=state_data['lang'],
        country_name=state_data['country_name'],
        data_name='city',
        data_list=city,
        change=StateVacancy.change if message.text == 'Не менять!' else None,
        region_name=state_data['region_name'],
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['update' if StateVacancy.change else 'create']['city'],
        reply_markup=reply_markup,
    )
    await state.set_state(StateVacancy.CITY)


@vacancy_router.message(StateVacancy.CITY, CityFilter())
async def finish_vacancy(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()

    if message.text != connector[state_data['lang']]['button']['skip']:
        if message.text == 'Не менять!':
            city = await get_city_one(
                session=session,
                city_id=StateVacancy.change.city_id,
            )
        else:
            city_name = ''
            for key, value in connector[state_data['lang']]['country'][state_data['country_name']]['region'][state_data['region_name']]['city'].items():
                if value == message.text:
                    city_name = key
                    break

            city = await get_city_one(
                session=session,
                city_name=city_name,
            )
        await state.update_data({
            'city_id': city.id,
        })

    state_data = await state.get_data()

    if StateVacancy.change:
        await update_vacancy(
            session=session,
            data=state_data,
            vacancy_id=StateVacancy.change.id,
        )
    else:
        await create_vacancy(
            session=session,
            data=state_data,
            user_id=message.from_user.id,
        )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['update' if StateVacancy.change else 'create']['finish'],
        reply_markup=ReplyKeyboardRemove(),
    )

    if StateVacancy.change:
        StateVacancy.change = None
        await state.clear()

        return await menu(
            message=message,
            session=session,
            view=state_data['update_view'],
            level=4,
            key='description',
            page=state_data['update_page'],
            catalog_id=state_data['update_catalog_id'],
            subcatalog_id=state_data['update_subcatalog_id'],
            vacancy_id=state_data['update_vacancy_id'],
        )
    else:
        StateVacancy.change = None
        await state.clear()

        return await menu(
            message=message,
            session=session,
        )


@vacancy_router.message(StateFilter("*"))
async def error_vacancy(message: Message) -> None:
    await message.delete()


@vacancy_router.message()
async def catalog_vacancy_message(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()
    catalog = await get_catalog_all(session=session)

    reply_markup = vacancy_profession_button(
        lang=state_data['lang'],
        data_name='catalog',
        data_list=catalog,
        change=StateVacancy.change,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['update' if StateVacancy.change else 'create']['catalog'],
        reply_markup=reply_markup,
    )
    await state.set_state(StateVacancy.CATALOG)
