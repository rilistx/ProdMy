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


class BackFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        button_back_list = [value['button']['back'] for _, value in connector.items()]

        if message.text in button_back_list:
            return True
        return False


class CatalogFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        state_data = await state.get_data()

        if message.text == 'Вихід':
            return True

        for _, value in connector[state_data['lang']]['catalog'].items():
            if message.text == value['logo'] + ' ' + value['name']:
                return True
        return False


class SubcatalogFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        state_data = await state.get_data()

        if message.text == 'Назад' or message.text == 'Вихід':
            return True

        for _, value in connector[state_data['lang']]['catalog'].items():
            for _, subcatalog in value['subcatalog'].items():
                if message.text == subcatalog:
                    return True
        return False


class NameFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        if message.text == 'Назад' or message.text == 'Вихід':
            return True

        if len(message.text) <= 60:
            return True
        return False


class DescriptionFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        if message.text == 'Назад' or message.text == 'Вихід':
            return True

        if 50 < len(message.text) < 1000:
            return True
        return False


class ChoiceFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        state_data = await state.get_data()

        if message.text == 'Назад' or message.text == 'Вихід':
            return True

        if (message.text == '✅ ' + connector[state_data['lang']]['button']['yes']
                or message.text == '❎ ' + connector[state_data['lang']]['button']['not']):
            return True
        return False


class PriceFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        if message.text == 'Назад' or message.text == 'Вихід':
            return True

        if message.text.isdigit():
            return True
        return False


class RegionFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        state_data = await state.get_data()

        if message.text == 'Назад' or message.text == 'Вихід':
            return True

        for _, country in connector[state_data['lang']]['country'].items():
            for _, region in country['region'].items():
                if message.text == region['name']:
                    return True
        return False


class CityFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        state_data = await state.get_data()

        if message.text == 'Назад' or message.text == 'Вихід' or message.text == connector['uk']['button']['skip']:
            return True

        for _, country in connector[state_data['lang']]['country'].items():
            for _, region in country['region'].items():
                for _, city in region['city'].items():
                    if message.text == city:
                        return True
        return False
