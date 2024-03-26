from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from sqlalchemy.ext.asyncio import async_sessionmaker

from .handlers import routers
from .settings import async_session


# Middleware
class SessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data['session'] = session
            return await handler(event, data)


# class UserNameMiddleware(BaseMiddleware):
#     def __init__(self, session_pool: async_sessionmaker):
#         self.session_pool = session_pool
#
#     async def __call__(
#         self,
#         handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
#         event: TelegramObject,
#         data: Dict[str, Any],
#     ) -> Any:
#         async with self.session_pool() as session:
#             while True:
#                 username = str(random.randint(10000000, 99999999))
#                 result = await search_username(session, username)
#
#                 if not result:
#                     break
#
#             data['create_username'] = username
#             return await handler(event, data)


def middlewares():
    routers['user_router'].message.middleware(SessionMiddleware(session_pool=async_session))
