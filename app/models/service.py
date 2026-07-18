from __future__ import annotations

from datetime import datetime, UTC
from decimal import Decimal
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric

from app.models.base import TimestampMixin


class Service(TimestampMixin, SQLModel, table=True):
    __tablename__ = "services"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    name: str = Field(index=True, max_length=100)

    description: str | None = Field(
        default=None,
        max_length=500,
    )

    price: Decimal = Field(
        sa_column=Column(
            Numeric(10, 2),
            nullable=False,
        )
    )

    is_active: bool = Field(default=True)

    