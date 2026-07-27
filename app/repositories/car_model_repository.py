from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.car_brand import CarBrand
from app.models.car_model import CarModel

class CarModelRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, car_model: CarModel) -> CarModel:
        self.db.add(car_model)
        await self.db.commit()
        await self.db.refresh(car_model)
        return car_model

    async def get_all(self) -> list[CarModel]:
        result = await self.db.execute(
            select(CarModel)
            .join(CarBrand)
            .order_by(
            CarBrand.name,
            CarModel.name,
        )
    )
        return list(result.scalars().all())

    async def get_by_id(self, model_id: UUID) -> CarModel | None:
        result = await self.db.execute(
            select(CarModel).where(
                CarModel.id == model_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_brand(
        self,
        brand_id: UUID,
    ) -> list[CarModel]:
        result = await self.db.execute(
            select(CarModel)
            .where(CarModel.brand_id == brand_id)
            .order_by(CarModel.name)
        )
        return list(result.scalars().all())

    async def get_by_name_and_brand(
        self,
        brand_id: UUID,
        name: str,
    ) -> CarModel | None:
        result = await self.db.execute(
            select(CarModel).where(
                CarModel.brand_id == brand_id,
                CarModel.name == name,
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        car_model: CarModel,
    ) -> CarModel:
        await self.db.commit()
        await self.db.refresh(car_model)
        return car_model

    async def delete(
        self,
        car_model: CarModel,
    ) -> None:
        await self.db.delete(car_model)
        await self.db.commit()
        
    async def exists(
        self,
        brand_id: UUID,
        name: str,
    ) -> bool:
        return (
            await self.get_by_name_and_brand(
                brand_id,
                name,
            )
        ) is not None