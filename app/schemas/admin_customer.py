from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.booking import BookingResponse
from app.schemas.vehicle import VehicleResponse


class AdminCustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID

    first_name: str
    last_name: str
    email: str
    phone: str

    is_active: bool

    created_at: datetime
    updated_at: datetime


class CustomerStatusUpdate(BaseModel):
    is_active: bool


class CustomerListResponse(BaseModel):
    items: list[AdminCustomerResponse]

    total: int
    page: int
    size: int


class AdminCustomerDetailsResponse(AdminCustomerResponse):
    vehicles: list[VehicleResponse]
    bookings: list[BookingResponse]

    total_bookings: int
    total_spent: Decimal