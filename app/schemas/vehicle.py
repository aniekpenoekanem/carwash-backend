from __future__ import annotations

from uuid import UUID

from app.schemas.base import SchemaBase


class VehicleCreate(SchemaBase):
    customer_id: UUID
    make: str
    model: str
    year: int
    color: str
    plate_number: str
    body_type: str


class VehicleUpdate(SchemaBase):
    make: str | None = None
    model: str | None = None
    year: int | None = None
    color: str | None = None
    plate_number: str | None = None
    body_type: str | None = None


class VehicleRead(SchemaBase):
    id: UUID
    customer_id: UUID
    make: str
    model: str
    year: int
    color: str
    plate_number: str
    body_type: str