from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Vehicle(Base, TimestampMixin):
    __tablename__ = "vehicles"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("customers.id"),
        index=True,
        nullable=False,
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="vehicles",
    )

    make: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
    )

    model: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    color: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    plate_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
    )

    body_type: Mapped[str] = mapped_column(
        String(50),
        index=True,
        nullable=False,
    )