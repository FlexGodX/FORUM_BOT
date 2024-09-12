from aiogram import Bot
from aiogram.types import BotCommand

from lexicon.lexicon import Lexicon_commands


# Функция для настройки кнопки Menu бота
async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(
            command=command,
            description=description
        ) for command, description in Lexicon_commands.items()
    ]
    await bot.set_my_commands(main_menu_commands)