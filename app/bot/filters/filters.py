from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message
from app.infrastructure.database.repositories.user import UserRepo

from app.bot.enums.roles import UserRole

class UserRoleFilter(BaseFilter):
    def __init__(self, *roles: str | UserRole):
        if not roles:
            raise ValueError("At least one role must be provided to UserRoleFilter.")
        
        self.roles = frozenset(
            UserRole(role) if isinstance(role, str) else role
            for role in roles
            if isinstance(role, (str ,UserRole))
        )

    async def __call__(self, event: Message | CallbackQuery, repo: UserRepo) -> bool:
        user = event.from_user
        if not user:
            return False

        role = await repo.get_role(user_id=user.id)
        if role is None:
            return False

        return role in self.roles