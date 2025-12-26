"""Test configuration and fixtures."""

import asyncio
import os
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import get_settings
from src.db.session import get_db
from src.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db():
    """Create test database session."""
    settings = get_settings()

    # Use test database URL if available, otherwise use main DB
    test_db_url = os.getenv("TEST_DATABASE_URL", settings.database_url)

    # Create async engine
    engine = create_async_engine(test_db_url, echo=False)

    # Create async session factory
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Override the get_db dependency
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with async_session() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield async_session

    # Cleanup
    await engine.dispose()


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest.fixture
async def auth_headers(client: TestClient) -> dict:
    """Create authentication headers for test user."""
    # Register a test user
    register_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "name": "Test User",
    }

    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code in [200, 201]  # Registration might return tokens

    # Login to get tokens
    login_data = {"email": "test@example.com", "password": "TestPassword123!"}

    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200

    data = response.json()
    access_token = data["access_token"]

    return {"Authorization": f"Bearer {access_token}"}
