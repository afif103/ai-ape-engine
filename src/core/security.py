"""Security utilities for authentication and encryption."""

from datetime import datetime, timedelta
from typing import Any, Optional

import bcrypt
from jose import JWTError, jwt

from src.config import get_settings
from src.core.exceptions import AuthenticationError


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    # Bcrypt has a 72-byte limit, ensure we're within bounds
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        # Truncate to 72 bytes
        password_bytes = password_bytes[:72]

    # Generate salt and hash password
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    # Bcrypt has a 72-byte limit, ensure we're within bounds
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > 72:
        # Truncate to 72 bytes
        password_bytes = password_bytes[:72]

    # Verify password
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token
    """
    settings = get_settings()

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    return encoded_jwt


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create a JWT refresh token.

    Args:
        data: Data to encode in the token

    Returns:
        Encoded JWT token
    """
    settings = get_settings()

    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)

    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token.

    Args:
        token: JWT token to decode

    Returns:
        Decoded token payload

    Raises:
        AuthenticationError: If token is invalid or expired
    """
    settings = get_settings()

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")
