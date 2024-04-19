from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import BaseFilter

from core.utils.connector import connector


class ExitFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        button_exit_list = [value['button']['exit'] for _, value in connector.items()]

        if message.text in button_exit_list:
            return True
        return False


class NameFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        if len(message.text) <= 50:
            return True
        return False
