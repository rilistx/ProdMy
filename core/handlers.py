from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from .filters import IsContactFilter
from .keyboards import contact_reply_keyboard
from .querys import create_db, drop_db, search_user, create_user, create_username
from .settings import admin
from .states import StateRegistration


routers = {
    'main_router': Router(),
    'user_router': Router(),
}


# ########################################   RUN \ STOP   ############################################### #

@routers['main_router'].startup()
async def run(bot: Bot) -> None:
    await create_db()
    await bot.send_message(admin, text='Run bot 👍🏻')


@routers['main_router'].shutdown()
async def stop(bot: Bot, dispatcher: Dispatcher) -> None:
    await dispatcher.storage.close()
    await drop_db()
    await bot.send_message(admin, text='Stop bot 👎🏻')


# ########################################   START   ############################################### #

@routers['user_router'].message(CommandStart())
async def start(message: Message, state: FSMContext, session: AsyncSession):
    user_exist = await search_user(session, message.from_user.id)
    if user_exist:
        await message.answer('Оффф!!! Вы уже зарегестрированы!')
        await state.clear()
        return await menu(message)

    await state.set_state(StateRegistration.PHONE)

    await message.answer(
        'Добро пожаловать в ProdMy!\n'
        'Напишите ваш номер телефона или нажми на него для потдерждения:',
        reply_markup=contact_reply_keyboard,
    )


@routers['user_router'].message(StateRegistration.PHONE, IsContactFilter())
async def contact(message: Message, state: FSMContext, session: AsyncSession):
    await create_user(
        session,
        user_id=message.from_user.id,
        username=await create_username(session),
        first_name=message.contact.first_name if message.contact else None,
        phone_number=message.contact.phone_number if message.contact else message.text,
    )

    await message.answer('Ура!!! Поздравляем вас с успешной регестрацией!', reply_markup=ReplyKeyboardRemove())
    await state.clear()
    return await menu(message=message)


@routers['user_router'].message(StateRegistration.PHONE)
async def fake_contact(message: Message) -> None:
    await message.answer('Ошибка: Номер не является действителен!')


# ########################################   MENU   ############################################### #

@routers['user_router'].message(Command(commands='menu'))
async def menu(message: Message) -> None:
    await message.answer('Это главное меню пользователя!')


# ########################################   ERROR   ############################################### #

@routers['user_router'].message()
async def error(message: Message) -> None:
    await message.answer('Ошибка! Неизвестная команда.')


def include_routers(dispatcher: Dispatcher):
    for key, value in routers.items():
        dispatcher.include_router(routers[key])
