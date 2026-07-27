from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.repositories.admin_repository import AdminRepository
from app.services.admin_service import AdminService


def get_admin_service(
    session: AsyncSession = Depends(get_session),
) -> AdminService:
    return AdminService(
        AdminRepository(session)
    )