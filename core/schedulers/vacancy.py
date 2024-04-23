from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.querys import deactivate_vacancy


async def scheduler_deactivate_vacancy(bot: Bot, session: AsyncSession, chat_id: int, vacancy_id: int):

    await deactivate_vacancy(
        session=session,
        vacancy_id=vacancy_id,
        method='deactivate',
    )

    await bot.send_message(chat_id=chat_id, text='Ваше обьявление деактивировано!')
