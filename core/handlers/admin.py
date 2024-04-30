from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.querys import blocked_user, get_vacancy_one, delete_vacancy_user, create_complaint, delete_vacancy
from core.handlers.menu import redirector
from core.keyboards.menu import MenuCallBack


admin_router = Router()


@admin_router.callback_query(MenuCallBack.filter(F.key == 'moderation'))
async def catalog_vacancy_callback(
        callback: CallbackQuery,
        bot: Bot,
        callback_data: MenuCallBack,
        session: AsyncSession,
) -> None:
    vacancy = await get_vacancy_one(session=session, vacancy_id=callback_data.vacancy_id)

    if callback_data.method == 'blocked':
        await delete_vacancy_user(session=session, user_id=vacancy.user_id)
        await blocked_user(session=session, user_id=vacancy.user_id)

        text = 'Ваш профиль заблокирован все ващи вакансии удалены'

        await bot.send_message(chat_id=vacancy.user_id, text=text)
    elif callback_data.method == 'activate':
        await create_complaint(session=session, user_id=callback.from_user.id, vacancy_id=callback_data.vacancy_id)

        text = 'Ваш вакансия прошла модерацию и была одобрена'

        await bot.send_message(chat_id=vacancy.user_id, text=text)
    else:
        await delete_vacancy(session=session, vacancy_id=callback_data.vacancy_id)

        text = 'Ваш вакансия прошла модерацию и была удалена'

        await bot.send_message(chat_id=vacancy.user_id, text=text)

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
