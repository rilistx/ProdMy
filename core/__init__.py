__all__ = ['start_polling']


from aiogram import Dispatcher
from aiogram.types import BotCommandScopeDefault

from core.commands.commands import commands
from core.handlers import main, registration, menu, vacancy, account, admin, error
from core.middlewares.session import SessionMiddleware
from core.middlewares.scheduler import SchedulerMiddleware
from core.schedulers.post import scheduler_channel_post
from core.utils.settings import bot, channel, storage, async_session_maker, async_scheduler


async def start_polling() -> None:
    dispatcher = Dispatcher(storage=storage)

    scheduler = async_scheduler()

    scheduler.add_job(
        scheduler_channel_post,
        id='channel_post',
        replace_existing=True,
        trigger='cron',
        minute='0',
        hour='18',
        kwargs={'chat_id': channel},
    )

    scheduler.start()

    dispatcher.update.middleware(SessionMiddleware(session_pool=async_session_maker))
    dispatcher.update.middleware(SchedulerMiddleware(scheduler=scheduler))
    dispatcher.include_router(main.main_router)
    dispatcher.include_router(registration.registration_router)
    dispatcher.include_router(menu.menu_router)
    dispatcher.include_router(vacancy.vacancy_router)
    dispatcher.include_router(account.account_router)
    dispatcher.include_router(admin.admin_router)
    dispatcher.include_router(error.error_router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.delete_my_commands(scope=BotCommandScopeDefault())
        await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
        await dispatcher.start_polling(bot, allowed_updates=dispatcher.resolve_used_update_types())
    finally:
        await bot.session.close()
