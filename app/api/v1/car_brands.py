from uuid import UUID

from fastapi import Response

from app.dependencies.auth import require_admin
from app.models.user import User

from fastapi import APIRouter, Depends, status

from app.dependencies.car_brand import get_car_brand_service
from app.schemas.car_brand import (
    CarBrandCreate,
    CarBrandResponse,
    CarBrandUpdate,
)
from app.services.car_brand_service import CarBrandService

router = APIRouter(prefix="/car-brands", tags=["Car Brands"])


@router.get(
    "/",
    response_model=list[CarBrandResponse],
)
async def get_car_brands(
    service: CarBrandService = Depends(get_car_brand_service),
):
    return await service.get_all()


@router.get(
    "/{brand_id}",
    response_model=CarBrandResponse,
)
async def get_car_brand(
    brand_id: UUID,
    service: CarBrandService = Depends(get_car_brand_service),
):
    return await service.get_by_id(brand_id)


@router.post(
    "/",
    response_model=CarBrandResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_car_brand(
    data: CarBrandCreate,
    admin: User = Depends(require_admin),
    service: CarBrandService = Depends(get_car_brand_service),
):
    return await service.create(data)


@router.put(
    "/{brand_id}",
    response_model=CarBrandResponse,
)
async def update_car_brand(
    brand_id: UUID,
    data: CarBrandUpdate,
    service: CarBrandService = Depends(get_car_brand_service),
):
    return await service.update(brand_id, data)


@router.delete(
    "/{brand_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_car_brand(
    brand_id: UUID,
    admin: User = Depends(require_admin),
    service: CarBrandService = Depends(get_car_brand_service),
):
    await service.delete(brand_id)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
