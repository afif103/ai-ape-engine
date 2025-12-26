"""Health check endpoint."""

from fastapi import APIRouter
from sqlalchemy import text

from src.db.redis import ping_redis
from src.db.session import SessionLocal

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint.

    Checks:
    - API is running
    - Database connection
    - Redis connection

    Returns:
        Health status with component checks
    """
    health_status = {
        "status": "healthy",
        "components": {
            "api": "up",
            "database": "unknown",
            "redis": "unknown",
        },
    }

    # Check database
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["components"]["database"] = "up"
    except Exception as e:
        health_status["components"]["database"] = f"down: {str(e)}"
        health_status["status"] = "degraded"

    # Check Redis
    try:
        if ping_redis():
            health_status["components"]["redis"] = "up"
        else:
            health_status["components"]["redis"] = "down"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["components"]["redis"] = f"down: {str(e)}"
        health_status["status"] = "degraded"

    return health_status
