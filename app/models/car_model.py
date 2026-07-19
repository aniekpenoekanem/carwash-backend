from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.car_model import CarModel
    from app.models.vehicle import Vehicle


class CarModel(Base, TimestampMixin):
    __tablename__ = "car_models"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    brand_id: Mapped[UUID] = mapped_column(
        ForeignKey("car_brands.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    body_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    brand: Mapped["CarBrand"] = relationship(
        back_populates="models",
    )

    vehicles: Mapped[list["Vehicle"]] = relationship(
        back_populates="car_model",
    )