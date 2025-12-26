"""FastAPI main application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routes import (
    auth,
    chat,
    code,
    extraction,
    export,
    health,
    instruction,
    processing,
    research,
)
from src.config import get_settings
from src.core.exceptions import APEException
from src.core.logging import get_logger, setup_logging

# Setup logging
setup_logging()
logger = get_logger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting APE - AI Productivity Engine")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Debug mode: {settings.debug}")

    yield

    # Shutdown
    logger.info("Shutting down APE")


# Create FastAPI application
app = FastAPI(
    title="APE - AI Productivity Engine",
    description="All-in-one AI platform for research, creation, automation, and development",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(APEException)
async def ape_exception_handler(request, exc: APEException):
    """Handle custom APE exceptions."""
    logger.error(f"APE Exception: {exc.message}", extra={"details": exc.details})
    return JSONResponse(status_code=400, content={"error": exc.message, "details": exc.details})


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.exception(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.debug else "An error occurred",
        },
    )


# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix=f"{settings.api_v1_prefix}/auth", tags=["Authentication"])
app.include_router(chat.router, prefix=f"{settings.api_v1_prefix}", tags=["Chat"])
app.include_router(code.router, prefix=f"{settings.api_v1_prefix}", tags=["Code"])
app.include_router(research.router, prefix=f"{settings.api_v1_prefix}", tags=["Research"])
app.include_router(extraction.router, prefix=f"{settings.api_v1_prefix}", tags=["Extraction"])
app.include_router(instruction.router, prefix=f"{settings.api_v1_prefix}", tags=["Instruction"])
app.include_router(processing.router, prefix=f"{settings.api_v1_prefix}", tags=["Processing"])
app.include_router(export.router, prefix=f"{settings.api_v1_prefix}", tags=["Export"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "APE - AI Productivity Engine",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
