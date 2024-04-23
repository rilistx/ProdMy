from aiogram import Bot

from core.utils.settings import channel


async def vacancy_channel(bot: Bot) -> None:
    await bot.send_message(chat_id=channel, text='Новая вакансия!')
