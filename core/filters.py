from aiogram.types import Message
from aiogram.filters import BaseFilter


class IsContactFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.contact or not message.contact and message.text.isdigit() and len(message.text) == 12:
            return True
        return False
