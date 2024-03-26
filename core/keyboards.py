from aiogram.utils.keyboard import ReplyKeyboardBuilder


def contact_reply_keyboard():
    contact = ReplyKeyboardBuilder()
    contact.button(text='Отправить номер телефона 📱', request_contact=True)
    contact.adjust(1)
    contact.as_markup(resize_keyboard=True, one_time_keyboard=True)
