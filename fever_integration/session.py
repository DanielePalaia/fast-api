from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .config import settings

# Async engine with asyncpg driver
engine = create_async_engine(settings.DB_URL, echo=True)

# Async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Async dependency for getting a SQLAlchemy async session"""
    async with AsyncSessionLocal() as session:
        yield session
