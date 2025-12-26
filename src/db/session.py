"""Database session management."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import get_settings

settings = get_settings()

# Convert postgres:// to postgresql+asyncpg://
database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

# Create async database engine (don't specify poolclass for async)
engine = create_async_engine(
    database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,  # Test connection before using
    echo=settings.is_development,  # Log SQL in development
)

# Create async session factory
SessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)


async def get_db():
    """Get database session (FastAPI dependency)."""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
