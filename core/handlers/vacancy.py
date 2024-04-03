# from aiogram import Router, F
# from aiogram.types import Message, CallbackQuery
# from aiogram.fsm.context import FSMContext
#
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from core.commands.languages import json
# from core.keyboards.keyboards import ScheduleCallBack, EmploymentCallBack, ExpertiseCallBack
# from core.utils.processing import add_vacancy_catalog_data, add_vacancy_subcatalog_data, add_vacancy_name_data, \
#     add_vacancy_description_data, add_vacancy_schedule_data, add_vacancy_employment_data, add_vacancy_expertise_data, \
#     add_vacancy_disability_data, add_vacancy_language_data, add_vacancy_region_data, add_vacancy_city_data
# from core.states.states import StateVacancy
#
#
# vacancy_router = Router()
#
#
# @vacancy_router.callback_query(F.data == 'vacancy')
# async def catalog_vacancy(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
#     await state.update_data({
#         'complete': False,
#         'incomplete': False,
#         'shift': False,
#         'rotating': False,
#         'flexible': False,
#         'remote': False,
#
#         'full': False,
#         'seasonal': False,
#         'partial': False,
#         'internship': False,
#         'part_time': False,
#
#         'inexperienced': False,
#         'one_to': False,
#         'one_to_three': False,
#         'three_to_six': False,
#         'from_six': False,
#     })
#
#     reply_markup = await add_vacancy_catalog_data(session)
#
#     await callback.message.edit_text(text='Давай выберем направление твоей работы:', reply_markup=reply_markup)
#     await callback.answer()
#
#     await state.set_state(StateVacancy.CATALOG)
#
#
# @vacancy_router.callback_query(F.data.startswith('catalog_'), StateVacancy.CATALOG)
# async def subcatalog_vacancy(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
#     catalog_id = int(callback.data.split('_')[-1])
#     await state.update_data({'catalog_id': catalog_id})
#     reply_markup = await add_vacancy_subcatalog_data(session, catalog_id)
#
#     await callback.message.edit_text(text='Давай выберем тип твоей работы:', reply_markup=reply_markup)
#     await callback.answer()
#
#     await state.set_state(StateVacancy.SUBCATALOG)
#
#
# # @user_router.callback_query(StateVacancy.CATALOG)
# # async def error_catalog_vacancy(callback: CallbackQuery, session: AsyncSession):
# #     reply_markup = await add_vacancy_catalog_data(session)
# #
# #     await callback.message.edit_text(text='Ошибка: Давай ещё раз выберем направление твоей работы:', reply_markup=reply_markup)
# #     await callback.answer()
#
#
# @vacancy_router.callback_query(F.data.startswith('subcatalog_'), StateVacancy.SUBCATALOG)
# async def name_vacancy(callback: CallbackQuery, state: FSMContext):
#     subcatalog_id = int(callback.data.split('_')[-1])
#     await state.update_data({'subcatalog_id': subcatalog_id})
#     reply_markup = await add_vacancy_name_data()
#
#     await callback.message.edit_text(text='Дай название своей професии', reply_markup=reply_markup)
#     await callback.answer()
#
#     await state.set_state(StateVacancy.NAME)
#
#
# # @user_router.callback_query(StateVacancy.SUBCATALOG)
# # async def error_subcatalog_vacancy(callback: CallbackQuery, session: AsyncSession):
# #     reply_markup = await add_vacancy_catalog_data(session)
# #
# #     await callback.message.answer(text='Ошибка: Давай ещё раз выберем направление твоей работы:',
# #                                   reply_markup=reply_markup)
# #     await callback.answer()
#
#
# @vacancy_router.message(StateVacancy.NAME)
# async def description_vacancy(message: Message, state: FSMContext):
#     await state.update_data({'name': message.text})
#     reply_markup = await add_vacancy_description_data()
#
#     await message.answer(text='Опиши свою вакансию: ', reply_markup=reply_markup)
#
#     await state.set_state(StateVacancy.DESCRIPTION)
#
#
# @vacancy_router.message(StateVacancy.DESCRIPTION)
# async def schedule_vacancy(message: Message, state: FSMContext):
#     await state.update_data({'description': message.text})
#     schedule_data = await state.get_data()
#
#     new_schedule_data = {}
#
#     for key, value in schedule_data.items():
#         if key in schedule_dict.keys():
#             new_schedule_data[key] = value
#
#     reply_markup = await add_vacancy_schedule_data(schedule_dict, new_schedule_data)
#
#     await message.answer(text='Вибери свой график работы и нажми далее!: ', reply_markup=reply_markup)
#
#     await state.set_state(StateVacancy.SCHEDULE)
#
#
# @vacancy_router.callback_query(ScheduleCallBack.filter(), StateVacancy.SCHEDULE)
# async def verification_schedule_vacancy(callback: CallbackQuery, callback_data: ScheduleCallBack, state: FSMContext):
#     schedule_data = await state.get_data()
#     await state.update_data({callback_data.name: False if schedule_data[callback_data.name] else True})
#
#     schedule_data = await state.get_data()
#
#     new_schedule_data = {}
#     for key, value in schedule_data.items():
#         if key in schedule_dict.keys():
#             new_schedule_data[key] = value
#
#     reply_markup = await add_vacancy_schedule_data(schedule_dict, new_schedule_data)
#
#     await callback.message.edit_text(text='Вибери свой график работы и нажми далее!: ', reply_markup=reply_markup)
#     await callback.answer()
#
#
# @vacancy_router.callback_query(F.data == 'next', StateVacancy.SCHEDULE)
# async def employment_vacancy(callback: CallbackQuery, state: FSMContext):
#     employment_data = await state.get_data()
#
#     new_employment_data = {}
#
#     for key, value in employment_data.items():
#         if key in employment_dict.keys():
#             new_employment_data[key] = value
#
#     reply_markup = await add_vacancy_employment_data(employment_dict, new_employment_data)
#
#     await callback.message.edit_text(text='Тип вашей занятости и нажми далее:', reply_markup=reply_markup)
#     await callback.answer()
#
#     await state.set_state(StateVacancy.EMPLOYMENT)
#
#
# @vacancy_router.callback_query(EmploymentCallBack.filter(), StateVacancy.EMPLOYMENT)
# async def verification_employment_vacancy(callback: CallbackQuery, callback_data: EmploymentCallBack, state: FSMContext):
#     employment_data = await state.get_data()
#     await state.update_data({callback_data.name: False if employment_data[callback_data.name] else True})
#
#     employment_data = await state.get_data()
#
#     new_employment_data = {}
#     for key, value in employment_data.items():
#         if key in employment_dict.keys():
#             new_employment_data[key] = value
#
#     reply_markup = await add_vacancy_employment_data(employment_dict, new_employment_data)
#
#     await callback.message.edit_text(text='Тип вашей занятости и нажми далее:', reply_markup=reply_markup)
#     await callback.answer()
#
#
# @vacancy_router.callback_query(F.data == 'next', StateVacancy.EMPLOYMENT)
# async def expertise_vacancy(callback: CallbackQuery, state: FSMContext):
#     expertise_data = await state.get_data()
#
#     new_expertise_data = {}
#
#     for key, value in expertise_data.items():
#         if key in expertise_dict.keys():
#             new_expertise_data[key] = value
#
#     reply_markup = await add_vacancy_expertise_data(expertise_dict, new_expertise_data)
#
#     await callback.message.edit_text(text='Какой опит необходим:', reply_markup=reply_markup)
#     await callback.answer()
#
#     await state.set_state(StateVacancy.EXPERTISE)
#
#
# @vacancy_router.callback_query(ExpertiseCallBack.filter(), StateVacancy.EXPERTISE)
# async def verification_expertise_vacancy(callback: CallbackQuery, callback_data: ExpertiseCallBack, state: FSMContext):
#     expertise_data = await state.get_data()
#     await state.update_data({callback_data.name: False if expertise_data[callback_data.name] else True})
#
#     expertise_data = await state.get_data()
#
#     new_expertise_data = {}
#     for key, value in expertise_data.items():
#         if key in expertise_dict.keys():
#             new_expertise_data[key] = value
#
#     reply_markup = await add_vacancy_expertise_data(expertise_dict, new_expertise_data)
#
#     await callback.message.edit_text(text='Тип вашей занятости и нажми далее:', reply_markup=reply_markup)
#     await callback.answer()
#
#
# @vacancy_router.callback_query(F.data == 'next', StateVacancy.EXPERTISE)
# async def disability_vacancy(callback: CallbackQuery, state: FSMContext):
#     reply_markup = await add_vacancy_disability_data()
#
#     await callback.message.edit_text(text='Инвалидность / Нет инвалидности:', reply_markup=reply_markup)
#     await callback.answer()
#
#     await state.set_state(StateVacancy.DISABILITY)
#
#
# @vacancy_router.callback_query(F.data.startswith('disability_'), StateVacancy.DISABILITY)
# async def language_vacancy(callback: CallbackQuery, state: FSMContext):
#     await state.update_data({'disability': True if callback.data.split('_')[-1] == 'true' else False})
#
#     reply_markup = await add_vacancy_language_data()
#
#     await callback.message.edit_text(text='Знание иностранного языка:', reply_markup=reply_markup)
#     await callback.answer()
#
#     await state.set_state(StateVacancy.LANGUAGE)
#
#
# @vacancy_router.callback_query(F.data.startswith('language_'), StateVacancy.LANGUAGE)
# async def price_vacancy(callback: CallbackQuery, state: FSMContext):
#     await state.update_data({'language': True if callback.data.split('_')[-1] == 'true' else False})
#
#     await callback.message.edit_text(text='Какова ваша зарплата:')
#     await callback.answer()
#
#     await state.set_state(StateVacancy.PRICE)
#
#
# @vacancy_router.message(StateVacancy.PRICE)
# async def region_vacancy(message: Message, state: FSMContext, session: AsyncSession):
#     await state.update_data({'price': message.text})
#
#     reply_markup = await add_vacancy_region_data(session)
#
#     await message.answer(text='Выберете свой регион: ', reply_markup=reply_markup)
#
#     await state.set_state(StateVacancy.REGION)
#
#
# @vacancy_router.callback_query(F.data.startswith('region_'), StateVacancy.REGION)
# async def city_vacancy(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
#     region_id = int(callback.data.split('_')[-1])
#     await state.update_data({'region_id': region_id})
#
#     reply_markup = await add_vacancy_city_data(session, region_id)
#
#     await callback.message.edit_text(text='Выберете свой город: ', reply_markup=reply_markup)
#
#     await state.set_state(StateVacancy.CITY)
#
#
# @vacancy_router.callback_query(F.data.startswith('city_'), StateVacancy.CITY)
# async def finish_vacancy(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
#     city_id = None if callback.data.split('_')[-1] == 'none' else int(callback.data.split('_')[-1])
#     await state.update_data({'city_id': city_id})
#
#     data_items = await state.get_data()
#     print(data_items)
#
#     await callback.message.edit_text(text='THE END')
#
#     await state.set_state(StateVacancy.CITY)
