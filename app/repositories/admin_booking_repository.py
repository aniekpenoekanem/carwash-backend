from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enums import BookingStatus, PaymentStatus
from app.models.booking import Booking
from app.models.vehicle import Vehicle


class AdminBookingRepository:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def get_all(
        self,
        page: int = 1,
        size: int = 20,
        status: BookingStatus | None = None,
        payment_status: PaymentStatus | None = None,
        scheduled_date: date | None = None,
    ) -> tuple[list[Booking], int]:

        query = (
            select(Booking)
            .options(
                selectinload(Booking.customer),
                selectinload(Booking.service),
                selectinload(Booking.vehicle).selectinload(Vehicle.brand),
                selectinload(Booking.vehicle).selectinload(Vehicle.car_model),
            )
        )

        count_query = select(func.count(Booking.id))

        if status:
            query = query.where(
                Booking.status == status,
            )
            count_query = count_query.where(
                Booking.status == status,
            )

        if payment_status:
            query = query.where(
                Booking.payment_status == payment_status,
            )
            count_query = count_query.where(
                Booking.payment_status == payment_status,
            )

        if scheduled_date:
            query = query.where(
                Booking.scheduled_date == scheduled_date,
            )
            count_query = count_query.where(
                Booking.scheduled_date == scheduled_date,
            )

        total = (
            await self.db.execute(count_query)
        ).scalar_one()

        result = await self.db.execute(
            query.order_by(
                Booking.scheduled_date.desc(),
                Booking.scheduled_time.desc(),
            )
            .offset((page - 1) * size)
            .limit(size)
        )

        bookings = result.scalars().unique().all()

        return bookings, total

    async def get_by_id(
        self,
        booking_id: UUID,
    ) -> Booking | None:

        result = await self.db.execute(
            select(Booking)
            .options(
                selectinload(Booking.customer),
                selectinload(Booking.service),
                selectinload(Booking.vehicle).selectinload(Vehicle.brand),
                selectinload(Booking.vehicle).selectinload(Vehicle.car_model),
            )
            .where(
                Booking.id == booking_id,
            )
        )

        return result.scalar_one_or_none()

    async def update(
        self,
        booking: Booking,
    ) -> Booking:

        await self.db.commit()
        await self.db.refresh(booking)

        return booking

    async def delete(
        self,
        booking: Booking,
    ) -> None:

        await self.db.delete(booking)
        await self.db.commit()