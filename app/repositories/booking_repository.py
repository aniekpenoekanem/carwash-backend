from __future__ import annotations

from datetime import date, time
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.schemas.booking import BookingUpdate


class BookingRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create(
        self,
        booking_data: dict[str, object],
    ) -> Booking:
        booking = Booking(**booking_data)

        try:
            self.session.add(booking)
            await self.session.commit()
            await self.session.refresh(booking)
            return booking
        
        except IntegrityError:
            await self.session.rollback()
            raise

        except Exception:
            await self.session.rollback()
            raise

    async def get_all(
        self,
    ) -> list[Booking]:
        result = await self.session.execute(
            select(Booking).order_by(
                Booking.scheduled_date,
                Booking.scheduled_time,
            )
        )

        return list(result.scalars().all())

    async def get_by_id(
        self,
        booking_id: UUID,
    ) -> Booking | None:
        result = await self.session.execute(
            select(Booking).where(
                Booking.id == booking_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_customer(
        self,
        customer_id: UUID,
    ) -> list[Booking]:
        result = await self.session.execute(
            select(Booking)
            .where(
                Booking.customer_id == customer_id,
            )
            .order_by(
                Booking.scheduled_date,
                Booking.scheduled_time,
            )
        )

        return list(result.scalars().all())

    async def get_by_vehicle(
        self,
        vehicle_id: UUID,
    ) -> list[Booking]:
        result = await self.session.execute(
            select(Booking)
            .where(
                Booking.vehicle_id == vehicle_id,
            )
            .order_by(
                Booking.scheduled_date,
                Booking.scheduled_time,
            )
        )

        return list(result.scalars().all())

    async def get_by_date(
        self,
        scheduled_date: date,
    ) -> list[Booking]:
        result = await self.session.execute(
            select(Booking)
            .where(
                Booking.scheduled_date == scheduled_date,
            )
            .order_by(
                Booking.scheduled_time,
            )
        )

        return list(result.scalars().all())

    async def get_by_slot(
        self,
        scheduled_date: date,
        scheduled_time: time,
    ) -> Booking | None:
        result = await self.session.execute(
            select(Booking).where(
                Booking.scheduled_date == scheduled_date,
                Booking.scheduled_time == scheduled_time,
            )
        )

        return result.scalar_one_or_none()

    async def update(
        self,
        booking: Booking,
        booking_data: BookingUpdate,
    ) -> Booking:
        update_data = booking_data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(booking, field, value)

        try:
            await self.session.commit()
            await self.session.refresh(booking)
            return booking

        except Exception:
            await self.session.rollback()
            raise

    async def delete(
        self,
        booking: Booking,
    ) -> None:
        try:
            await self.session.delete(booking)
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise