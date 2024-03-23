__all__ = [
    'session_bot', 'start_bot', 'stop_bot',
    ]


from aiogram import Router

from core.database.engine import async_session
from core.views.middlewares.database import DataBaseSession

from .handlers.main import start, stop


# Session Database
def session_bot(router: Router) -> None:
    router.message.middleware.register(DataBaseSession(session_pool=async_session))


# Start bot
def start_bot(router: Router) -> None:
    router.startup.register(start)


# Stop bot
def stop_bot(router: Router) -> None:
    router.shutdown.register(stop)
