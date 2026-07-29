from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import BookingStatus, PaymentStatus


class VehicleSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    registration_number: str
    color: str
    year: int | None

    brand_name: str
    model_name: str


class ServiceSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    price: Decimal


class BookingHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    scheduled_date: date
    scheduled_time: time

    price_at_booking: Decimal

    status: BookingStatus
    payment_status: PaymentStatus

    notes: str | None

    vehicle: VehicleSummary
    service: ServiceSummary