from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import User


class UserRepo:
    """Все операции с таблицей users. Коммит здесь НЕ делается: его делает DataBaseMiddleware."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: int) -> User | None:
        """Пользователь по Telegram id или None."""
        return await self.session.scalar(
            select(User).where(User.user_id == user_id)
        )

    async def add(
        self, user_id: int, username: str | None, language: str, role: str,
    ) -> bool:
        """Создать пользователя. True, если создан; False, если уже был."""
        stmt = (
            insert(User)
            .values(
                user_id=user_id,
                username=username,
                language=language,
                role=role,
                is_alive=True,
                banned=False,
            )
            .on_conflict_do_nothing(index_elements=["user_id"])
            .returning(User.id)
        )
        new_id = await self.session.scalar(stmt)
        return new_id is not None

    async def get_role(self, user_id: int) -> str | None:
        return await self.session.scalar(
            select(User.role).where(User.user_id == user_id)
        )
    
    async def get_banned_status(self, user_id: int) -> bool | None:
        """True/False: забанен ли пользователь. None: пользователя нет в базе."""
        return await self.session.scalar(
            select(User.banned).where(User.user_id == user_id)
        )

    async def _set(self, user_id: int, **fields) -> bool:
        """Обновить поля. True, если пользователь найден и обновлён."""
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(**fields)
            .returning(User.id)
        )
        return await self.session.scalar(stmt) is not None

    async def set_language(self, user_id: int, language: str) -> bool:
        return await self._set(user_id, language=language)

    async def set_banned(self, user_id: int, banned: bool) -> bool:
        return await self._set(user_id, banned=banned)

    async def set_alive(self, user_id: int, is_alive: bool) -> bool:
        return await self._set(user_id, is_alive=is_alive)

    async def all_active(self) -> list[User]:
        """Для рассылки: не забаненные и живые."""
        result = await self.session.scalars(
            select(User).where(User.banned.is_(False), User.is_alive.is_(True))
        )
        return list(result)

    async def count(self) -> int:
        """Сколько всего пользователей."""
        return await self.session.scalar(select(func.count(User.id))) or 0