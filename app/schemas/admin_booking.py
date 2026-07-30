from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import (
    BookingStatus,
    BodyType,
    PaymentStatus,
)


class AdminCustomerSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str


class AdminVehicleSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    registration_number: str
    color: str
    year: int | None

    brand: str
    model: str
    body_type: BodyType


class AdminServiceSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    price: Decimal


class AdminBookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    customer: AdminCustomerSummary
    vehicle: AdminVehicleSummary
    service: AdminServiceSummary

    scheduled_date: date
    scheduled_time: time

    price_at_booking: Decimal

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