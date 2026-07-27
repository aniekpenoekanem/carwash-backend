from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.repositories.availability_repository import (
    AvailabilityRepository,
)
from app.services.availability_service import (
    AvailabilityService,
)


def get_availability_service(
    session: AsyncSession = Depends(get_session),
) -> AvailabilityService:

    repository = AvailabilityRepository(session)

    return AvailabilityService(repository)