from aiogram import Bot

from core.database.querys import deactivate_vacancy
from core.utils.settings import async_session_maker


async def scheduler_deactivate_vacancy(bot: Bot, chat_id: int, vacancy_id: int):
    async with async_session_maker() as session:
        await deactivate_vacancy(
            session=session,
            vacancy_id=vacancy_id,
            method='deactivate',
        )

    await bot.send_message(chat_id=chat_id, text='Ваше обьявление деактивировано!')
