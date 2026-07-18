from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Customer(SQLModel, table=True):
    __tablename__ = "customers"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    first_name: str = Field(index=True, max_length=100)

    last_name: str = Field(index=True, max_length=100)

    email: str = Field(
        index=True,
        unique=True,
        max_length=255,
    )

    phone: str = Field(
        index=True,
        unique=True,
        max_length=20,
    )

    is_active: bool = Field(default=True)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )