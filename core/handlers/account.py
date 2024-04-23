from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from core.filters.account import ExitFilter, NameFilter
from core.handlers.menu import menu
from core.keyboards.account import account_name_button
from core.keyboards.menu import MenuCallBack
from core.database.querys import search_user, update_name_user
from core.states.account import StateAccount
from core.utils.connector import connector  # noqa


account_router = Router()


@account_router.callback_query(MenuCallBack.filter(F.key == 'change'))
async def name_account_callback(callback: CallbackQuery, callback_data: MenuCallBack, state: FSMContext, session: AsyncSession) -> None:
    await callback.message.delete()

    await state.update_data({
        'account_lang': callback_data.lang,
        'account_level': callback_data.level,
        'account_key': callback_data.key,
    })

    user = await search_user(session=session, user_id=callback.message.from_user.id)

    StateAccount.change = user

    reply_markup = account_name_button(
        lang=callback_data.lang,
    )

    await callback.message.answer(
        text='Придумай новое себе имя!',
        reply_markup=reply_markup,
    )
    await callback.answer()
    await state.set_state(StateAccount.NAME)


@account_router.message(StateFilter(StateAccount), ExitFilter())
async def exit_account(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()

    await message.answer(
        text='Вы отменили действие!',
        reply_markup=ReplyKeyboardRemove(),
    )

    StateAccount.change = None
    await state.clear()

    return await menu(
        message=message,
        session=session,
        level=state_data['account_level'],
        key=state_data['account_key'],
    )


@account_router.message(StateAccount.NAME, NameFilter())
async def finish_account(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()

    await update_name_user(session=session, user_id=message.from_user.id, first_name=message.text)

    await message.answer(
        text='Вы изменили имя!',
        reply_markup=ReplyKeyboardRemove(),
    )

    StateAccount.change = None
    await state.clear()

    return await menu(
        message=message,
        session=session,
        level=state_data['account_level'],
        key=state_data['account_key'],
    )


@account_router.message(StateFilter(StateAccount))
async def error_account(message: Message) -> None:
    await message.delete()
