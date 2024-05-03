from aiogram import Bot

from core.keyboards.post import get_chat_button


async def scheduler_channel_post(
        bot: Bot,
        chat_id: int,
) -> None:
    text = 'Пост каждый день '
    reply_markup = get_chat_button()

    await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
