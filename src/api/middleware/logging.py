"""Request/Response logging middleware."""

import time
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses."""

    async def dispatch(self, request: Request, call_next):
        """Log request and response."""
        request_id = str(uuid4())
        start_time = time.time()

        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else None,
            },
        )

        # Process request
        response = await call_next(request)

        # Log response
        duration = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} ({duration:.3f}s)",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration": duration,
            },
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
