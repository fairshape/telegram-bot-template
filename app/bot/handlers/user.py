import logging

from aiogram import Router, Bot
from aiogram.enums import BotCommandScopeType
from aiogram.types import Message, BotCommandScopeChat, ChatMemberUpdated
from aiogram.filters import KICKED, CommandStart, ChatMemberUpdatedFilter

from app.bot.enums.roles import UserRole
from app.bot.i18n.translator import Translator
from app.infrastructure.database.repositories.user import UserRepo
from app.bot.keyboards.menu_button import get_main_menu_commands

logger = logging.getLogger(__name__)

user_router = Router()

@user_router.message(CommandStart())
async def process_command_start(
    message: Message,
    i18n: Translator,
    bot: Bot,
    admin_ids: list,
    repo: UserRepo,
):
    if not message.from_user:
        return
    user_row = await repo.get(user_id=message.from_user.id)

    if user_row is None:
        if message.from_user.id in admin_ids:
            user_role = UserRole.ADMIN
        else:
            user_role = UserRole.USER

        await repo.add(
            user_id=message.from_user.id,
            username=message.from_user.username,
            language=(message.from_user.language_code if message.from_user.language_code else "en"),
            role=user_role,
        )
    else:
        user_role = user_row.role
        await repo.set_alive(user_id=message.from_user.id, is_alive=True)
    
    await bot.set_my_commands(
        commands=get_main_menu_commands(i18n=i18n, role=user_role),
        scope=BotCommandScopeChat(
            type=BotCommandScopeType.CHAT,
            chat_id=message.from_user.id,
        )
    )

    await message.answer(i18n.get("start"))

@user_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def process_user_blocked_bot(event: ChatMemberUpdated, repo: UserRepo):
    logger.info("User %d has blocked the bot", event.from_user.id)
    await repo.set_alive(user_id=event.from_user.id, is_alive=False)