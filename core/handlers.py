from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from .filters import IsContactFilter
from .keyboards import contact_reply_keyboard
from .querys import create_db, drop_db, search_user
from .settings import admin
from .states import StateRegistration


routers = {
    'main_router': Router(),
    'user_router': Router(),
}


# Run \ Stop
@routers['main_router'].startup()
async def run(bot: Bot) -> None:
    await create_db()
    await bot.send_message(admin, text='Run bot 👍🏻')


@routers['main_router'].shutdown()
async def stop(bot: Bot, dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await drop_db()
    await bot.send_message(admin, text='Stop bot 👎🏻')


# Handlers
@routers['user_router'].message(CommandStart())
async def start(message: Message, state: FSMContext, session):
    user_exist = await search_user(session, message.from_user.id)
    if user_exist:
        await message.answer('Оффф!!! Вы уже зарегестрированы!')
        await state.clear()
        return await menu(message)

    await state.set_state(StateRegistration.PHONE)

    await message.answer(
        'Добро пожаловать в ProdMy!\n'
        'Напишите ваш номер телефона или нажми на него для потдерждения:',
        reply_markup=contact_reply_keyboard(),
    )


@routers['user_router'].message(StateRegistration.PHONE, IsContactFilter())
async def contact(message: Message, state: FSMContext):
    await message.answer('Ура!!! Поздравляем вас с успешной регестрацией!')
    await state.clear()
    return await menu(message=message)


@routers['user_router'].message(StateRegistration.PHONE)
async def fake_contact(message: Message):
    await message.answer('Ошибка! Номер не действителен.')


@routers['user_router'].message(Command(commands='menu'))
async def menu(message: Message):
    await message.answer('Это главное меню пользователя!')


@routers['user_router'].message()
async def error(message: Message):
    await message.answer('Ошибка! Неизвестная команда.')


def include_routers(dispatcher: Dispatcher):
    for key, value in routers.items():
        dispatcher.include_router(routers[key])
