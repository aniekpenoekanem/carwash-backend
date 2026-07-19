from datetime import date, time

from sqlalchemy import select
from uuid import UUID

from app.models.booking import Booking
from app.repositories.base import BaseRepository


class BookingRepository(BaseRepository[Booking]):
    def __init__(self, session):
        super().__init__(session, Booking)

    async def get_by_id(self, booking_id: UUID) -> Booking | None:
        return await self.session.get(Booking, booking_id)

    async def slot_exists(
        self,
        scheduled_date: date,
        scheduled_time: time,
    ) -> bool:
        result = await self.session.execute(
            select(Booking).where(
                Booking.scheduled_date == scheduled_date,
                Booking.scheduled_time == scheduled_time,
            )
        )
        return result.scalar_one_or_none() is not None

    async def create(self, booking: Booking) -> Booking:
        self.session.add(booking)
        await self.session.flush()
        await self.session.refresh(booking)
        return booking