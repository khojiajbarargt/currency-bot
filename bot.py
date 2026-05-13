import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.convert import router as convert_router
from handlers.ai import router as ai_router
from handlers.alerts import router as alerts_router, check_alerts
from db import init_db

async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(convert_router)
    dp.include_router(alerts_router)
    dp.include_router(ai_router)
    asyncio.create_task(check_alerts(bot))
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())