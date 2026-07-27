from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import BookingStatus, PaymentStatus


class BookingBase(BaseModel):
    vehicle_id: UUID
    service_id: UUID

    scheduled_date: date
    scheduled_time: time

    notes: str | None = Field(
        default=None,
        max_length=500,
    )


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    scheduled_date: date | None = None
    scheduled_time: time | None = None

    status: BookingStatus | None = None
    payment_status: PaymentStatus | None = None

    notes: str | None = Field(
        default=None,
        max_length=500,
    )


class BookingResponse(BookingBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    customer_id: UUID
    vehicle_id: UUID
    service_id: UUID

    price_at_booking: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2,
    )

    status: BookingStatus
    payment_status: PaymentStatus