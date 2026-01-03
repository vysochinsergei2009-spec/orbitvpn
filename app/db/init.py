from app.db.db import engine, Base
from app.utils.logging import get_logger

LOG = get_logger(__name__)


async def init_database():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        LOG.info("Database tables initialized successfully")
    except Exception as e:
        LOG.error(f"Error initializing database: {e}")
        raise
