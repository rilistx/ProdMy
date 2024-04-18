from aiogram.types import Message
from aiogram.filters import BaseFilter

from sqlalchemy.ext.asyncio import AsyncSession

from core.models.querys import search_user


class IsUserFilter(BaseFilter):
    async def __call__(self, message: Message, session: AsyncSession) -> bool:
        user = await search_user(session=session, user_id=message.from_user.id)

        if user:
            return True
        return False
