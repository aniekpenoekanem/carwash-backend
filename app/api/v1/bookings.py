from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.schemas.booking import BookingCreate, BookingRead
from app.services.booking_service import BookingService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "",
    response_model=BookingRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_booking(
    booking: BookingCreate,
    session: AsyncSession = Depends(get_session),
):
    service = BookingService(session)
    return await service.create_booking(booking)