from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.car_brand import CarBrand
    from app.models.car_model import CarModel


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

    brand_id: Mapped[UUID] = mapped_column(
        ForeignKey("car_brands.id"),
        nullable=False,
        index=True,
    )
    brand: Mapped["CarBrand"] = relationship(
        back_populates="vehicles",
    )
    
    car_model_id: Mapped[UUID] = mapped_column(
        ForeignKey("car_models.id"),
        nullable=False,
        index=True,
    )

    car_model: Mapped["CarModel"] = relationship(
        back_populates="vehicles",
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
