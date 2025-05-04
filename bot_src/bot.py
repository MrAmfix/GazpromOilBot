import asyncio
from aiogram import Bot, Dispatcher
from bot_src.middleware.session_middleware import DBSessionMiddleware
from database.config import BOT_TOKEN
from bot_src.routers.user import urt


tgbot = Bot(token=BOT_TOKEN)


async def main():
    print('Bot started')
    dp = Dispatcher()
    dp.update.outer_middleware(DBSessionMiddleware())
    dp.include_router(urt)
    await tgbot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(tgbot, allowed_updates=dp.resolve_used_update_types())

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')
