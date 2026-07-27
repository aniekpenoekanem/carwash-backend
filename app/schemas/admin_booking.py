from __future__ import annotations

from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import BookingStatus, PaymentStatus


class AdminBookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    customer_id: UUID
    vehicle_id: UUID
    service_id: UUID

    scheduled_date: date
    scheduled_time: time

    price_at_booking: float

    status: BookingStatus
    payment_status: PaymentStatus

    notes: str | None

    created_at: datetime
    updated_at: datetime


class BookingStatusUpdate(BaseModel):
    status: BookingStatus


class BookingListResponse(BaseModel):
    items: list[AdminBookingResponse]

    total: int
    page: int
    size: int
    
class BookingFilter(BaseModel):
    status: BookingStatus | None = None

    payment_status: PaymentStatus | None = None

    scheduled_date: date | None = None

    page: int = 1

    size: int = 20