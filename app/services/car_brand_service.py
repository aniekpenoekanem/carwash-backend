from uuid import UUID

from fastapi import HTTPException, status

from app.models.car_brand import CarBrand
from app.repositories.car_brand_repository import CarBrandRepository
from app.schemas.car_brand import (
    CarBrandCreate,
    CarBrandUpdate,
)


class CarBrandService:
    def __init__(self, repository: CarBrandRepository):
        self.repository = repository

    async def create(self, data: CarBrandCreate) -> CarBrand:
        existing = await self.repository.get_by_name(data.name)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Car brand already exists.",
            )

        brand = CarBrand(name=data.name)

        return await self.repository.create(brand)

    async def get_all(self):
        return await self.repository.get_all()

    async def get_by_id(self, brand_id: UUID):
        brand = await self.repository.get_by_id(brand_id)

        if brand is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Car brand not found.",
            )

        return brand

    async def update(
        self,
        brand_id: UUID,
        data: CarBrandUpdate,
    ):
        brand = await self.get_by_id(brand_id)

        if (
            data.name is not None
            and data.name != brand.name
        ):
            duplicate = await self.repository.get_by_name(
            data.name,
        )

            if duplicate:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Car brand already exists.",
                )

        for field, value in data.model_dump(
            exclude_unset=True,
        ).items():
            setattr(brand, field, value)

        await self.repository.update()

        return brand

    async def delete(self, brand_id: UUID):
        brand = await self.get_by_id(brand_id)

        await self.repository.delete(brand)