from aiogram.types import Message
from aiogram.filters import BaseFilter

from core.utils.connector import connector


class CatalogFilter(BaseFilter):
    async def __call__(self, message: Message, lang) -> bool:
        for _, value in connector[lang]['catalog'].items():
            if message.text.split(' ')[0] == value['logo']:
                return True
        return False


class SubcatalogFilter(BaseFilter):
    async def __call__(self, message: Message, lang) -> bool:
        for _, value in connector[lang]['catalog'].items():
            for _, subcatalog in value['subcatalog'].items():
                if message.text == subcatalog:
                    return True
        return False


class ChoiceFilter(BaseFilter):
    async def __call__(self, message: Message, lang) -> bool:
        if (message.text == '✅ ' + connector[lang]['button']['yes']
                or message.text == '❎ ' + connector[lang]['button']['not']):
            return True
        return False


class PriceFilter(BaseFilter):
    async def __call__(self, message: Message, lang) -> bool:
        if message.text.isdigit():
            return True
        return False


class RegionFilter(BaseFilter):
    async def __call__(self, message: Message, lang) -> bool:
        for _, country in connector[lang]['country'].items():
            for _, region in country['region'].items():
                if message.text == region['name']:
                    return True
        return False


class CityFilter(BaseFilter):
    async def __call__(self, message: Message, lang) -> bool:
        if message.text == connector[lang]['button']['skip']:
            return True

        for _, country in connector[lang]['country'].items():
            for _, region in country['region'].items():
                for _, city in region['city'].items():
                    if message.text == city:
                        return True
        return False
