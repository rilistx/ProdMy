from aiogram import Bot

from core.keyboards.post import get_chat_button
from core.utils.message import get_text_scheduler_post
from core.utils.settings import default_language


async def scheduler_channel_post(
        bot: Bot,
        chat_id: int,
) -> None:
    text = await get_text_scheduler_post(
        lang=default_language,
    )
    reply_markup = get_chat_button()

    await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup,
    )
