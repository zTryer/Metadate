import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db
from handlers import commands, photo, video

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
init_db()

async def main():
    dp.include_router(commands.router)
    dp.include_router(photo.router)
    dp.include_router(video.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
