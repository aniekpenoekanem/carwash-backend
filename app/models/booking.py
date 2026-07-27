from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (Date, Enum as SQLEnum, ForeignKey, Numeric, String, Time, UniqueConstraint,)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.core.enums import (BookingStatus, PaymentStatus)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle
    from app.models.customer import Customer
    from app.models.service import Service
    from app.models.payment import Payment


class Booking(Base, TimestampMixin):
    __tablename__ = "bookings"
    
    # Define unique constraint for the combination of scheduled_date and scheduled_time
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
        SQLEnum(
            BookingStatus,
            native_enum=False,
            validate_strings=True,
        ),
        default=BookingStatus.PENDING,
        nullable=False,
    )

    payment_status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(
            PaymentStatus,
            native_enum=False,
            validate_strings=True,
        ),
        default=PaymentStatus.PENDING,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    
    vehicle: Mapped["Vehicle"] = relationship(
        back_populates="bookings",
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="bookings",
    )

    service: Mapped["Service"] = relationship(
        back_populates="bookings",
    )
    
    payment: Mapped["Payment | None"] = relationship(
        back_populates="booking",
        uselist=False,
        cascade="all, delete-orphan",
    )