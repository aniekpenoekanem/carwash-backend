from __future__ import annotations

from uuid import UUID

from app.models.user import UserRole, User

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    UserNotFoundError,
)
from app.core.security import get_token_subject
from app.db.database import get_session
from app.repositories.user_repository import UserRepository

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_session),
) -> User:
    token = credentials.credentials

    subject = get_token_subject(token)

    if subject is None:
        raise AuthenticationError("Invalid or expired token.")

    try:
        user_id = UUID(subject)
    except ValueError:
        raise AuthenticationError("Invalid token subject.")

    user = await UserRepository(db).get_by_id(user_id)

    if user is None:
        raise UserNotFoundError("User not found.")

    if not user.is_active:
        raise AuthenticationError("User account is inactive.")

    return user

async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise AuthorizationError("Admin access required.")

    return current_user

async def require_customer(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.CUSTOMER:
        raise AuthorizationError("Customer access required.")

    return current_user
