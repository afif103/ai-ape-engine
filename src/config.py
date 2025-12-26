"""Configuration management for APE."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Application
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    secret_key: str = Field(..., min_length=32)
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = Field(..., description="PostgreSQL connection string")
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Redis
    redis_url: str = Field(..., description="Redis connection string")
    redis_max_connections: int = 10

    # LLM Providers
    groq_api_key: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_default_region: str = "us-east-1"
    openai_api_key: str | None = None

    # External Services
    firecrawl_api_key: str | None = None

    # LangSmith (optional)
    langchain_tracing_v2: bool = False
    langchain_project: str = "ape-dev"
    langchain_api_key: str | None = None

    # Security
    jwt_secret_key: str = Field(..., min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000

    # ChromaDB
    chroma_persist_directory: str = "./chroma_db"
    chroma_host: str = "localhost"
    chroma_port: int = 8001

    # S3 (optional)
    s3_bucket_name: str | None = None
    s3_region: str = "us-east-1"

    # CORS
    cors_origins: str = (
        "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:8000"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
