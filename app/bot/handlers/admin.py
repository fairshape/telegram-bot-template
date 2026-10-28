from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from app.bot.enums.roles import UserRole
from app.bot.filters.filters import UserRoleFilter
from app.bot.i18n.translator import Translator
from app.infrastructure.database.repositories.user import UserRepo


admin_router = Router()

admin_router.message.filter(UserRoleFilter(UserRole.ADMIN))

@admin_router.message(Command("ban"))
async def process_admin_ban_command(message: Message, command: CommandObject,repo: UserRepo, i18n: Translator):
    args = command.args

    if not args:
        await message.answer(i18n.get("empty_ban_answer"))
        return
    
    arg_user = args.split()[0].strip()

    if arg_user.isdigit():
        status = await repo.get_banned_status(user_id=int(arg_user))
    else:
        await message.reply(text=i18n.get('incorrect_ban_arg'))
        return

    if status is None:
        await message.reply(text=i18n.get('no_user'))
    elif status:
        await message.reply(text=i18n.get('already_banned'))
    else:
        await repo.set_banned(user_id=int(arg_user), banned=True)
        await message.reply(text='successfully_banned')

@admin_router.message(Command("unban"))
async def process_admin_unban_command(message: Message, command: CommandObject,repo: UserRepo, i18n: Translator):
    args = command.args

    if not args:
        await message.answer(i18n.get("empty_unban_answer"))
        return
    
    arg_user = args.split()[0].strip()

    if arg_user.isdigit():
        status = await repo.get_banned_status(user_id=int(arg_user))
    else:
        await message.reply(text=i18n.get('incorrect_unban_arg'))
        return

    if status is None:
        await message.reply(text=i18n.get('no_user'))
    elif not status:
        await message.reply(text=i18n.get('not_banned'))
    else:
        await repo.set_banned(user_id=int(arg_user), banned=False)
        await message.reply(text='successfully_unbanned')