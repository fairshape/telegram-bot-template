from aiogram.types import BotCommand

from app.bot.enums.roles import UserRole
from app.bot.i18n.translator import Translator


def get_main_menu_commands(
    i18n: Translator, role: UserRole | str
) -> list[BotCommand]:
    commands = [
        BotCommand(
            command='/start',
            description=i18n.get('start_description')
        ),
        BotCommand(
            command="/lang",
            description=i18n.get('lang-description')
        )
    ]

    if role == UserRole.ADMIN:
        commands += [
            BotCommand(
                command='/ban',
                description=i18n.get('ban_description')
            ),
            BotCommand(
                command='/unban',
                description=i18n.get('unban_description')
            ),
        ]

    return commands