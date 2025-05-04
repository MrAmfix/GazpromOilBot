from aiogram import BaseMiddleware
from database.gen_session import get_session


class DBSessionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        async for session in get_session():
            data["session"] = session
            result = await handler(event, data)
            return result
