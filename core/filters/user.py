from aiogram.types import Message
from aiogram.filters import BaseFilter
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.querys import search_user


class IsUserFilter(BaseFilter):
    async def __call__(self, message: Message, session: AsyncSession) -> bool:
        if await search_user(session, message.from_user.id):
            return True
        return False
