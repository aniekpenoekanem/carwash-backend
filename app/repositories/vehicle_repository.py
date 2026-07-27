from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate
from typing import Any


class VehicleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        vehicle_data: dict[str, Any],
    ) -> Vehicle:
        vehicle = Vehicle(**vehicle_data)

        self.session.add(vehicle)
        await self.session.commit()
        await self.session.refresh(vehicle)

        return vehicle

    async def get_all(self) -> list[Vehicle]:
        result = await self.session.execute(
            select(Vehicle).order_by(Vehicle.registration_number)
        )

        return list(result.scalars().all())

    async def get_by_id(
        self,
        vehicle_id: UUID,
    ) -> Vehicle | None:
        result = await self.session.execute(
            select(Vehicle).where(
                Vehicle.id == vehicle_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_registration_number(
        self,
        registration_number: str,
    ) -> Vehicle | None:
        result = await self.session.execute(
            select(Vehicle).where(
                Vehicle.registration_number == registration_number,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_customer(
        self,
        customer_id: UUID,
    ) -> list[Vehicle]:
        result = await self.session.execute(
            select(Vehicle)
            .where(Vehicle.customer_id == customer_id)
            .order_by(Vehicle.registration_number)
        )

        return list(result.scalars().all())

    async def update(
        self,
        vehicle: Vehicle,
        vehicle_data: VehicleUpdate,
    ) -> Vehicle:
        update_data = vehicle_data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(vehicle, field, value)

        await self.session.commit()
        await self.session.refresh(vehicle)

        return vehicle

    async def delete(
        self,
        vehicle: Vehicle,
    ) -> None:
        await self.session.delete(vehicle)
        await self.session.commit()  