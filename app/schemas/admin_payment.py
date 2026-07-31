from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import PaymentStatus


class AdminPaymentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    booking_id: UUID

    customer_name: str
    customer_email: str

    service_name: str
    vehicle: str

    amount: Decimal

    reference: str
    provider: str
    status: PaymentStatus

    paid_at: datetime | None
    created_at: datetime


class AdminPaymentListResponse(BaseModel):
    items: list[AdminPaymentSummary]
    total: int
    page: int
    size: int


class AdminPaymentDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    booking_id: UUID

    amount: Decimal
    currency: str

    provider: str
    reference: str

    access_code: str | None
    authorization_url: str | None
    gateway_response: str | None

    status: PaymentStatus

    paid_at: datetime | None
    created_at: datetime

    customer_name: str
    customer_email: str
    customer_phone: str

    vehicle: str
    service_name: str


class PaymentStatistics(BaseModel):
    total_payments: int
    successful_payments: int
    pending_payments: int
    failed_payments: int

    total_revenue: Decimal