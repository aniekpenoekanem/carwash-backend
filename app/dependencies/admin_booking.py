from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.repositories.admin_booking_repository import (
    AdminBookingRepository,
)
from app.services.admin_booking_service import (
    AdminBookingService,
)


def get_admin_booking_service(
    session: AsyncSession = Depends(get_session),
) -> AdminBookingService:
    return AdminBookingService(
        AdminBookingRepository(session)
    )