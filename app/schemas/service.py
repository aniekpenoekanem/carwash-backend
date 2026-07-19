from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from app.schemas.base import SchemaBase


class ServiceCreate(SchemaBase):
    name: str
    description: str | None = None
    price: Decimal


class ServiceUpdate(SchemaBase):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    is_active: bool | None = None


class ServiceRead(SchemaBase):
    id: UUID
    name: str
    description: str | None
    price: Decimal
    is_active: bool