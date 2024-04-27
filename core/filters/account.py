from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import BaseFilter

from core.utils.connector import connector


class CancelFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        lang = (await state.get_data())['lang']

        if message.text == connector[lang]['button']['navigation']['cancel']:
            return True
        return False


class NameFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        if len(message.text) <= 30:
            return True
        return False
