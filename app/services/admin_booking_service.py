from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import HTTPException, status

from app.core.enums import BookingStatus, PaymentStatus
from app.repositories.admin_booking_repository import (
    AdminBookingRepository,
)
from app.schemas.admin_booking import (
    AdminBookingResponse,
    BookingListResponse,
)


class AdminBookingService:
    def __init__(
        self,
        repository: AdminBookingRepository,
    ):
        self.repository = repository

    async def get_all_bookings(
        self,
        page: int = 1,
        size: int = 20,
        status: BookingStatus | None = None,
        payment_status: PaymentStatus | None = None,
        scheduled_date: date | None = None,
    ) -> BookingListResponse:

        bookings, total = await self.repository.get_all(
            page=page,
            size=size,
            status=status,
            payment_status=payment_status,
            scheduled_date=scheduled_date,
        )

        return BookingListResponse(
            items=[
                AdminBookingResponse.model_validate(
                    booking
                )
                for booking in bookings
            ],
            total=total,
            page=page,
            size=size,
        )

    async def get_booking(
        self,
        booking_id: UUID,
    ) -> AdminBookingResponse:

        booking = await self.repository.get_by_id(
            booking_id
        )

        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )

        return AdminBookingResponse.model_validate(
            booking
        )

    async def update_status(
        self,
        booking_id: UUID,
        booking_status: BookingStatus,
    ) -> AdminBookingResponse:

        booking = await self.repository.get_by_id(
            booking_id
        )

        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )

        allowed_transitions = {
            BookingStatus.PENDING: {
                BookingStatus.CONFIRMED,
                BookingStatus.CANCELLED,
            },
            BookingStatus.CONFIRMED: {
                BookingStatus.IN_PROGRESS,
                BookingStatus.CANCELLED,
            },
            BookingStatus.IN_PROGRESS: {
                BookingStatus.COMPLETED,
            },
            BookingStatus.COMPLETED: set(),
                BookingStatus.CANCELLED: set(),
        }

        if booking_status not in allowed_transitions[
            booking.status
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot change booking status "
                    f"from '{booking.status.value}' "
                    f"to '{booking_status.value}'."
                ),
            )

        booking.status = booking_status

        booking = await self.repository.update(
            booking
        )

        return AdminBookingResponse.model_validate(
            booking
        )

    async def delete_booking(
        self,
        booking_id: UUID,
    ) -> None:

        booking = await self.repository.get_by_id(
            booking_id
        )

        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )

        await self.repository.delete(booking)