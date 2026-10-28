from aiogram import BaseMiddleware

from app.infrastructure.database.repositories.user import UserRepo


class DataBaseMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        session_maker = data["session_maker"]
        async with session_maker() as session:
            data["session"] = session
            data["repo"] = UserRepo(session) 
            result = await handler(event, data)
            await session.commit()
            return result