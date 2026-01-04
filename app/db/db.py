from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager

from app.settings.config import env

DATABASE_URL=f'postgresql+asyncpg://{env.DATABASE_USER}:{env.DATABASE_PASSWORD}@{env.DATABASE_HOST}:{env.DATABASE_PORT}/{env.DATABASE_NAME}'

engine: AsyncEngine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    pool_size=20, 
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

@asynccontextmanager
async def get_session():
    async with SessionLocal() as session:
        yield session

async def close_db():
    await engine.dispose()
