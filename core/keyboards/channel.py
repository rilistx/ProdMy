from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


def get_channel_button(
        sizes: tuple[int] = (2,),
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(
        text='@wadsworkbot',
        url="https://t.me/wadsworkbot",
    ))

    return keyboard.adjust(*sizes).as_markup()
