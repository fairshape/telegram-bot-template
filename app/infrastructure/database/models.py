from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)  # SERIAL PRIMARY KEY
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    language: Mapped[str] = mapped_column(String(10))
    role: Mapped[str] = mapped_column(String(30))
    is_alive: Mapped[bool] = mapped_column(Boolean)
    banned: Mapped[bool] = mapped_column(Boolean)