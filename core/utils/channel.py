from aiogram import Bot

from sqlalchemy.ext.asyncio import AsyncSession

from core.database.querys import search_user, get_vacancy_one, update_channel
from core.utils.settings import channel


async def vacancy_channel(bot: Bot, session: AsyncSession, method: str, user_id: int, vacancy_id: int) -> None:
    user = await search_user(session=session, user_id=user_id)
    vacancy = await get_vacancy_one(session=session, vacancy_id=vacancy_id, user_id=user.id)

    text = ''

    if method == 'create':
        msg = await bot.send_message(chat_id=channel, text='Новая вакансия!')

        await update_channel(session=session, vacancy_id=vacancy.id, channel_id=msg.message_id)

    if method == 'update':
        await bot.edit_message_text(chat_id=channel, message_id=vacancy.channel_id, text='Вакансия обновлена!')
