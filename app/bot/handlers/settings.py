from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.bot.i18n.translator import Translator
from app.infrastructure.database.repositories.user import UserRepo
from app.bot.keyboards.lang_kb import LangCb, create_lang_keyboard

settings_router = Router()

@settings_router.message(Command("lang"))
async def process_command_lang(message: Message, i18n: Translator):
    await message.answer(text=i18n.get("lang-choose"), reply_markup=create_lang_keyboard(i18n))

@settings_router.callback_query(LangCb.filter())
async def process_set_lang(
    callback: CallbackQuery,
    callback_data: LangCb,
    repo: UserRepo,
    i18n: Translator,
):
    code = callback_data.code
    
    if code not in i18n.hub.locales:
        await callback.answer()
        return
    
    found = await repo.set_language(callback.from_user.id, code)
    if not found:
        await callback.answer(text=i18n.get("err-need-start"), show_alert=True)
        return

    i18n = i18n.switch(code)
    
    if isinstance(callback.message, Message):
        await callback.message.edit_text(text=i18n.get("lang-changed"))
    await callback.answer()