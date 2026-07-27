from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session

from app.repositories.admin_service_repository import (
    AdminServiceRepository,
)
from app.services.admin_service_service import (
    AdminServiceService,
)


def get_admin_service_service(
    session: AsyncSession = Depends(get_session),
) -> AdminServiceService:

    repository = AdminServiceRepository(session)

    return AdminServiceService(repository)