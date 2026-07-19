from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.car_model import CarModel
    from app.models.vehicle import Vehicle

class CarBrand(Base, TimestampMixin):
    __tablename__ = "car_brands"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    models: Mapped[list["CarModel"]] = relationship(
        back_populates="brand",
        cascade="all, delete-orphan",
    )

    vehicles: Mapped[list["Vehicle"]] = relationship(
        back_populates="brand",
    )