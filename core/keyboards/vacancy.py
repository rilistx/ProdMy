# from aiogram.filters.callback_data import CallbackData
# from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
#
# from core.commands.languages import json
#
#
# class ScheduleCallBack(CallbackData, prefix="schedule"):
#     name: str
#
#
# class EmploymentCallBack(CallbackData, prefix="employment"):
#     name: str
#
#
# class ExpertiseCallBack(CallbackData, prefix="employment"):
#     name: str
#
#
# def add_vacancy_catalog_button(all_catalog):
#     keyboard = InlineKeyboardBuilder()
#     for item in all_catalog:
#         keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f'catalog_{item.id}'))
#
#     keyboard.add(InlineKeyboardButton(text='Назад', callback_data=MenuCallBack(level=0, name='menu').pack()))
#     keyboard.add(InlineKeyboardButton(text='Выйти', callback_data=MenuCallBack(level=0, name='menu').pack()))
#
#     sizes = [2 for _ in range(len(all_catalog) // 2)] + [1] + [2]
#              if len(all_catalog) % 2 else [2 for _ in range(len(all_catalog) // 2)] + [2]
#
#     return keyboard.adjust(*sizes).as_markup()
#
#
# def add_vacancy_subcatalog_button(all_subcatalog):
#     keyboard = InlineKeyboardBuilder()
#     for item in all_subcatalog:
#         keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f'subcatalog_{item.id}'))
#
#     keyboard.add(InlineKeyboardButton(text='Назад', callback_data=MenuCallBack(level=0, name='menu').pack()))
#     keyboard.add(InlineKeyboardButton(text='Выйти', callback_data=MenuCallBack(level=0, name='menu').pack()))
#
#     sizes = [2 for _ in range(len(all_subcatalog) // 2)] + [1] + [2]
#              if len(all_subcatalog) % 2 else [2 for _ in range(len(all_subcatalog) // 2)] + [2]
#
#     return keyboard.adjust(*sizes).as_markup()
#
#
# def add_vacancy_keyboard_button():
#     keyboard = InlineKeyboardBuilder()
#
#     keyboard.add(InlineKeyboardButton(text='Назад', callback_data=MenuCallBack(level=0, name='menu').pack()))
#     keyboard.add(InlineKeyboardButton(text='Выйти', callback_data=MenuCallBack(level=0, name='menu').pack()))
#
#     return keyboard.adjust(2, ).as_markup()
#
#
# def add_vacancy_schedule_button(schedule_list, schedule_data):
#     keyboard = InlineKeyboardBuilder()
#
#     for name, description in schedule_list.items():
#         for key, value in schedule_data.items():
#             if name == key and value:
#                 keyboard.add(InlineKeyboardButton(text='✅ ' + description, callback_data=ScheduleCallBack(name=key).pack()))
#             if name == key and not value:
#                 keyboard.add(InlineKeyboardButton(text='❌ ' + description, callback_data=ScheduleCallBack(name=key).pack()))
#
#     keyboard.add(InlineKeyboardButton(text='Далее', callback_data='next'))
#     keyboard.add(InlineKeyboardButton(text='Назад', callback_data=MenuCallBack(level=0, name='menu').pack()))
#     keyboard.add(InlineKeyboardButton(text='Выйти', callback_data=MenuCallBack(level=0, name='menu').pack()))
#
#     sizes = [1 for _ in range(len(schedule_list))] + [1] + [2]
#
#     return keyboard.adjust(*sizes).as_markup()
#
#
# def add_vacancy_employment_button(employment_list, employment_data):
#     keyboard = InlineKeyboardBuilder()
#
#     for name, description in employment_list.items():
#         for key, value in employment_data.items():
#             if name == key and value:
#                 keyboard.add(InlineKeyboardButton(text='✅ ' + description, callback_data=EmploymentCallBack(name=key).pack()))
#             if name == key and not value:
#                 keyboard.add(InlineKeyboardButton(text='❌ ' + description, callback_data=EmploymentCallBack(name=key).pack()))
#
#     keyboard.add(InlineKeyboardButton(text='Далее', callback_data='next'))
#     keyboard.add(InlineKeyboardButton(text='Назад', callback_data=MenuCallBack(level=0, name='menu').pack()))
#     keyboard.add(InlineKeyboardButton(text='Выйти', callback_data=MenuCallBack(level=0, name='menu').pack()))
#
#     sizes = [1 for _ in range(len(employment_list))] + [1] + [2]
#
#     return keyboard.adjust(*sizes).as_markup()
#
#
# def add_vacancy_expertise_button(expertise_list, expertise_data):
#     keyboard = InlineKeyboardBuilder()
#
#     for name, description in expertise_list.items():
#         for key, value in expertise_data.items():
#             if name == key and value:
#                 keyboard.add(InlineKeyboardButton(text='✅ ' + description, callback_data=ExpertiseCallBack(name=key).pack()))
#             if name == key and not value:
#                 keyboard.add(InlineKeyboardButton(text='❌ ' + description, callback_data=ExpertiseCallBack(name=key).pack()))
#
#     keyboard.add(InlineKeyboardButton(text='Далее', callback_data='next'))
#     keyboard.add(InlineKeyboardButton(text='Назад', callback_data=MenuCallBack(level=0, name='menu').pack()))
#     keyboard.add(InlineKeyboardButton(text='Выйти', callback_data=MenuCallBack(level=0, name='menu').pack()))
#
#     sizes = [1 for _ in range(len(expertise_list))] + [1] + [2]
#
#     return keyboard.adjust(*sizes).as_markup()
#
#
# def add_vacancy_disability_button():
#     keyboard = InlineKeyboardBuilder()
#
#     keyboard.add(InlineKeyboardButton(text='✅ С инвалидностью', callback_data='disability_true'))
#     keyboard.add(InlineKeyboardButton(text='❌ Без инвалидности', callback_data='disability_false'))
#
#     keyboard.add(InlineKeyboardButton(text='Назад', callback_data=MenuCallBack(level=0, name='menu').pack()))
#     keyboard.add(InlineKeyboardButton(text='Выйти', callback_data=MenuCallBack(level=0, name='menu').pack()))
#
#     return keyboard.adjust(2, 2).as_markup()
#
#
# def add_vacancy_language_button():
#     keyboard = InlineKeyboardBuilder()
#
#     keyboard.add(InlineKeyboardButton(text='✅ Нужно', callback_data='language_true'))
#     keyboard.add(InlineKeyboardButton(text='❌ Не нужно', callback_data='language_false'))
#
#     keyboard.add(InlineKeyboardButton(text='Назад', callback_data=MenuCallBack(level=0, name='menu').pack()))
#     keyboard.add(InlineKeyboardButton(text='Выйти', callback_data=MenuCallBack(level=0, name='menu').pack()))
#
#     return keyboard.adjust(2, 2).as_markup()
#
#
# def add_vacancy_region_button(all_region):
#     keyboard = InlineKeyboardBuilder()
#     for item in all_region:
#         keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f'region_{item.id}'))
#
#     keyboard.add(InlineKeyboardButton(text='Назад', callback_data=MenuCallBack(level=0, name='menu').pack()))
#     keyboard.add(InlineKeyboardButton(text='Выйти', callback_data=MenuCallBack(level=0, name='menu').pack()))
#
#     sizes = [2 for _ in range(len(all_region) // 2)] + [1] + [2] if len(all_region) % 2 else [2 for _ in range(
#         len(all_region) // 2)] + [2]
#
#     return keyboard.adjust(*sizes).as_markup()
#
#
# def add_vacancy_city_button(city):
#     keyboard = InlineKeyboardBuilder()
#
#     for sub in city:
#         keyboard.add(InlineKeyboardButton(
#             text=sub.name,
#             callback_data=f'city_{sub.id}'
#         ))
#
#     keyboard.add(InlineKeyboardButton(text='Нет', callback_data=f'city_none'))
#
#     keyboard.add(InlineKeyboardButton(text='Назад', callback_data=MenuCallBack(level=0, name='menu').pack()))
#     keyboard.add(InlineKeyboardButton(text='Выйти', callback_data=MenuCallBack(level=0, name='menu').pack()))
#
#     sizes = [2 for _ in range((len(city) + 1) // 2)] + [1] + [2] if len(city) % 2 else [2 for _ in range((len(city) + 1) // 2)] + [2]
#
#     return keyboard.adjust(*sizes).as_markup()


