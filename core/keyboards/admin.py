from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from core.keyboards.menu import MenuCallBack
from core.utils.connector import connector


def get_admin_vacancy_button(
        lang: str,
        vacancy_id: int,
        sizes: tuple[int] = (2,),
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(
        InlineKeyboardButton(
            text=f"👀 {connector[lang]['button']['vacancy']['show']}",
            callback_data=MenuCallBack(
                lang=lang,
                view='your',
                level=4,
                key='description',
                vacancy_id=vacancy_id,
            ).pack()
        )
    )

    return keyboard.adjust(*sizes).as_markup(resize_keyboard=True, one_time_keyboard=True)
