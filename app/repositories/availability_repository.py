from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import BookingStatus
from app.models.booking import Booking


class AvailabilityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_booked_slots(
        self,
        scheduled_date: date,
    ) -> list:

        result = await self.session.scalars(
            select(Booking.scheduled_time).where(
                Booking.scheduled_date == scheduled_date,
                Booking.status.in_(
                    [
                        BookingStatus.PENDING,
                        BookingStatus.CONFIRMED,
                        BookingStatus.IN_PROGRESS,
                    ]
                ),
            )
        )

        return list(result.all())