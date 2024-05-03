from aiogram import Bot

from core.database.querys import deactivate_vacancy
from core.keyboards.vacancy import get_activate_vacancy_button
from core.utils.connector import connector
from core.utils.settings import async_session_maker


async def scheduler_deactivate_vacancy(
        bot: Bot,
        lang: str,
        chat_id: int,
        vacancy_id: int,
) -> None:
    async with async_session_maker() as session:
        await deactivate_vacancy(
            session=session,
            vacancy_id=vacancy_id,
            method='deactivate',
        )

    text = f"🥺 {connector[lang]['message']['vacancy']['deactivate']}!"
    reply_markup = get_activate_vacancy_button(lang=lang, vacancy_id=vacancy_id)

    await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
