from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.i18n.translator import Translator


class LangCb(CallbackData, prefix="lang"):
    code: str

def create_lang_keyboard(i18n: Translator) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for code in sorted(i18n.hub.locales):
        name = i18n.hub.get_translator(code).get("lang-name")
        mark = "✅ " if code == i18n.locale else ""   
        kb.button(text=f"{mark}{name}", callback_data=LangCb(code=code))
    kb.adjust(2)
    return kb.as_markup()