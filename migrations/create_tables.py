import asyncio
import logging

from app.infrastructure.database.base import Base
from app.infrastructure.database import models  # noqa: F401 (без этого таблицы не увидит Base)
from app.infrastructure.database.session import create_engine
from config.config import load_config

logger = logging.getLogger(__name__)


async def create_tables() -> None:
    config = load_config()

    engine = create_engine(
        host=config.db.host,
        port=config.db.port,
        user=config.db.user,
        password=config.db.password,
        db=config.db.name,
    )

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(create_tables())