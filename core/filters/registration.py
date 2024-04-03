from aiogram.types import Message
from aiogram.filters import BaseFilter

from core.commands.languages import json


class IsLanguageFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        language_list = []
        for key, value in json['ua']['language'].items():
            text = value['flag'] + ' ' + value['name']
            language_list.append(text)

        if message.text in language_list:
            return True
        return False


class IsContactFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.contact or not message.contact and message.text.isdigit():
            return True
        return False
