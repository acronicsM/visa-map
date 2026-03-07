import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from dotenv import load_dotenv

# Base class for your ORM models
Base = declarative_base()

load_dotenv()

def _get_database_url() -> str:
    """
    Build the async PostgreSQL URL from environment variables.

    Prefer a full DATABASE_URL if set; otherwise compose from parts:
    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB.
    """
    # If you prefer, you can set this directly, e.g.
    # DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "visamap")

    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"


DATABASE_URL = _get_database_url()

# Create the async engine
engine = create_async_engine(
    DATABASE_URL,
    future=True,
    echo=os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true",
)

# Factory for async sessions
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an AsyncSession.

    Usage:
        from fastapi import Depends
        from .database import get_db

        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session