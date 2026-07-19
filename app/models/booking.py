from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import (Date, Enum as SQLEnum, ForeignKey, Numeric, String, Time, UniqueConstraint,)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class Booking(Base, TimestampMixin):
    __tablename__ = "bookings"
    
    __table_args__ = (
        UniqueConstraint(
            "scheduled_date",
            "scheduled_time",
            name="uq_booking_slot",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("customers.id"),
        index=True,
        nullable=False,
    )

    vehicle_id: Mapped[UUID] = mapped_column(
        ForeignKey("vehicles.id"),
        index=True,
        nullable=False,
    )

    service_id: Mapped[UUID] = mapped_column(
        ForeignKey("services.id"),
        index=True,
        nullable=False,
    )

    scheduled_date: Mapped[date] = mapped_column(
        Date,
        index=True,
        nullable=False,
    )

    scheduled_time: Mapped[time] = mapped_column(
        Time,
        index=True,
        nullable=False,
    )

    price_at_booking: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    status: Mapped[BookingStatus] = mapped_column(
        SQLEnum(BookingStatus),
        default=BookingStatus.PENDING,
        nullable=False,
    )

    payment_status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )