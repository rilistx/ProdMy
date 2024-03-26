__all__ = ['start_polling']


from aiogram import Dispatcher
from aiogram.types import BotCommandScopeDefault

from .commands import commands
from .handlers import include_routers
from .middlewares import middlewares
from .settings import bot, storage, schedulers


async def start_polling() -> None:
    dispatcher = Dispatcher(storage=storage)

    middlewares()
    include_routers(dispatcher)
    schedulers.start()

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.delete_my_commands(scope=BotCommandScopeDefault())
        await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()
