from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from sqlalchemy.ext.asyncio import async_sessionmaker

from core.models.querys import search_user, get_language_one


class LanguageMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            user = await search_user(session, event.from_user.id)
            if user:
                lang = await get_language_one(session, user.language_id)
                data['lang'] = lang.abbreviation
                return await handler(event, data)
