from aiogram.types import BotCommand


commands = [
        BotCommand(command='menu', description='Главное меню'),
        BotCommand(command='catalog', description='Каталог обьявлений'),
        BotCommand(command='profile', description='Твой профиль'),
        BotCommand(command='new_product', description='Создать новое обьявление'),
        BotCommand(command='your_product', description='Твои обьявления'),
        BotCommand(command='about', description='Информация о нас'),
        BotCommand(command='support', description='Техническая поддержка'),
    ]
