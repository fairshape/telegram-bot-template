from aiogram import BaseMiddleware

from app.bot.i18n.translator import TranslatorHub


class I18nMiddleware(BaseMiddleware):
    def __init__(self, hub: TranslatorHub):
        self.hub = hub

    async def __call__(self, handler, event, data):
        user = data.get("user")
        tg_user = data.get("event_from_user")

        if user is not None:
            code = user.language
        else:
            code = tg_user.language_code if tg_user else None

        data["i18n"] = self.hub.get_translator(code)
        return await handler(event, data)