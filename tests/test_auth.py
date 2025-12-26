"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


class TestAuth:
    """Test authentication functionality."""

    @pytest.mark.asyncio
    async def test_register_user(self, client: AsyncClient):
        """Test user registration."""
        user_data = {
            "email": "testuser@example.com",
            "password": "SecurePass123!",
            "name": "Test User",
        }

        response = await client.post("/api/v1/auth/register", json=user_data)

        # Registration should succeed
        assert response.status_code in [200, 201]

        data = response.json()
        # Should return user data or tokens
        assert "email" in data or "access_token" in data

    @pytest.mark.asyncio
    async def test_login_user(self, client: AsyncClient):
        """Test user login."""
        # First register
        user_data = {
            "email": "logintest@example.com",
            "password": "SecurePass123!",
            "name": "Login Test",
        }

        await client.post("/api/v1/auth/register", json=user_data)

        # Now login
        login_data = {"email": "logintest@example.com", "password": "SecurePass123!"}

        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, auth_headers: dict):
        """Test getting current user with valid token."""
        response = await client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "name" in data
        assert "is_active" in data

    @pytest.mark.asyncio
    async def test_invalid_login(self, client: AsyncClient):
        """Test login with invalid credentials."""
        login_data = {"email": "nonexistent@example.com", "password": "WrongPassword123!"}

        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_access_protected_route_without_token(self, client: AsyncClient):
        """Test accessing protected route without authentication."""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401
        assert "Missing or invalid authorization header" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_duplicate_email_registration(self, client: AsyncClient):
        """Test registering with email that already exists."""
        user_data = {
            "email": "duplicate@example.com",
            "password": "SecurePass123!",
            "name": "First User",
        }

        # First registration
        await client.post("/api/v1/auth/register", json=user_data)

        # Second registration with same email
        user_data["name"] = "Second User"
        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
