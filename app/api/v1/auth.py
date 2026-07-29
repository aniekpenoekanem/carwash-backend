from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_session, engine
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=201,
)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_session),
) -> TokenResponse:
    service = AuthService(db)
    return await service.register(payload)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_session),
) -> TokenResponse:
    service = AuthService(db)
    return await service.login(payload)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)


# ---------------------------------------------------------
# Temporary Debug Endpoints
# ---------------------------------------------------------

@router.get("/debug/user/{email}")
async def debug_user(
    email: str,
    db: AsyncSession = Depends(get_session),
):
    repo = UserRepository(db)
    user = await repo.get_by_email(email)

    if not user:
        return {
            "found": False,
        }

    return {
        "found": True,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "password_hash_exists": bool(user.password_hash),
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


@router.get("/debug/database")
async def debug_database():
    return {
        "database_url": settings.DATABASE_URL,
        "engine_url": str(engine.url),
        "engine_name": engine.dialect.name,
    }