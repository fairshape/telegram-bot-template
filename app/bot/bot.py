import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from app.bot.middlewares.database import DataBaseMiddleware
from app.bot.middlewares.user import UserMiddleware
from app.bot.middlewares.shadow_ban import ShadowBanMiddleware
from app.bot.middlewares.i18n import I18nMiddleware
from app.infrastructure.database.session import create_engine, create_session_maker
from config.config import Config
from app.bot.handlers.admin import admin_router
from app.bot.handlers.user import user_router
from app.bot.i18n.translator import TranslatorHub

logger = logging.getLogger(__name__)

async def main(config: Config) -> None:
    logger.info("Starting bot...")

    storage = RedisStorage(
        redis=Redis(
            host=config.redis.host,
            port=config.redis.port,
            db=config.redis.db,
            password=config.redis.password,
            username=config.redis.username,
        )
    )

    hub = TranslatorHub()
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)

    engine = create_engine(
        host=config.db.host,
        port=config.db.port,
        user=config.db.user,
        password=config.db.password,
        db=config.db.name,
    )
    session_maker = create_session_maker(engine)

    logger.info("Including routers...")
    dp.include_routers(admin_router, user_router)

    logger.info("Including middlewares...")
    dp.update.outer_middleware(DataBaseMiddleware())
    dp.update.outer_middleware(UserMiddleware())     
    dp.update.outer_middleware(ShadowBanMiddleware())    
    dp.update.outer_middleware(I18nMiddleware(hub))

    try:
        await dp.start_polling(
            bot,
            session_maker=session_maker,
            admin_ids=config.bot.admin_ids,
        )
    except Exception as e:
        logger.exception(e)
    finally:
        await engine.dispose()             
        logger.info("Connection to Postgres closed")


