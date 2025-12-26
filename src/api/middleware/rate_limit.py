"""Rate limiting middleware."""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.config import get_settings
from src.db.redis import get_redis

settings = get_settings()
redis_client = get_redis()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting based on IP address or user ID."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit before processing request."""

        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)

        # Get identifier (IP address or user ID from token)
        identifier = request.client.host if request.client else "unknown"

        # Get current minute window
        current_minute = int(time.time() / 60)
        key_minute = f"ratelimit:{identifier}:minute:{current_minute}"

        try:
            # Increment counter
            count = redis_client.incr(key_minute)

            # Set expiry on first request
            if count == 1:
                redis_client.expire(key_minute, 60)

            # Check limit
            if count > settings.rate_limit_per_minute:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Maximum {settings.rate_limit_per_minute} requests per minute",
                    },
                )

        except Exception:
            # If Redis is down, allow the request (fail open)
            pass

        return await call_next(request)
