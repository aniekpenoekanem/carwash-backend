from __future__ import annotations

from datetime import date, time

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from app.models.booking import Booking
from app.repositories.booking_repository import BookingRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.service_repository import ServiceRepository

from app.core.enums import (
    BookingStatus,
    PaymentStatus,
)

from app.schemas.booking import (
    BookingCreate,
    BookingUpdate,
)

from app.schemas.booking_history import (
    BookingHistoryResponse,
    VehicleSummary,
    ServiceSummary,
)

OPENING_TIME = time(8, 0)
CLOSING_TIME = time(17, 0)

WORKING_DAYS = {
    0,
    1,
    2,
    3,
    4,
    5,
}

ALLOWED_STATUS_TRANSITIONS = {
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

ALLOWED_PAYMENT_TRANSITIONS = {
    PaymentStatus.PENDING: {
        PaymentStatus.PAID,
        PaymentStatus.FAILED,
    },
    PaymentStatus.PAID: {
        PaymentStatus.REFUNDED,
    },
    PaymentStatus.FAILED: set(),
    PaymentStatus.REFUNDED: set(),
}


class BookingService:
    def __init__(
        self,
        booking_repository: BookingRepository,
        customer_repository: CustomerRepository,
        vehicle_repository: VehicleRepository,
        service_repository: ServiceRepository,
    ):
        self.booking_repository = booking_repository
        self.customer_repository = customer_repository
        self.vehicle_repository = vehicle_repository
        self.service_repository = service_repository

    async def create_booking(
        self,
        booking_data: BookingCreate,
        customer_id: UUID,
    ) -> Booking:

        customer = await self.customer_repository.get_by_id(
            customer_id,
        )

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )

        vehicle = await self.vehicle_repository.get_by_id(
            booking_data.vehicle_id,
        )

        if vehicle is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found.",
            )

        if vehicle.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle does not belong to the selected customer.",
            )

        service = await self.service_repository.get_by_id(
            booking_data.service_id,
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        if not service.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected service is inactive.",
            )

        if booking_data.scheduled_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking date cannot be in the past.",
            )

        if booking_data.scheduled_date.weekday() not in WORKING_DAYS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bookings are not available on this day.",
            )

        if (
            booking_data.scheduled_time < OPENING_TIME
            or booking_data.scheduled_time >= CLOSING_TIME
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bookings are allowed only between 08:00 and 17:00.",
            )

        existing_booking = (
            await self.booking_repository.get_by_slot(
                booking_data.scheduled_date,
                booking_data.scheduled_time,
            )
        )

        if existing_booking is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The selected time slot is already booked.",
            )

        booking_payload = booking_data.model_dump()
        
        # Never trust the client for these values.
        booking_payload["customer_id"] = customer_id
        booking_payload["price_at_booking"] = service.price
        
        try:
            return await self.booking_repository.create(
                booking_payload,
            )
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The selected time slot is already booked.",
            )

    async def get_bookings(
        self,
    ) -> list[Booking]:
        return await self.booking_repository.get_all()

    async def get_booking(
        self,
        booking_id: UUID,
        customer_id: UUID,
    ) -> Booking:

        booking = await self.booking_repository.get_by_id(
        booking_id,
        )

        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )

        if booking.customer_id != customer_id:
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to pay for this booking.",
            )

        return booking

    async def get_customer_bookings(
        self,
        customer_id: UUID,
    ) -> list[Booking]:

        customer = await self.customer_repository.get_by_id(
            customer_id,
        )

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )

        return await self.booking_repository.get_by_customer(
            customer_id,
        )

    async def update_booking(
        self,
        booking_id: UUID,
        booking_data: BookingUpdate,
        customer_id: UUID,
    ) -> Booking:

        booking = await self.booking_repository.get_by_id(
            booking_id,
        )

        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )

        if booking.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this booking.",
            )

        # Only validate scheduling if the customer is changing
        # the booking date or time.
        if (
            booking_data.scheduled_date is not None
            or booking_data.scheduled_time is not None
        ):

            booking_date = (
                booking_data.scheduled_date
                if booking_data.scheduled_date is not None
                else booking.scheduled_date
            )

            booking_time = (
                booking_data.scheduled_time
                if booking_data.scheduled_time is not None
                else booking.scheduled_time
            )

            if booking_date < date.today():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Booking date cannot be in the past.",
                )

            if booking_date.weekday() not in WORKING_DAYS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Bookings are not available on this day.",
                )

            if (
                booking_time < OPENING_TIME
                or booking_time >= CLOSING_TIME
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Bookings are allowed only between 08:00 and 17:00.",
                )

            existing_booking = await self.booking_repository.get_by_slot(
                booking_date,
                booking_time,
            )

            if (
                existing_booking is not None
                and existing_booking.id != booking.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="The selected time slot is already booked.",
                )
                
         # Validate booking status transition.
        if booking_data.status is not None:
            allowed_statuses = ALLOWED_STATUS_TRANSITIONS[
                booking.status
            ]

            if booking_data.status not in allowed_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Cannot change booking status "
                        f"from '{booking.status.value}' "
                        f"to '{booking_data.status.value}'."
                    ),
                )

        # Validate payment status transition.
        if booking_data.payment_status is not None:
            allowed_payments = ALLOWED_PAYMENT_TRANSITIONS[
                booking.payment_status
            ]

            if booking_data.payment_status not in allowed_payments:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Cannot change payment status "
                        f"from '{booking.payment_status.value}' "
                        f"to '{booking_data.payment_status.value}'."
                    ),
                )

        return await self.booking_repository.update(
            booking,
            booking_data,
        )

    async def delete_booking(
        self,
        booking_id: UUID,
        customer_id: UUID,
    ) -> None:

        booking = await self.booking_repository.get_by_id(
            booking_id,
        )

        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )

        if booking.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this booking.",
            )
            
        await self.booking_repository.delete(
            booking,
        )
        
    async def get_booking_history(
        self,
        customer_id: UUID,
    ) -> list[BookingHistoryResponse]:

        customer = await self.customer_repository.get_by_id(
            customer_id,
        )

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )

        bookings = await self.booking_repository.get_history_by_customer(
            customer_id,
        )

        history: list[BookingHistoryResponse] = []

        for booking in bookings:
            history.append(
                BookingHistoryResponse(
                    id=booking.id,
                    scheduled_date=booking.scheduled_date,
                    scheduled_time=booking.scheduled_time,
                    price_at_booking=booking.price_at_booking,
                    status=booking.status,
                    payment_status=booking.payment_status,
                    notes=booking.notes,
                    vehicle=VehicleSummary(
                        id=booking.vehicle.id,
                        registration_number=booking.vehicle.registration_number,
                        color=booking.vehicle.color,
                        year=booking.vehicle.year,
                        brand_name=booking.vehicle.brand.name,
                        model_name=booking.vehicle.car_model.name,
                    ),
                    service=ServiceSummary(
                        id=booking.service.id,
                        name=booking.service.name,
                        price=booking.service.price,
                    ),
                )
            )

        return history        