__all__ = ['start_polling']


from aiogram import Dispatcher
from aiogram.types import BotCommandScopeDefault

from core.commands.commands import commands
from core.handlers import main, registration, menu, vacancy, error  # noqa
from core.middlewares.session import SessionMiddleware
from core.utils.settings import bot, storage, schedulers, session_maker


async def start_polling() -> None:
    dispatcher = Dispatcher(storage=storage)

    dispatcher.include_router(main.main_router)
    dispatcher.update.middleware(SessionMiddleware(session_pool=session_maker))
    dispatcher.include_router(registration.registration_router)
    dispatcher.include_router(menu.menu_router)
    # dispatcher.include_router(vacancy.vacancy_router)
    dispatcher.include_router(error.error_router)

    schedulers.start()

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.delete_my_commands(scope=BotCommandScopeDefault())
        await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
        await dispatcher.start_polling(bot, allowed_updates=dispatcher.resolve_used_update_types())
    finally:
        await bot.session.close()
