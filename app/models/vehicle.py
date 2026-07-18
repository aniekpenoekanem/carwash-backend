from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Vehicle(SQLModel, table=True):
    __tablename__ = "vehicles"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    customer_id: UUID = Field(
        foreign_key="customers.id",
        index=True,
    )

    make: str = Field(
        max_length=100,
        index=True,
    )

    model: str = Field(
        max_length=100,
        index=True,
    )

    year: int

    color: str = Field(max_length=50)

    plate_number: str = Field(
        max_length=20,
        unique=True,
        index=True,
    )

    body_type: str = Field(
        max_length=50,
        index=True,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )