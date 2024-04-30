from datetime import datetime, timedelta

from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.filters.vacancy import CatalogFilter, SubcatalogFilter, NameFilter, DescriptionFilter, RequirementFilter, \
    EmploymentFilter, ChoiceFilter, PriceFilter, RegionFilter, CityFilter, CancelFilter, BackFilter
from core.handlers.menu import menu
from core.keyboards.menu import MenuCallBack
from core.keyboards.vacancy import vacancy_profession_button, vacancy_keyboard_button, vacancy_employment_button, \
    vacancy_choice_button, vacancy_location_button
from core.database.querys import get_catalog_all, get_subcatalog_all, get_catalog_one, get_subcatalog_one, \
    get_country_first, get_region_all, get_region_one, get_city_all, get_city_one, create_vacancy, get_vacancy_one, \
    update_vacancy, get_currency_first
from core.schedulers.vacancy import scheduler_deactivate_vacancy
from core.states.vacancy import StateVacancy
from core.utils.channel import vacancy_channel
from core.utils.connector import connector
from core.utils.message import get_text_vacancy_create
from core.utils.vacancy import check_update_vacancy, method_preview_vacancy, method_complaint_vacancy, \
    method_delete_vacancy


vacancy_router = Router()


@vacancy_router.callback_query(MenuCallBack.filter(F.key == 'vacancy'))
async def catalog_vacancy_callback(
        callback: CallbackQuery,
        bot: Bot,
        callback_data: MenuCallBack,
        state: FSMContext,
        session: AsyncSession,
        apscheduler: AsyncIOScheduler,
) -> None:
    if callback_data.method == 'activate' or callback_data.method == 'deactivate':
        return await method_preview_vacancy(
            callback=callback,
            callback_data=callback_data,
            session=session,
            apscheduler=apscheduler,
        )

    if callback_data.method == 'complaint' or callback_data.method == 'pity':
        return await method_complaint_vacancy(
            bot=bot,
            callback=callback,
            callback_data=callback_data,
            session=session,
        )
    if callback_data.method == 'delete':
        return await method_delete_vacancy(
            callback=callback,
            callback_data=callback_data,
            session=session,
            apscheduler=apscheduler,
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
            'vacancy_view': callback_data.view,
            'vacancy_page': callback_data.page,
            'vacancy_catalog_id': callback_data.catalog_id,
            'vacancy_subcatalog_id': callback_data.subcatalog_id,
            'vacancy_vacancy_id': callback_data.vacancy_id,
        })

        StateVacancy.change = await get_vacancy_one(session=session, vacancy_id=callback_data.vacancy_id)

    text = get_text_vacancy_create(
        lang=callback_data.lang,
        func_name='catalog',
        change=True if StateVacancy.change else False
    )
    reply_markup = vacancy_profession_button(
            lang=callback_data.lang,
            data_name='catalog',
            data_list=await get_catalog_all(session=session),
            change=True if StateVacancy.change else False,
        )

    await callback.message.answer(
        text=text,
        reply_markup=reply_markup,
    )

    await callback.answer()
    await state.set_state(StateVacancy.CATALOG)


@vacancy_router.message(StateFilter(StateVacancy), CancelFilter())
async def cancel_vacancy(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
) -> None:
    state_data = await state.get_data()

    text = get_text_vacancy_create(
        lang=state_data['lang'],
        func_name='exit',
        change=True if StateVacancy.change else False,
    )
    reply_markup = ReplyKeyboardRemove()

    await message.answer(
        text=text,
        reply_markup=reply_markup,
    )

    return_data = {
        'method': None if StateVacancy.change else 'create',
        'view': state_data['update_view'] if StateVacancy.change else None,
        'level': 4 if StateVacancy.change else 10,
        'key': 'description' if StateVacancy.change else 'confirm_user',
        'page': state_data['update_page'] if StateVacancy.change else None,
        'catalog_id': state_data['update_catalog_id'] if StateVacancy.change else None,
        'subcatalog_id': state_data['update_subcatalog_id'] if StateVacancy.change else None,
        'vacancy_id': state_data['update_vacancy_id'] if StateVacancy.change else None,
    }

    StateVacancy.change = None
    await state.clear()

    return await menu(
        message=message,
        session=session,
        method=return_data['method'],
        view=return_data['view'],
        level=return_data['level'],
        key=return_data['key'],
        page=return_data['page'],
        catalog_id=return_data['catalog_id'],
        subcatalog_id=return_data['subcatalog_id'],
        vacancy_id=return_data['vacancy_id'],
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
            'country_id': None,
            'country_name': None,
            'salary': None,
        })

        await state.set_state(StateVacancy.SALARY)

        return await salary_vacancy(
            message=message,
            state=state,
        )
    elif state_data == StateVacancy.CITY:
        await state.update_data({
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
        catalog_id: int | None = None,
        catalog_logo: str | None = None,
) -> None:
    state_data = await state.get_data()

    if not state_data['catalog_id'] and not state_data['catalog_title'] and not state_data['currency_id']:
        if StateVacancy.change and message.text == connector[state_data['lang']]['button']['vacancy']['nochange']:
            catalog_id = StateVacancy.change.catalog_id

        if message.text != connector[state_data['lang']]['button']['vacancy']['nochange']:
            catalog_logo = message.text.split(' ')[0]

        catalog = await get_catalog_one(session=session, catalog_id=catalog_id, catalog_logo=catalog_logo)
        currency = await get_currency_first(session=session)

        await state.update_data({
            'catalog_id': catalog.id,
            'catalog_title': catalog.title,
            'currency_id': currency.id
        })

        state_data = await state.get_data()

    text = get_text_vacancy_create(
        lang=state_data['lang'],
        func_name='subcatalog',
        change=True if StateVacancy.change and StateVacancy.change.catalog_id == state_data['catalog_id'] else False,
    )
    reply_markup = vacancy_profession_button(
        lang=state_data['lang'],
        data_name='subcatalog',
        data_list=await get_subcatalog_all(session=session, catalog_id=state_data['catalog_id']),
        change=True if StateVacancy.change and StateVacancy.change.catalog_id == state_data['catalog_id'] else False,
        catalog_title=state_data['catalog_title'],
    )

    await message.answer(
        text=text,
        reply_markup=reply_markup,
    )

    await state.set_state(StateVacancy.SUBCATALOG)


@vacancy_router.message(StateVacancy.SUBCATALOG, SubcatalogFilter())
async def name_vacancy(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
        subcatalog_id: int | None = None,
        subcatalog_title: str | None = None,
) -> None:
    state_data = await state.get_data()

    if not state_data['subcatalog_id']:
        if message.text != connector[state_data['lang']]['button']['vacancy']['nochange']:
            for key, value in connector[state_data['lang']]['catalog'][state_data['catalog_title']]['subcatalog'].items():
                if value == message.text:
                    subcatalog_title = key
                    break

        if StateVacancy.change and message.text == connector[state_data['lang']]['button']['vacancy']['nochange']:
            subcatalog_id = StateVacancy.change.subcatalog_id

        subcatalog = await get_subcatalog_one(
            session=session,
            catalog_id=state_data['catalog_id'],
            subcatalog_id=subcatalog_id,
            subcatalog_title=subcatalog_title,
        )

        await state.update_data({
            'subcatalog_id': subcatalog.id,
        })

    text = get_text_vacancy_create(
        lang=state_data['lang'],
        func_name='name',
        change=True if StateVacancy.change else False,
    )
    reply_markup = vacancy_keyboard_button(
        lang=state_data['lang'],
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=text,
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
        if message.text == connector[state_data['lang']]['button']['vacancy']['nochange']:
            name = StateVacancy.change.name
        else:
            name = message.text

        await state.update_data({
            'name': name,
        })

    text = get_text_vacancy_create(
        lang=state_data['lang'],
        func_name='description',
        change=True if StateVacancy.change else False,
    )
    reply_markup = vacancy_keyboard_button(
        lang=state_data['lang'],
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=text,
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
        if message.text == connector[state_data['lang']]['button']['vacancy']['nochange']:
            description = StateVacancy.change.description
        else:
            description = message.text

        await state.update_data({
            'description': description,
        })

    text = get_text_vacancy_create(
        lang=state_data['lang'],
        func_name='requirement',
        change=True if StateVacancy.change else False,
    )
    reply_markup = vacancy_keyboard_button(
        lang=state_data['lang'],
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=text,
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
        if message.text == connector[state_data['lang']]['button']['vacancy']['nochange']:
            requirement = StateVacancy.change.requirement
        else:
            requirement = message.text

        await state.update_data({
            'requirement': requirement,
        })

    text = get_text_vacancy_create(
        lang=state_data['lang'],
        func_name='employment',
        change=True if StateVacancy.change else False,
    )
    reply_markup = vacancy_employment_button(
        lang=state_data['lang'],
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=text,
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
        if message.text == connector[state_data['lang']]['button']['vacancy']['nochange']:
            employment = StateVacancy.change.employment
        else:
            if message.text == connector[state_data['lang']]['button']['vacancy']['employment']['complete']:
                employment = True
            else:
                employment = False

        await state.update_data({
            'employment': employment,
        })

    text = get_text_vacancy_create(
        lang=state_data['lang'],
        func_name='experience',
        change=True if StateVacancy.change else False,
    )
    reply_markup = vacancy_choice_button(
        lang=state_data['lang'],
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=text,
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
        if message.text == connector[state_data['lang']]['button']['vacancy']['nochange']:
            experience = StateVacancy.change.experience
        else:
            if message.text == connector[state_data['lang']]['button']['vacancy']['choice']['yes']:
                experience = True
            else:
                experience = False

        await state.update_data({
            'experience': experience,
        })

    text = get_text_vacancy_create(
        lang=state_data['lang'],
        func_name='remote',
        change=True if StateVacancy.change else False,
    )
    reply_markup = vacancy_choice_button(
        lang=state_data['lang'],
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=text,
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
        if message.text == connector[state_data['lang']]['button']['vacancy']['nochange']:
            remote = StateVacancy.change.remote
        else:
            if message.text == connector[state_data['lang']]['button']['vacancy']['choice']['yes']:
                remote = True
            else:
                remote = False

        await state.update_data({
            'remote': remote,
        })

    text = get_text_vacancy_create(
        lang=state_data['lang'],
        func_name='language',
        change=True if StateVacancy.change else False,
    )
    reply_markup = vacancy_choice_button(
        lang=state_data['lang'],
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=text,
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
        if message.text == connector[state_data['lang']]['button']['vacancy']['nochange']:
            language = StateVacancy.change.language
        else:
            if message.text == connector[state_data['lang']]['button']['vacancy']['choice']['yes']:
                language = True
            else:
                language = False

        await state.update_data({
            'language': language,
        })

    text = get_text_vacancy_create(
        lang=state_data['lang'],
        func_name='foreigner',
        change=True if StateVacancy.change else False,
    )
    reply_markup = vacancy_choice_button(
        lang=state_data['lang'],
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=text,
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
        if message.text == connector[state_data['lang']]['button']['vacancy']['nochange']:
            foreigner = StateVacancy.change.foreigner
        else:
            if message.text == connector[state_data['lang']]['button']['vacancy']['choice']['yes']:
                foreigner = True
            else:
                foreigner = False

        await state.update_data({
            'foreigner': foreigner,
        })

    text = get_text_vacancy_create(
        lang=state_data['lang'],
        func_name='disability',
        change=True if StateVacancy.change else False,
    )
    reply_markup = vacancy_choice_button(
        lang=state_data['lang'],
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=text,
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
        if message.text == connector[state_data['lang']]['button']['vacancy']['nochange']:
            disability = StateVacancy.change.disability
        else:
            if message.text == connector[state_data['lang']]['button']['vacancy']['choice']['yes']:
                disability = True
            else:
                disability = False

        await state.update_data({
            'disability': disability,
        })

    text = get_text_vacancy_create(
        lang=state_data['lang'],
        func_name='salary',
        change=True if StateVacancy.change else False,
    )
    reply_markup = vacancy_keyboard_button(
        lang=state_data['lang'],
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=text,
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

    if not state_data['country_id'] and not state_data['country_name'] and not state_data['salary']:
        country = await get_country_first(session=session)

        if message.text == connector[state_data['lang']]['button']['vacancy']['nochange']:
            salary = StateVacancy.change.salary
        else:
            salary = int(message.text)

        await state.update_data({
            'country_id': country.id,
            'country_name': country.name,
            'salary': salary,
        })

        state_data = await state.get_data()

    region = await get_region_all(session=session, country_id=state_data['country_id'])

    text = get_text_vacancy_create(
        lang=state_data['lang'],
        func_name='region',
        change=True if StateVacancy.change else False,
    )
    reply_markup = vacancy_location_button(
        lang=state_data['lang'],
        country_name=state_data['country_name'],
        data_name='region',
        data_list=region,
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=text,
        reply_markup=reply_markup,
    )

    await state.set_state(StateVacancy.REGION)


@vacancy_router.message(StateVacancy.REGION, RegionFilter())
async def city_vacancy(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
        region_id: int | None = None,
        region_name: str | None = None,
) -> None:
    state_data = await state.get_data()

    if not state_data['region_id'] and not state_data['region_name']:
        if message.text != connector[state_data['lang']]['button']['vacancy']['nochange']:
            for key, value in connector[state_data['lang']]['country'][state_data['country_name']]['region'].items():
                if value['name'] == message.text:
                    region_name = key
                    break

        if StateVacancy.change and message.text == connector[state_data['lang']]['button']['vacancy']['nochange']:
            region_id = StateVacancy.change.region_id

        region = await get_region_one(session=session, region_id=region_id, region_name=region_name)

        await state.update_data({
            'region_id': region.id,
            'region_name': region.name,
        })

        state_data = await state.get_data()

    text = get_text_vacancy_create(
        lang=state_data['lang'],
        func_name='city',
        change=True if StateVacancy.change and StateVacancy.change.region_id == state_data['region_id'] else False,
    )
    reply_markup = vacancy_location_button(
        lang=state_data['lang'],
        country_name=state_data['country_name'],
        data_name='city',
        data_list=await get_city_all(session=session, region_id=state_data['region_id']),
        change=True if StateVacancy.change and StateVacancy.change.region_id == state_data['region_id'] else False,
        region_name=state_data['region_name'],
    )

    await message.answer(
        text=text,
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
        city_id: int | None = None,
        city_name: str | None = None,
) -> None:
    state_data = await state.get_data()

    if message.text != connector[state_data['lang']]['button']['vacancy']['city']:
        if message.text != connector[state_data['lang']]['button']['vacancy']['nochange']:
            for key, value in connector[state_data['lang']]['country'][state_data['country_name']]['region'][state_data['region_name']]['city'].items():
                if value == message.text:
                    city_name = key
                    break

        if StateVacancy.change and message.text == connector[state_data['lang']]['button']['vacancy']['nochange']:
            city_id = StateVacancy.change.city_id

        city = await get_city_one(session=session, city_id=city_id, city_name=city_name)

        await state.update_data({
            'city_id': city.id,
        })

        state_data = await state.get_data()

    if StateVacancy.change:
        check_vacancy = check_update_vacancy(old_data=StateVacancy.change, new_data=state_data, method='change')

        if check_vacancy:
            await update_vacancy(session=session, data=state_data, vacancy_id=StateVacancy.change.id)

            check_channel = check_update_vacancy(old_data=StateVacancy.change, new_data=state_data, method='channel')

            if check_channel:
                await vacancy_channel(
                    bot=bot,
                    session=session,
                    method='change',
                    lang=state_data['lang'],
                    user_id=message.chat.id,
                    vacancy_id=StateVacancy.change.id,
                )

        text = get_text_vacancy_create(lang=state_data['lang'], func_name='change', change=check_vacancy)
    else:
        vacancy = await create_vacancy(session=session, data=state_data, user_id=message.from_user.id)

        if apscheduler.get_job(f'deactivate_vacancy_{str(vacancy.id)}'):
            apscheduler.remove_job(f'deactivate_vacancy_{str(vacancy.id)}')

        apscheduler.add_job(
            scheduler_deactivate_vacancy,
            trigger='date',
            next_run_time=datetime.now() + timedelta(days=30),
            kwargs={'chat_id': message.chat.id, 'vacancy_id': vacancy.id},
            id=f'deactivate_vacancy_{str(vacancy.id)}',
        )

        await vacancy_channel(
            bot=bot,
            session=session,
            method='create',
            lang=state_data['lang'],
            user_id=message.chat.id,
            vacancy_id=vacancy.id,
        )

        text = get_text_vacancy_create(lang=state_data['lang'], func_name='create')

    reply_markup = ReplyKeyboardRemove()

    await message.answer(
        text=text,
        reply_markup=reply_markup,
    )

    return_data = {
        'view': state_data['update_view'] if StateVacancy.change else None,
        'level': 4 if StateVacancy.change else None,
        'key': 'description' if StateVacancy.change else None,
        'page': state_data['update_page'] if StateVacancy.change else None,
        'catalog_id': state_data['update_catalog_id'] if StateVacancy.change else None,
        'subcatalog_id': state_data['update_subcatalog_id'] if StateVacancy.change else None,
        'vacancy_id': state_data['update_vacancy_id'] if StateVacancy.change else None,
    }

    StateVacancy.change = None
    await state.clear()

    return await menu(
        message=message,
        session=session,
        view=return_data['view'],
        level=return_data['level'],
        key=return_data['key'],
        page=return_data['page'],
        catalog_id=return_data['catalog_id'],
        subcatalog_id=return_data['subcatalog_id'],
        vacancy_id=return_data['vacancy_id'],
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
    lang = (await state.get_data())['lang']

    text = get_text_vacancy_create(
        lang=lang,
        func_name='catalog',
        change=True if StateVacancy.change else False,
    )
    reply_markup = vacancy_profession_button(
        lang=lang,
        data_name='catalog',
        data_list=await get_catalog_all(session=session),
        change=True if StateVacancy.change else False,
    )

    await message.answer(
        text=text,
        reply_markup=reply_markup,
    )

    await state.set_state(StateVacancy.CATALOG)
