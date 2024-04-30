from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


def get_chat_button(
        sizes: tuple[int] = (2,),
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(
        text='@wadsworkchat',
        url="https://t.me/wadsworkchat",
    ))

    return keyboard.adjust(*sizes).as_markup()
