from aiogram.types import BotCommand


commands = [
        BotCommand(command='menu', description='Главное меню'),
        BotCommand(command='catalog', description='Каталог обьявлений'),
        BotCommand(command='profile', description='Твой профиль'),
        BotCommand(command='create', description='Создать новое обьявление'),
        BotCommand(command='your', description='Твои обьявления'),
        BotCommand(command='about', description='Информация о нас'),
        BotCommand(command='support', description='Техническая поддержка'),
    ]
