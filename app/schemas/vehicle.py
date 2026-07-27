from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VehicleBase(BaseModel):
    brand_id: UUID
    car_model_id: UUID

    registration_number: str = Field(
        min_length=1,
        max_length=20,
    )

    color: str = Field(
        min_length=1,
        max_length=50,
    )

    year: int | None = Field(
        default=None,
        ge=1900,
        le=2100,
    )


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    brand_id: UUID | None = None
    car_model_id: UUID | None = None

    registration_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
    )

    color: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    year: int | None = Field(
        default=None,
        ge=1900,
        le=2100,
    )


class VehicleResponse(VehicleBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    customer_id: UUID