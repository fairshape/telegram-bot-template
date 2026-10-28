from aiogram import BaseMiddleware


class UserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        data["user"] = None
        tg_user = data.get("event_from_user")

        if tg_user:
            repo = data["repo"]
            user = await repo.get(tg_user.id)
            if user and user.username != tg_user.username:
                await repo.set_username(tg_user.id, tg_user.username)
            data["user"] = user

        return await handler(event, data)