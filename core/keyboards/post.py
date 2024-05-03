from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


def get_chat_button(
        sizes: tuple[int] = (2,),
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(
        InlineKeyboardButton(
            text='🤖 bot',
            url="https://t.me/wadsworkbot",
        )
    )

    keyboard.add(
        InlineKeyboardButton(
            text='💬 chat',
            url="https://t.me/wadsworkchat",
        )
    )

    return keyboard.adjust(*sizes).as_markup()