# async def add_vacancy_catalog_data(session: AsyncSession):
#     all_catalog = await get_catalog(session)
#
#     button = add_vacancy_catalog_button(all_catalog)
#
#     return button
#
#
# async def add_vacancy_subcatalog_data(session: AsyncSession, catalog_id):
#     all_subcatalog = await get_subcatalog(session, catalog_id)
#
#     button = add_vacancy_subcatalog_button(all_subcatalog)
#
#     return button
#
#
# async def add_vacancy_name_data():
#     button = add_vacancy_keyboard_button()
#
#     return button
#
#
# async def add_vacancy_description_data():
#     button = add_vacancy_keyboard_button()
#
#     return button
#
#
# async def add_vacancy_schedule_data(schedule_list, schedule_data):
#     button = add_vacancy_schedule_button(schedule_list, schedule_data)
#
#     return button
#
#
# async def add_vacancy_employment_data(employment_list, employment_data):
#     button = add_vacancy_employment_button(employment_list, employment_data)
#
#     return button
#
#
# async def add_vacancy_expertise_data(expertise_list, expertise_data):
#     button = add_vacancy_expertise_button(expertise_list, expertise_data)
#
#     return button
#
#
# async def add_vacancy_disability_data():
#     button = add_vacancy_disability_button()
#
#     return button
#
#
# async def add_vacancy_language_data():
#     button = add_vacancy_language_button()
#
#     return button
#
#
# async def add_vacancy_region_data(session):
#     region = await get_region(session)
#
#     button = add_vacancy_region_button(region)
#
#     return button
#
#
# async def add_vacancy_city_data(session, region_id):
#     city = await get_city(session, region_id)
#
#     button = add_vacancy_city_button(city)
#
#     return button
