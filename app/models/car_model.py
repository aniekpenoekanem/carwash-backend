from __future__ import annotations
from uuid import UUID, uuid4
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin
from sqlalchemy import Enum as SQLEnum
from app.core.enums import BodyType

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.car_brand import CarBrand
    from app.models.vehicle import Vehicle


class CarModel(Base, TimestampMixin):
    __tablename__ = "car_models"
    
    __table_args__ = (
        UniqueConstraint(
            "brand_id",
            "name",
            name="uq_car_model_brand_name",
        ),
    )

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

    body_type: Mapped[BodyType] = mapped_column(
        SQLEnum(
            BodyType,
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
    )
    brand: Mapped["CarBrand"] = relationship(
        back_populates="models",
    )

    vehicles: Mapped[list["Vehicle"]] = relationship(
        back_populates="car_model",
    )
    
    ForeignKey(
    "car_brands.id",
    ondelete="RESTRICT",
    )