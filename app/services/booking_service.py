from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import (
    Booking,
    BookingStatus,
    PaymentStatus,
)
from app.repositories.booking_repository import BookingRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.booking import BookingCreate, BookingRead


class BookingService:
    OPENING_TIME = time(8, 0)
    CLOSING_TIME = time(17, 0)

    def __init__(self, session: AsyncSession):
        self.session = session

        self.booking_repo = BookingRepository(session)
        self.customer_repo = CustomerRepository(session)
        self.vehicle_repo = VehicleRepository(session)
        self.service_repo = ServiceRepository(session)

    async def create_booking(
        self,
        booking_data: BookingCreate,
    ) -> BookingRead:

        customer = await self.customer_repo.get_by_id(
            booking_data.customer_id
        )
        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )

        vehicle = await self.vehicle_repo.get_by_id(
            booking_data.vehicle_id
        )
        if vehicle is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found.",
            )

        if vehicle.customer_id != customer.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle does not belong to this customer.",
            )

        service = await self.service_repo.get_by_id(
            booking_data.service_id
        )
        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        if booking_data.scheduled_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking date cannot be in the past.",
            )

        if not (
            self.OPENING_TIME
            <= booking_data.scheduled_time
            <= self.CLOSING_TIME
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bookings are accepted between 08:00 and 17:00.",
            )

        slot_taken = await self.booking_repo.slot_exists(
            booking_data.scheduled_date,
            booking_data.scheduled_time,
        )

        if slot_taken:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Selected time slot is already booked.",
            )

        booking = Booking(
            customer_id=customer.id,
            vehicle_id=vehicle.id,
            service_id=service.id,
            scheduled_date=booking_data.scheduled_date,
            scheduled_time=booking_data.scheduled_time,
            price_at_booking=Decimal(service.price),
            status=BookingStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            notes=booking_data.notes,
        )

        await self.booking_repo.create(booking)

        await self.session.commit()

        await self.session.refresh(booking)

        return BookingRead.model_validate(booking)