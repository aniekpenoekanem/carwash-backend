from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi import Response

from app.dependencies.auth import require_admin
from app.models.user import User

from app.dependencies.car_model import get_car_model_service
from app.schemas.car_model import (
    CarModelCreate,
    CarModelResponse,
    CarModelUpdate,
)
from app.services.car_model_service import CarModelService

router = APIRouter(
    prefix="/car-models",
    tags=["Car Models"],
)


@router.post(
    "/",
    response_model=CarModelResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_car_model(
    data: CarModelCreate,
    admin: User = Depends(require_admin),
    service: CarModelService = Depends(get_car_model_service),
):
    return await service.create(data)


@router.get(
    "/",
    response_model=list[CarModelResponse],
)
async def get_car_models(
    brand_id: UUID | None = Query(default=None),
    service: CarModelService = Depends(get_car_model_service),
):
    if brand_id:
        return await service.get_by_brand(brand_id)

    return await service.get_all()


@router.get(
    "/{model_id}",
    response_model=CarModelResponse,
)
async def get_car_model(
    model_id: UUID,
    service: CarModelService = Depends(get_car_model_service),
):
    return await service.get_by_id(model_id)


@router.put(
    "/{model_id}",
    response_model=CarModelResponse,
)
async def update_car_model(
    model_id: UUID,
    data: CarModelUpdate,
    admin: User = Depends(require_admin),
    service: CarModelService = Depends(get_car_model_service),
):
    return await service.update(model_id, data)


@router.delete(
    "/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_car_model(
    model_id: UUID,
    admin: User = Depends(require_admin),
    service: CarModelService = Depends(get_car_model_service),
):
    await service.delete(model_id)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
    
    