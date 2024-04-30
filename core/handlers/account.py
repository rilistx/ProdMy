from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from core.filters.account import CancelFilter, NameFilter
from core.handlers.menu import menu
from core.keyboards.account import account_name_button
from core.keyboards.menu import MenuCallBack
from core.database.querys import search_user, update_name_user
from core.states.account import StateAccount
from core.utils.connector import connector


account_router = Router()


@account_router.callback_query(MenuCallBack.filter(F.key == 'account'))
async def name_account_callback(
        callback: CallbackQuery,
        callback_data: MenuCallBack,
        state: FSMContext,
        session: AsyncSession
) -> None:
    await callback.message.delete()

    await state.update_data({
        'lang': callback_data.lang,
        'account_level': callback_data.level,
    })

    StateAccount.change = await search_user(session=session, user_id=callback.from_user.id)

    reply_markup = account_name_button(
        lang=callback_data.lang,
    )

    await callback.message.answer(
        text=connector[callback_data.lang]['message']['settings'][callback_data.data],
        reply_markup=reply_markup,
    )

    await callback.answer()
    await state.set_state(StateAccount.NAME)


@account_router.message(StateFilter(StateAccount), CancelFilter())
async def cancel_account(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()

    if StateAccount.change.first_name:
        text = connector[state_data['lang']]['message']['settings']['exit']['change']
    else:
        text = connector[state_data['lang']]['message']['settings']['exit']['create']

    await message.answer(
        text=text,
        reply_markup=ReplyKeyboardRemove(),
    )

    return_level = state_data['account_level']

    StateAccount.change = None
    await state.clear()

    return await menu(
        message=message,
        session=session,
        level=return_level,
        key='settings',
    )


@account_router.message(StateAccount.NAME, NameFilter())
async def finish_account(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()

    if message.text == StateAccount.change.first_name:
        text = connector[state_data['lang']]['message']['settings']['finish']['nochange']
    else:
        text = connector[state_data['lang']]['message']['settings']['finish']['change']

    if StateAccount.change.first_name != message.text:
        await update_name_user(session=session, user_id=message.from_user.id, first_name=message.text)

    await message.answer(
        text=text,
        reply_markup=ReplyKeyboardRemove(),
    )

    return_level = state_data['account_level']

    StateAccount.change = None
    await state.clear()

    return await menu(
        message=message,
        session=session,
        level=return_level,
        key='settings',
    )


@account_router.message(StateFilter(StateAccount))
async def error_account(message: Message) -> None:
    await message.delete()
