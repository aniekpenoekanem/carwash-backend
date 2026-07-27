from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.car_brand import CarBrand


class CarBrandRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, brand: CarBrand) -> CarBrand:
        self.db.add(brand)
        await self.db.commit()
        await self.db.refresh(brand)
        return brand

    async def get_all(self) -> list[CarBrand]:
        result = await self.db.execute(
            select(CarBrand).order_by(CarBrand.name)
        )
        return list(result.scalars().all())

    async def get_by_id(self, brand_id: UUID) -> CarBrand | None:
        result = await self.db.execute(
            select(CarBrand).where(CarBrand.id == brand_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> CarBrand | None:
        result = await self.db.execute(
            select(CarBrand).where(CarBrand.name == name)
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        brand: CarBrand,
    ) -> CarBrand:
        await self.db.commit()
        await self.db.refresh(brand)
        return brand

    async def delete(self, brand: CarBrand) -> None:
        await self.db.delete(brand)
        await self.db.commit()