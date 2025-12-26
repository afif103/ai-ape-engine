"""Authentication service."""

from datetime import timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AuthenticationError, ValidationError
from src.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from src.repositories.user_repository import UserRepository


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, email: str, password: str, name: Optional[str] = None) -> dict:
        """Register new user.

        Args:
            email: User email
            password: Plain text password
            name: User name

        Returns:
            Dict with user and tokens

        Raises:
            ValidationError: If user already exists
        """
        # Check if user exists
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ValidationError("User with this email already exists")

        # Hash password
        password_hash = hash_password(password)

        # Create user
        user = await self.user_repo.create(email, password_hash, name)

        # Generate tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def login(self, email: str, password: str) -> dict:
        """Login user.

        Args:
            email: User email
            password: Plain text password

        Returns:
            Dict with user and tokens

        Raises:
            AuthenticationError: If credentials are invalid
        """
        # Get user
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise AuthenticationError("Invalid email or password")

        # Verify password
        if not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password")

        # Check if active
        if not user.is_active:
            raise AuthenticationError("Account is inactive")

        # Generate tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
