from uuid import UUID

from sqlalchemy import select

from app.models.vehicle import Vehicle
from app.repositories.base import BaseRepository


class VehicleRepository(BaseRepository[Vehicle]):
    def __init__(self, session):
        super().__init__(session, Vehicle)

    async def get_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        return await self.session.get(Vehicle, vehicle_id)

    async def get_by_plate_number(self, plate_number: str) -> Vehicle | None:
        result = await self.session.execute(
            select(Vehicle).where(
                Vehicle.plate_number == plate_number
            )
        )
        return result.scalar_one_or_none()

    async def create(self, vehicle: Vehicle) -> Vehicle:
        self.session.add(vehicle)
        await self.session.flush()
        await self.session.refresh(vehicle)
        return vehicle