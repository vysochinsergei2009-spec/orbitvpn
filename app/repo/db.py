from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager

from config import DATABASE_URL

print("DATABASE_URL:", DATABASE_URL)

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
