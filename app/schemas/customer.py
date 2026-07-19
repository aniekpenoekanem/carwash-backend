from __future__ import annotations

from uuid import UUID

from app.schemas.base import SchemaBase


class CustomerCreate(SchemaBase):
    first_name: str
    last_name: str
    email: str
    phone: str


class CustomerUpdate(SchemaBase):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    is_active: bool | None = None


class CustomerRead(SchemaBase):
    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str
    is_active: bool