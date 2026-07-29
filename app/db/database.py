"""
Database configuration.

Provides:
- Async SQLAlchemy engine
- Async session factory
- FastAPI dependency
- Engine lifecycle management

Compatible with:
- SQLite (development)
- PostgreSQL (production)
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.models.base import Base

from app.core.config import settings
from app.core.logger import logger



# ---------------------------------------------------------
# Database Engine
# ---------------------------------------------------------

database_url = settings.DATABASE_URL

# Render provides PostgreSQL URLs like:
# postgresql://...
# SQLAlchemy async expects:
# postgresql+asyncpg://...

if database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://",
        "postgresql+asyncpg://",
        1,
    )

engine: AsyncEngine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
)


# ---------------------------------------------------------
# Session Factory
# ---------------------------------------------------------

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ---------------------------------------------------------
# Dependency Injection
# ---------------------------------------------------------

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an AsyncSession.
    """

    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ---------------------------------------------------------
# Database Lifecycle
# ---------------------------------------------------------

async def startup_database() -> None:
    """
    Initialize database resources.

    NOTE:
    Tables are NOT created here.
    Alembic migrations are responsible for schema creation.
    """

    logger.info("Database engine initialized.")


async def shutdown_database() -> None:
    """
    Dispose the SQLAlchemy engine.
    """

    logger.info("Closing database engine...")

    await engine.dispose()

    logger.info("Database engine closed.")