import asyncio
from aiogram import Dispatcher

from app.routers import router
from app.settings.locales import LocaleMiddleware
from app.db.cache import init_cache, close_cache
from app.settings.log import get_logger, setup_aiogram_logger
from app.settings.utils import tasker
from app.db.db import close_db
from app.db.init_db import init_database

from app.settings.factory import create_bot
from app.settings.middlewares import RateLimitMiddleware, cleanup_rate_limit

LOG = get_logger(__name__)

bot = create_bot()

async def main():
    setup_aiogram_logger()

    await init_database()
    await init_cache()

    dp = Dispatcher()
    dp.include_router(router)

    dp.message.middleware(LocaleMiddleware())
    dp.callback_query.middleware(LocaleMiddleware())

    limiter = RateLimitMiddleware(
        default_limit=0.8,
        custom_limits={
            '/start': 1,
            'add_funds': 1.0,
            'pm_ton': 5.0,
            'pm_stars': 5.0,
            'buy_sub': 2.0,
            'sub_1m': 2.0,
            'sub_3m': 2.0,
            'sub_6m': 2.0,
            'sub_12m': 2.0,
        },
    )
    dp.message.middleware(limiter)
    dp.callback_query.middleware(limiter)

    rate_limit_cleanup_task = asyncio.create_task(
        cleanup_rate_limit(limiter, interval=3600, max_age=3600)
    )

    LOG.info("Bot started...")

    try:
        await dp.start_polling(bot)
    finally:
        rate_limit_cleanup_task.cancel()

        try:
            await rate_limit_cleanup_task
        except asyncio.CancelledError:
            pass

        await bot.session.close()
        await close_db()
        await close_cache()
        LOG.info("Bot stopped cleanly")


if __name__ == "__main__":
    asyncio.run(main())