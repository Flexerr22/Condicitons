import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from app.handlers import router

async def set_default_commands(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/help", description="Помощь"),
        BotCommand(command="/clear", description="Очистить бота"),
    ])

async def main():
    bot = Bot(token='7641008131:AAHY5nGar9rIG0xEBr7duB1bElV1AgaV1Ns')
    dp = Dispatcher()
    dp.include_router(router)
    await set_default_commands(bot)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот закрыт')