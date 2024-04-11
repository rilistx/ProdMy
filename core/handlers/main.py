from aiogram import Bot, Dispatcher, Router

from core.models.auto import create_db, drop_db  # noqa
from core.utils.settings import admin


main_router = Router()


@main_router.startup()
async def run(bot: Bot) -> None:
    await create_db()
    await bot.send_message(admin, text='Run bot 👍🏻')


@main_router.shutdown()
async def stop(bot: Bot, dispatcher: Dispatcher) -> None:
    await dispatcher.storage.close()
    # await drop_db()
    await bot.send_message(admin, text='Stop bot 👎🏻')
