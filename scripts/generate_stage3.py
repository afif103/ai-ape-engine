#!/usr/bin/env python3
"""
Script to generate all remaining implementation files for APE.
Run this to create Stage 3-5: Authentication, LLM Service, and Chat Module.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# File contents as dictionary
FILES = {
    # STAGE 3: Authentication
    "src/api/schemas/auth.py": '''"""Authentication schemas."""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str | None = None


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User response."""
    id: str
    email: str
    name: str | None
    is_active: bool
    is_verified: bool
    
    class Config:
        from_attributes = True
''',
    "src/repositories/user_repository.py": '''"""User repository for database operations."""

from sqlalchemy.orm import Session

from src.models.user import User


class UserRepository:
    """Repository for User model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: str) -> User | None:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def create(self, email: str, password_hash: str, name: str | None = None) -> User:
        """Create new user."""
        user = User(
            email=email,
            password_hash=password_hash,
            name=name
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update(self, user: User) -> User:
        """Update user."""
        self.db.commit()
        self.db.refresh(user)
        return user
''',
    "src/services/auth_service.py": '''"""Authentication service."""

from datetime import timedelta

from sqlalchemy.orm import Session

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
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def register(self, email: str, password: str, name: str | None = None) -> dict:
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
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise ValidationError("User with this email already exists")
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user
        user = self.user_repo.create(email, password_hash, name)
        
        # Generate tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    
    def login(self, email: str, password: str) -> dict:
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
        user = self.user_repo.get_by_email(email)
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
''',
    "src/api/routes/auth.py": '''"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from src.core.exceptions import AuthenticationError, ValidationError
from src.dependencies import CurrentUser, DatabaseSession
from src.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    db: DatabaseSession
):
    """Register new user."""
    try:
        service = AuthService(db)
        result = service.register(data.email, data.password, data.name)
        
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"]
        )
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: DatabaseSession
):
    """Login user."""
    try:
        service = AuthService(db)
        result = service.login(data.email, data.password)
        
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"]
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: CurrentUser
):
    """Get current user information."""
    return current_user
''',
}


def main():
    """Generate all files."""
    print("Generating APE implementation files...")

    created = 0
    for file_path, content in FILES.items():
        full_path = BASE_DIR / file_path

        # Create directory if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✓ Created: {file_path}")
        created += 1

    print(f"\n✅ Successfully created {created} files!")
    print("\nNext steps:")
    print("1. Review generated files")
    print("2. Continue with Stage 4-5 generation")
    print("3. Run: docker-compose up --build")


if __name__ == "__main__":
    main()
