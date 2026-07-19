from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from app.models.booking import BookingStatus, PaymentStatus
from app.schemas.base import SchemaBase


class BookingCreate(SchemaBase):
    customer_id: UUID
    vehicle_id: UUID
    service_id: UUID

    scheduled_date: date
    scheduled_time: time

    notes: str | None = None


class BookingUpdate(SchemaBase):
    status: BookingStatus | None = None
    payment_status: PaymentStatus | None = None
    notes: str | None = None


class BookingRead(SchemaBase):
    id: UUID

    customer_id: UUID
    vehicle_id: UUID
    service_id: UUID

    scheduled_date: date
    scheduled_time: time

    price_at_booking: Decimal

    status: BookingStatus
    payment_status: PaymentStatus

    notes: str | None

    created_at: datetime
    updated_at: datetime