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
from core.utils.message import get_text_settings_name


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
        'account_method': callback_data.method,
        'account_view': callback_data.view,
        'account_level': callback_data.level,
    })

    StateAccount.change = await search_user(session=session, user_id=callback.from_user.id)

    text = get_text_settings_name(
        lang=callback_data.lang,
        func_name='name',
        change=True if StateAccount.change else False,
        data=callback_data.data,
    )
    reply_markup = account_name_button(
        lang=callback_data.lang,
    )

    await callback.message.answer(
        text=text,
        reply_markup=reply_markup,
    )

    await callback.answer()
    await state.set_state(StateAccount.NAME)


@account_router.message(StateFilter(StateAccount), CancelFilter())
async def cancel_account(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()

    text = get_text_settings_name(
        lang=state_data['lang'],
        func_name='cancel',
        change=True if StateAccount.change else False,
    )
    reply_markup = ReplyKeyboardRemove()

    await message.answer(
        text=text,
        reply_markup=reply_markup,
    )

    return_data = {
        'method': state_data['account_method'],
        'view': state_data['account_view'],
        'level': state_data['account_level'],
    }

    StateAccount.change = None
    await state.clear()

    return await menu(
        message=message,
        session=session,
        method=return_data['method'],
        view=return_data['view'],
        level=return_data['level'],
        key='confirm_user' if return_data['method'] else 'settings',
    )


@account_router.message(StateAccount.NAME, NameFilter())
async def finish_account(message: Message, state: FSMContext, session: AsyncSession) -> None:
    state_data = await state.get_data()

    if StateAccount.change.first_name != message.text:
        await update_name_user(session=session, user_id=message.from_user.id, first_name=message.text)

    text = get_text_settings_name(
        lang=state_data['lang'],
        func_name='finish',
        change=True if StateAccount.change.first_name != message.text else False,
    )
    reply_markup = ReplyKeyboardRemove()

    await message.answer(
        text=text,
        reply_markup=reply_markup,
    )

    return_data = {
        'method': state_data['account_method'],
        'view': state_data['account_view'],
        'level': state_data['account_level'],
    }

    StateAccount.change = None
    await state.clear()

    return await menu(
        message=message,
        session=session,
        method=return_data['method'],
        view=return_data['view'],
        level=return_data['level'],
        key='confirm_user' if return_data['method'] else 'settings',
    )


@account_router.message(StateFilter(StateAccount))
async def error_account(message: Message) -> None:
    await message.delete()
