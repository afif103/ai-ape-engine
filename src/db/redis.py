"""Redis client management."""

import redis
from redis.connection import ConnectionPool

from src.config import get_settings

settings = get_settings()

# Create connection pool
redis_pool = ConnectionPool.from_url(
    settings.redis_url,
    max_connections=settings.redis_max_connections,
    decode_responses=True,
)

# Create Redis client
redis_client = redis.Redis(connection_pool=redis_pool)


def get_redis():
    """Get Redis client (FastAPI dependency)."""
    return redis_client


def ping_redis() -> bool:
    """Check if Redis is available."""
    try:
        return redis_client.ping()
    except Exception:
        return False
