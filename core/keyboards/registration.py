from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton, InlineKeyboardBuilder

from core.utils.connector import connector
from core.utils.settings import support


def get_contact_button(
        lang: str,
        sizes: tuple[int] = (2,),
):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
        KeyboardButton(
            text=f"{connector[lang]['button']['registration']['contact']} 📱",
            request_contact=True
        )
    )

    return keyboard.adjust(*sizes).as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_support_button(
        lang: str,
        sizes: tuple[int] = (2,),
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(
        InlineKeyboardButton(
            text=f"⚙️ {connector[lang]['button']['menu']['support']}",
            url=f"https://t.me/{support}",
        )
    )

    return keyboard.adjust(*sizes).as_markup()


def get_channel_button(
        lang: str,
        sizes: tuple[int] = (2,),
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(
        InlineKeyboardButton(
            text=f"📺 {connector[lang]['button']['about']['channel']}",
            url="https://t.me/wadsworkua",
        )
    )

    return keyboard.adjust(*sizes).as_markup()
