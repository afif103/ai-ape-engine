"""Authentication schemas."""

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_serializer


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

    id: UUID
    email: str
    name: str | None
    is_active: bool
    is_verified: bool

    @field_serializer("id")
    def serialize_id(self, id: UUID, _info):
        return str(id)

    class Config:
        from_attributes = True
