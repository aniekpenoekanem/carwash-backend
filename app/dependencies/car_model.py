from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.repositories.car_brand_repository import CarBrandRepository
from app.repositories.car_model_repository import CarModelRepository
from app.services.car_model_service import CarModelService


def get_car_model_service(
    db: AsyncSession = Depends(get_session),
) -> CarModelService:
    car_model_repository = CarModelRepository(db)
    car_brand_repository = CarBrandRepository(db)

    return CarModelService(
        car_model_repository=car_model_repository,
        car_brand_repository=car_brand_repository,
    )