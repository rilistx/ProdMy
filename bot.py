import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.redis import RedisStorage

from core.commands.commands import commands
from core.scheduler.tasks import scheduler_tasks
from core.utils import dispatchers, environments

bot = Bot(token=environments.envs['bot_token'], parse_mode='HTML')


async def main() -> None:
    # Logging DEBUG on console
    logging.basicConfig(level=logging.DEBUG)

    # Start Polling Bot
    try:
        # Redis Storage
        storage = RedisStorage.from_url('redis://localhost:6379/0')

        # Create Dispatcher
        dispatcher = Dispatcher(storage=storage)

        dispatchers.all_dispatchers(dispatcher)

        # Time Tasks
        scheduler = scheduler_tasks()
        scheduler.start()

        await bot.delete_webhook(drop_pending_updates=True)
        await bot.delete_my_commands(scope=types.BotCommandScopeDefault())
        await bot.set_my_commands(commands=commands, scope=types.BotCommandScopeDefault())
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('This bot stopped!')
