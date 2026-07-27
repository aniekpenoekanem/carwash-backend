from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.repositories.car_brand_repository import CarBrandRepository
from app.services.car_brand_service import CarBrandService


def get_car_brand_service(
    db: AsyncSession = Depends(get_session),
) -> CarBrandService:
    repository = CarBrandRepository(db)
    return CarBrandService(repository)
