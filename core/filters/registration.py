from aiogram.types import Message
from aiogram.filters import BaseFilter


class IsContactFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.contact:
            return True
        return False
