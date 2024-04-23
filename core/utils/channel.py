from aiogram import Bot

from core.database.models import Vacancy


# from core.utils.settings import async_session_maker, channel


async def vacancy_channel(bot: Bot, data: Vacancy) -> None:
    # await bot.send_message(chat_id=channel, text='Новая вакансия!')
    pass
