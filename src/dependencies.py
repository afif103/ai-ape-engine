"""FastAPI dependency injection."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AuthenticationError
from src.core.security import decode_token
from src.db.redis import get_redis
from src.db.session import get_db
from src.models.user import User


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None, db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token.

    Args:
        authorization: Authorization header with Bearer token
        db: Database session

    Returns:
        Current user object

    Raises:
        HTTPException: If authentication fails
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.replace("Bearer ", "")

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        token_type = payload.get("type")

        if not user_id:
            raise AuthenticationError("Token missing user ID")

        if token_type != "access":
            raise AuthenticationError("Invalid token type")

        # Get user from database (async query)
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise AuthenticationError("User not found")

        if not user.is_active:
            raise AuthenticationError("User account is inactive")

        return user

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    authorization: Annotated[str | None, Header()] = None, db: AsyncSession = Depends(get_db)
) -> User | None:
    """Get current user if authenticated, None otherwise.

    Args:
        authorization: Authorization header with Bearer token
        db: Database session

    Returns:
        Current user object or None
    """
    try:
        return await get_current_user(authorization, db)
    except HTTPException:
        return None


# Type aliases for cleaner route signatures
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
RedisClient = Annotated[object, Depends(get_redis)]
