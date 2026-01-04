import asyncio
from aiogram import Dispatcher

from app.routers import router
from app.settings.factory.factory import create_bot
from app.settings.locales.locales_mw import LocaleMiddleware
from app.db.cache import init_cache, close_cache
from app.settings.middlewares.rate_limit import RateLimitMiddleware, cleanup_rate_limit
from app.settings.log.logging import get_logger, setup_aiogram_logger
from app.db.db import close_db
from app.db.init import init_database
from app.settings.tasks import tasker

LOG = get_logger(__name__)


async def main():
    setup_aiogram_logger()

    bot = create_bot()

    await init_database()
    await init_cache()

    dp = Dispatcher()
    dp.include_router(router)

    dp.message.middleware(LocaleMiddleware())
    dp.callback_query.middleware(LocaleMiddleware())

    limiter = RateLimitMiddleware(
        default_limit=0.8,
        custom_limits={
            "/start": 1.5,
            "add_funds": 3.0,
            "pm_ton": 5.0,
            "pm_stars": 5.0,
            "buy_sub": 3.0,
            "sub_1m": 2.0,
            "sub_3m": 2.0,
            "sub_6m": 2.0,
            "sub_12m": 2.0,
        },
    )

    dp.message.middleware(limiter)
    dp.callback_query.middleware(limiter)

    rate_limit_cleanup_task = asyncio.create_task(
        cleanup_rate_limit(limiter, interval=3600, max_age=3600)
    )

    await tasker.start(bot)
    LOG.info("Bot started...")

    try:
        await dp.start_polling(bot)
    finally:
        rate_limit_cleanup_task.cancel()
        await tasker.stop()

        await bot.session.close()
        await close_db()
        await close_cache()

        LOG.info("Bot stopped cleanly")


if __name__ == "__main__":
    asyncio.run(main())