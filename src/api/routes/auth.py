"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from src.core.exceptions import AuthenticationError, ValidationError
from src.dependencies import CurrentUser, DatabaseSession
from src.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: DatabaseSession):
    """Register new user."""
    try:
        service = AuthService(db)
        result = await service.register(data.email, data.password, data.name)

        return TokenResponse(
            access_token=result["access_token"], refresh_token=result["refresh_token"]
        )
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: DatabaseSession):
    """Login user."""
    try:
        service = AuthService(db)
        result = await service.login(data.email, data.password)

        return TokenResponse(
            access_token=result["access_token"], refresh_token=result["refresh_token"]
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser):
    """Get current user information."""
    return current_user


@router.options("/login")
async def options_login():
    return {"message": "OK"}


@router.options("/me")
async def options_me():
    return {"message": "OK"}
