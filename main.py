
import asyncio #для раброты асинхронных функций
import logging #для логирования

from aiogram import Bot, Dispatcher #классы бота и диспетчера
from aiogram.client.default import DefaultBotProperties #дополнительные параметры для классы бот
from aiogram.enums import ParseMode #режим парсинга
from config_data.config import Config, load_config # испортируем класс конфиг и функцию для загрузки конфига
from aiogram.fsm.storage.memory import MemoryStorage


from general_handlers import command_handlers, other_handlers #
from Module_Base import handlers_base
from keyboards.set_menu import set_main_menu

# Инициализируем логгер
logger = logging.getLogger(__name__)

storage = MemoryStorage()

#создаенм основной цикл, вкотором все будет работать
async def main():
     # Конфигурируем логирование
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')
    
 
    config: Config = load_config()
    bot = Bot(token=config.tg_bot.token, default= DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=storage)

    #устанавливаем меню
    await set_main_menu(bot)

    # Регистриуем роутеры
    logger.info('Подключаем роутеры')
    dp.include_router(command_handlers.router)
    dp.include_router(handlers_base.router)
    #dp.include_router(other_handlers.router)
    
    #await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
