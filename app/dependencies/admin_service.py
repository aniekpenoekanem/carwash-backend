from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.repositories.service_repository import ServiceRepository
from app.services.service_service import ServiceService


def get_admin_service_service(
    session: AsyncSession = Depends(get_session),
) -> ServiceService:
    return ServiceService(session)