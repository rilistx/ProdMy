from datetime import datetime, timedelta

from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from sqlalchemy.ext.asyncio import AsyncSession

from core.filters.vacancy import CatalogFilter, SubcatalogFilter, NameFilter, DescriptionFilter, RequirementFilter, \
    EmploymentFilter, ChoiceFilter, PriceFilter, RegionFilter, CityFilter, CancelFilter, BackFilter
from core.handlers.menu import menu, redirector
from core.keyboards.menu import MenuCallBack
from core.keyboards.vacancy import vacancy_profession_button, vacancy_keyboard_button, vacancy_employment_button, \
    vacancy_choice_button, vacancy_location_button
from core.database.querys import get_catalog_all, get_subcatalog_all, get_catalog_one, get_subcatalog_one, \
    get_country_first, get_region_all, get_region_one, get_city_all, get_city_one, create_vacancy, get_vacancy_one, \
    update_vacancy, get_currency_first, deactivate_vacancy, delete_vacancy
from core.schedulers.vacancy import scheduler_deactivate_vacancy
from core.states.vacancy import StateVacancy
from core.utils.channel import vacancy_channel
from core.utils.connector import connector


vacancy_router = Router()


@vacancy_router.callback_query(MenuCallBack.filter(F.key == 'vacancy'))
async def catalog_vacancy_callback(
        callback: CallbackQuery,
        callback_data: MenuCallBack,
        state: FSMContext,
        session: AsyncSession,
        apscheduler: AsyncIOScheduler,
) -> None:
    if callback_data.method == 'activate' or callback_data.method == 'deactivate':
        await callback.answer("Вакансия деактивирована!." if callback_data.method == 'deactivate' else "Вакансия активирована!.")

        await deactivate_vacancy(
            session=session,
            vacancy_id=callback_data.vacancy_id,
            method='deactivate' if callback_data.method == 'deactivate' else 'activate',
        )

        if apscheduler.get_job(f'deactivate_vacancy_{str(callback_data.vacancy_id)}'):
            apscheduler.remove_job(f'deactivate_vacancy_{str(callback_data.vacancy_id)}')

        if callback_data.method == 'activate':
            apscheduler.add_job(
                scheduler_deactivate_vacancy,
                trigger='date',
                next_run_time=datetime.now() + timedelta(seconds=30),
                kwargs={
                    'chat_id': callback.message.chat.id,
                    'vacancy_id': callback_data.vacancy_id,
                },
                id=f'deactivate_vacancy_{str(callback_data.vacancy_id)}',
            )

        return await redirector(
            callback=callback,
            callback_data=callback_data,
            session=session,
            view=callback_data.view,
            level=4,
            key='description',
            page=callback_data.page,
            catalog_id=callback_data.catalog_id,
            subcatalog_id=callback_data.subcatalog_id,
            vacancy_id=callback_data.vacancy_id,
        )

    if callback_data.method == 'delete':
        if apscheduler.get_job(f'deactivate_vacancy_{str(callback_data.vacancy_id)}'):
            apscheduler.remove_job(f'deactivate_vacancy_{str(callback_data.vacancy_id)}')

        await delete_vacancy(
            session=session,
            vacancy_id=callback_data.vacancy_id,
        )
        await callback.answer("Вакансия удалена!.")

        return await redirector(
            callback=callback,
            callback_data=callback_data,
            session=session,
            view=callback_data.view,
            level=3,
            key='view',
            page=callback_data.page - 1 if callback_data.page - 1 != 0 else 1,
            catalog_id=callback_data.catalog_id,
            subcatalog_id=callback_data.subcatalog_id,
        )

    await callback.message.delete()

    state_list = [
        'lang', 'catalog_id', 'catalog_title', 'currency_id', 'subcatalog_id', 'name', 'description',
        'requirement', 'employment', 'experience', 'remote', 'language', 'foreigner', 'disability',
        'salary', 'country_id', 'country_name', 'region_id', 'region_name', 'city_id',
    ]

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

    catalog = await get_catalog_all(
        session=session,
    )

    reply_markup = vacancy_profession_button(
        lang=callback_data.lang,
        data_name='catalog',
        data_list=catalog,
        change=StateVacancy.change,
    )

    await callback.message.answer(
        text=connector[callback_data.lang]['message']['vacancy']['create']['catalog'] +
             (connector[callback_data.lang]['message']['vacancy']['update']['add'] if StateVacancy.change else ''),
        reply_markup=reply_markup,
    )

    await callback.answer()
    await state.set_state(StateVacancy.CATALOG)


@vacancy_router.message(StateFilter(StateVacancy), CancelFilter())
async def exit_vacancy(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
) -> None:
    state_data = await state.get_data()

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['update' if StateVacancy.change else 'create']['exit'],
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
        await state.clear()

        return await menu(
            message=message,
            session=session,
            method='create',
            level=10,
            key='confirm',
        )


@vacancy_router.message(StateFilter(StateVacancy), BackFilter())
async def back_vacancy(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
) -> None:
    state_data = await state.get_state()

    if state_data == StateVacancy.SUBCATALOG:
        await state.update_data({
            'catalog_id': None,
            'catalog_title': None,
            'currency_id': None,
        })

        await state.set_state(StateVacancy.CATALOG)

        return await catalog_vacancy_message(
            message=message,
            state=state,
            session=session,
        )
    elif state_data == StateVacancy.NAME:
        await state.update_data({
            'subcatalog_id': None,
        })

        await state.set_state(StateVacancy.SUBCATALOG)

        return await subcatalog_vacancy(
            message=message,
            state=state,
            session=session,
        )
    elif state_data == StateVacancy.DESCRIPTION:
        await state.update_data({
            'name': None,
        })

        await state.set_state(StateVacancy.NAME)

        return await name_vacancy(
            message=message,
            state=state,
            session=session,
        )
    elif state_data == StateVacancy.REQUIREMENT:
        await state.update_data({
            'description': None,
        })

        await state.set_state(StateVacancy.DESCRIPTION)

        return await description_vacancy(
            message=message,
            state=state,
        )
    elif state_data == StateVacancy.EMPLOYMENT:
        await state.update_data({
            'requirement': None,
        })

        await state.set_state(StateVacancy.REQUIREMENT)

        return await requirement_vacancy(
            message=message,
            state=state,
        )
    elif state_data == StateVacancy.EXPERIENCE:
        await state.update_data({
            'employment': None,
        })

        await state.set_state(StateVacancy.EMPLOYMENT)

        return await employment_vacancy(
            message=message,
            state=state,
        )
    elif state_data == StateVacancy.REMOTE:
        await state.update_data({
            'experience': None,
        })

        await state.set_state(StateVacancy.EXPERIENCE)

        return await experience_vacancy(
            message=message,
            state=state,
        )
    elif state_data == StateVacancy.LANGUAGE:
        await state.update_data({
            'remote': None,
        })

        await state.set_state(StateVacancy.REMOTE)

        return await remote_vacancy(
            message=message,
            state=state,
        )
    elif state_data == StateVacancy.FOREIGNER:
        await state.update_data({
            'language': None,
        })

        await state.set_state(StateVacancy.LANGUAGE)

        return await language_vacancy(
            message=message,
            state=state,
        )
    elif state_data == StateVacancy.DISABILITY:
        await state.update_data({
            'foreigner': None,
        })

        await state.set_state(StateVacancy.FOREIGNER)

        return await foreigner_vacancy(
            message=message,
            state=state,
        )
    elif state_data == StateVacancy.SALARY:
        await state.update_data({
            'disability': None,
        })

        await state.set_state(StateVacancy.DISABILITY)

        return await disability_vacancy(
            message=message,
            state=state,
        )
    elif state_data == StateVacancy.REGION:
        await state.update_data({
            'salary': None,
        })

        await state.set_state(StateVacancy.SALARY)

        return await salary_vacancy(
            message=message,
            state=state,
        )
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
async def subcatalog_vacancy(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
) -> None:
    state_data = await state.get_data()

    if not state_data['catalog_id'] and not state_data['catalog_title'] and not state_data['currency_id']:
        if message.text == connector[state_data['lang']]['button']['nochange']:
            catalog = await get_catalog_one(
                session=session,
                catalog_id=StateVacancy.change.catalog_id,
            )
        else:
            catalog = await get_catalog_one(
                session=session,
                catalog_logo=message.text.split(' ')[0],
            )

        currency = await get_currency_first(
            session=session,
        )

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
        change=True if StateVacancy.change and StateVacancy.change.catalog_id == state_data['catalog_id'] else False,
        catalog_title=state_data['catalog_title'],
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['create']['subcatalog'] + (connector[state_data['lang']]['message']['vacancy']['update']['add'] if (StateVacancy.change and message.text == connector[state_data['lang']]['button']['nochange']) or (StateVacancy.change and StateVacancy.change.catalog_id == state_data['catalog_id']) else ''),
        reply_markup=reply_markup,
    )

    await state.set_state(StateVacancy.SUBCATALOG)


@vacancy_router.message(StateVacancy.SUBCATALOG, SubcatalogFilter())
async def name_vacancy(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
) -> None:
    state_data = await state.get_data()

    if not state_data['subcatalog_id']:
        if message.text == connector[state_data['lang']]['button']['nochange']:
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
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['create']['name'] + (connector[state_data['lang']]['message']['vacancy']['update']['add'] if StateVacancy.change else ''),
        reply_markup=reply_markup,
    )

    await state.set_state(StateVacancy.NAME)


@vacancy_router.message(StateVacancy.NAME, NameFilter())
async def description_vacancy(
        message: Message,
        state: FSMContext,
) -> None:
    state_data = await state.get_data()

    if not state_data['name']:
        await state.update_data({
            'name': StateVacancy.change.name if message.text == connector[state_data['lang']]['button']['nochange'] else message.text,
        })

    reply_markup = vacancy_keyboard_button(
        lang=state_data['lang'],
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['create']['description'] + (connector[state_data['lang']]['message']['vacancy']['update']['add'] if StateVacancy.change else ''),
        reply_markup=reply_markup,
    )

    await state.set_state(StateVacancy.DESCRIPTION)


@vacancy_router.message(StateVacancy.DESCRIPTION, DescriptionFilter())
async def requirement_vacancy(
        message: Message,
        state: FSMContext,
) -> None:
    state_data = await state.get_data()

    if not state_data['description']:
        await state.update_data({
            'description': StateVacancy.change.description if message.text == connector[state_data['lang']]['button']['nochange'] else message.text,
        })

    reply_markup = vacancy_keyboard_button(
        lang=state_data['lang'],
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['create']['requirement'] + (connector[state_data['lang']]['message']['vacancy']['update']['add'] if StateVacancy.change else ''),
        reply_markup=reply_markup,
    )

    await state.set_state(StateVacancy.REQUIREMENT)


@vacancy_router.message(StateVacancy.REQUIREMENT, RequirementFilter())
async def employment_vacancy(
        message: Message,
        state: FSMContext,
) -> None:
    state_data = await state.get_data()

    if not state_data['requirement']:
        await state.update_data({
            'requirement': StateVacancy.change.description if message.text == connector[state_data['lang']]['button']['nochange'] else message.text,
        })

    reply_markup = vacancy_employment_button(
        lang=state_data['lang'],
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['create']['employment'] + (connector[state_data['lang']]['message']['vacancy']['update']['add'] if StateVacancy.change else ''),
        reply_markup=reply_markup,
    )

    await state.set_state(StateVacancy.EMPLOYMENT)


@vacancy_router.message(StateVacancy.EMPLOYMENT, EmploymentFilter())
async def experience_vacancy(
        message: Message,
        state: FSMContext,
) -> None:
    state_data = await state.get_data()

    if not state_data['employment']:
        await state.update_data({
            'employment': StateVacancy.change.experience if message.text == connector[state_data['lang']]['button']['nochange'] else (True if message.text == connector[state_data['lang']]['button']['complete'] else False),
        })

    reply_markup = vacancy_choice_button(
        lang=state_data['lang'],
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['create']['experience'] + (connector[state_data['lang']]['message']['vacancy']['update']['add'] if StateVacancy.change else ''),
        reply_markup=reply_markup,
    )

    await state.set_state(StateVacancy.EXPERIENCE)


