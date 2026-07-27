from uuid import UUID

from fastapi import HTTPException, status

from app.models.car_model import CarModel
from app.repositories.car_brand_repository import CarBrandRepository
from app.repositories.car_model_repository import CarModelRepository
from app.schemas.car_model import (
    CarModelCreate,
    CarModelUpdate,
)


class CarModelService:
    def __init__(
        self,
        car_model_repository: CarModelRepository,
        car_brand_repository: CarBrandRepository,
    ):
        self.car_model_repository = car_model_repository
        self.car_brand_repository = car_brand_repository

    async def create(
        self,
        data: CarModelCreate,
    ) -> CarModel:

        brand = await self.car_brand_repository.get_by_id(
            data.brand_id,
        )

        if brand is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Car brand not found.",
            )

        existing = (
            await self.car_model_repository.get_by_name_and_brand(
                data.brand_id,
                data.name,
            )
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Car model already exists for this brand.",
            )

        model = CarModel(
            brand_id=data.brand_id,
            name=data.name,
            body_type=data.body_type,
        )

        return await self.car_model_repository.create(model)

    async def get_all(self):
        return await self.car_model_repository.get_all()

    async def get_by_brand(
        self,
        brand_id: UUID,
    ):
        return await self.car_model_repository.get_by_brand(
            brand_id,
        )

    async def get_by_id(
        self,
        model_id: UUID,
    ):
        model = await self.car_model_repository.get_by_id(
            model_id,
        )

        if model is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Car model not found.",
            )

        return model

    async def update(
        self,
        model_id: UUID,
        data: CarModelUpdate,
    ):
        model = await self.get_by_id(model_id)

        brand = await self.car_brand_repository.get_by_id(
            data.brand_id,
        )

        if brand is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Car brand not found.",
            )

        duplicate = (
            await self.car_model_repository.get_by_name_and_brand(
                data.brand_id,
                data.name,
            )
        )

        if duplicate and duplicate.id != model.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Car model already exists for this brand.",
            )

        model.brand_id = data.brand_id
        model.name = data.name
        model.body_type = data.body_type

        await self.car_model_repository.update()

        return model

    async def delete(
        self,
        model_id: UUID,
    ):
        model = await self.get_by_id(model_id)

        await self.car_model_repository.delete(model)