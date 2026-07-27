from __future__ import annotations

from uuid import UUID, uuid4
from sqlalchemy import ForeignKey
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle
    from app.models.booking import Booking
    from app.models.user import User
    
class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )
    
    first_name: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    vehicles: Mapped[list["Vehicle"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="customer",
    )
    
    user: Mapped["User"] = relationship(
        back_populates="customer",
    )
    