@vacancy_router.message(StateVacancy.EXPERIENCE, ChoiceFilter())
async def remote_vacancy(
        message: Message,
        state: FSMContext,
) -> None:
    state_data = await state.get_data()

    if not state_data['experience']:
        await state.update_data({
            'experience': StateVacancy.change.experience if message.text == connector[state_data['lang']]['button']['nochange'] else (True if message.text == connector[state_data['lang']]['button']['yes'] else False),
        })

    reply_markup = vacancy_choice_button(
        lang=state_data['lang'],
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['create']['remote'] + (connector[state_data['lang']]['message']['vacancy']['update']['add'] if StateVacancy.change else ''),
        reply_markup=reply_markup,
    )

    await state.set_state(StateVacancy.REMOTE)


@vacancy_router.message(StateVacancy.REMOTE, ChoiceFilter())
async def language_vacancy(
        message: Message,
        state: FSMContext,
) -> None:
    state_data = await state.get_data()

    if not state_data['remote']:
        await state.update_data({
            'remote': StateVacancy.change.experience if message.text == connector[state_data['lang']]['button']['nochange'] else (True if message.text == connector[state_data['lang']]['button']['yes'] else False),
        })

    reply_markup = vacancy_choice_button(
        lang=state_data['lang'],
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['create']['language'] + (connector[state_data['lang']]['message']['vacancy']['update']['add'] if StateVacancy.change else ''),
        reply_markup=reply_markup,
    )

    await state.set_state(StateVacancy.LANGUAGE)


@vacancy_router.message(StateVacancy.LANGUAGE, ChoiceFilter())
async def foreigner_vacancy(
        message: Message,
        state: FSMContext,
) -> None:
    state_data = await state.get_data()

    if not state_data['language']:
        await state.update_data({
            'language': StateVacancy.change.language if message.text == connector[state_data['lang']]['button']['nochange'] else (True if message.text == connector[state_data['lang']]['button']['yes'] else False),
        })

    reply_markup = vacancy_choice_button(
        lang=state_data['lang'],
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['create']['foreigner'] + (connector[state_data['lang']]['message']['vacancy']['update']['add'] if StateVacancy.change else ''),
        reply_markup=reply_markup,
    )

    await state.set_state(StateVacancy.FOREIGNER)


@vacancy_router.message(StateVacancy.FOREIGNER, ChoiceFilter())
async def disability_vacancy(
        message: Message,
        state: FSMContext,
) -> None:
    state_data = await state.get_data()

    if not state_data['foreigner']:
        await state.update_data({
            'foreigner': StateVacancy.change.foreigner if message.text == connector[state_data['lang']]['button']['nochange'] else (True if message.text == connector[state_data['lang']]['button']['yes'] else False),
        })

    reply_markup = vacancy_choice_button(
        lang=state_data['lang'],
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['create']['disability'] + (connector[state_data['lang']]['message']['vacancy']['update']['add'] if StateVacancy.change else ''),
        reply_markup=reply_markup,
    )

    await state.set_state(StateVacancy.DISABILITY)


@vacancy_router.message(StateVacancy.DISABILITY, ChoiceFilter())
async def salary_vacancy(
        message: Message,
        state: FSMContext,
) -> None:
    state_data = await state.get_data()

    if not state_data['disability']:
        await state.update_data({
            'disability': StateVacancy.change.disability if message.text == connector[state_data['lang']]['button']['nochange'] else (True if message.text == connector[state_data['lang']]['button']['yes'] else False),
        })

    reply_markup = vacancy_keyboard_button(
        lang=state_data['lang'],
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['create']['salary'] + (connector[state_data['lang']]['message']['vacancy']['update']['add'] if StateVacancy.change else ''),
        reply_markup=reply_markup,
    )

    await state.set_state(StateVacancy.SALARY)


@vacancy_router.message(StateVacancy.SALARY, PriceFilter())
async def region_vacancy(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
) -> None:
    state_data = await state.get_data()

    if not state_data['salary']:
        await state.update_data({
            'salary': StateVacancy.change.salary if message.text == connector[state_data['lang']]['button']['nochange'] else int(message.text),
        })

    country = await get_country_first(
        session=session,
    )
    region = await get_region_all(
        session=session,
        country_id=country.id,
    )

    reply_markup = vacancy_location_button(
        lang=state_data['lang'],
        country_name=country.name,
        data_name='region',
        data_list=region,
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['create']['region'] + (connector[state_data['lang']]['message']['vacancy']['update']['add'] if StateVacancy.change else ''),
        reply_markup=reply_markup,
    )

    await state.set_state(StateVacancy.REGION)


@vacancy_router.message(StateVacancy.REGION, RegionFilter())
async def city_vacancy(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
) -> None:
    state_data = await state.get_data()

    if not state_data['country_id'] and not state_data['country_name'] and not state_data['region_id'] and not state_data['region_name']:
        country = await get_country_first(
            session=session,
        )

        if message.text == connector[state_data['lang']]['button']['nochange']:
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
        change=True if StateVacancy.change and StateVacancy.change.region_id == state_data['region_id'] else False,
        region_name=state_data['region_name'],
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['create']['city'] + (connector[state_data['lang']]['message']['vacancy']['update']['add'] if (StateVacancy.change and message.text == connector[state_data['lang']]['button']['nochange']) or (StateVacancy.change and StateVacancy.change.region_id == state_data['region_id']) else ''),
        reply_markup=reply_markup,
    )

    await state.set_state(StateVacancy.CITY)


@vacancy_router.message(StateVacancy.CITY, CityFilter())
async def finish_vacancy(
        message: Message,
        bot: Bot,
        state: FSMContext,
        session: AsyncSession,
        apscheduler: AsyncIOScheduler,
) -> None:
    state_data = await state.get_data()

    if message.text != connector[state_data['lang']]['button']['skip']:
        if message.text == connector[state_data['lang']]['button']['nochange']:
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

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['update' if StateVacancy.change else 'create']['finish'],
        reply_markup=ReplyKeyboardRemove(),
    )

    if StateVacancy.change:
        await update_vacancy(
            session=session,
            data=state_data,
            vacancy_id=StateVacancy.change.id,
        )

        await vacancy_channel(
            bot=bot,
            session=session,
            method='update',
            user_id=message.chat.id,
            vacancy_id=StateVacancy.change.id,
        )

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
        vacancy = await create_vacancy(
            session=session,
            data=state_data,
            user_id=message.from_user.id,
        )

        if apscheduler.get_job(f'deactivate_vacancy_{str(vacancy.id)}'):
            apscheduler.remove_job(f'deactivate_vacancy_{str(vacancy.id)}')

        apscheduler.add_job(
            scheduler_deactivate_vacancy,
            trigger='date',
            next_run_time=datetime.now() + timedelta(seconds=30),
            kwargs={
                'chat_id': message.chat.id,
                'vacancy_id': vacancy.id,
            },
            id=f'deactivate_vacancy_{str(vacancy.id)}',
        )

        await vacancy_channel(
            bot=bot,
            session=session,
            method='create',
            user_id=message.chat.id,
            vacancy_id=vacancy.id,
        )

        await state.clear()

        return await menu(
            message=message,
            session=session,
        )


@vacancy_router.message(StateFilter(StateVacancy))
async def error_vacancy(
        message: Message,
) -> None:
    await message.delete()


@vacancy_router.message(StateFilter(StateVacancy))
async def catalog_vacancy_message(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
) -> None:
    state_data = await state.get_data()

    catalog = await get_catalog_all(
        session=session,
    )

    reply_markup = vacancy_profession_button(
        lang=state_data['lang'],
        data_name='catalog',
        data_list=catalog,
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=connector[state_data['lang']]['message']['vacancy']['create']['catalog'] + (connector[state_data['lang']]['message']['vacancy']['update']['add'] if StateVacancy.change else ''),
        reply_markup=reply_markup,
    )

    await state.set_state(StateVacancy.CATALOG)
