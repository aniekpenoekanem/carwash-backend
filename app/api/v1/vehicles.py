from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.dependencies.auth import require_customer
from app.models.user import User

from app.dependencies.vehicle import get_vehicle_service
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleResponse,
    VehicleUpdate,
)
from app.services.vehicle_service import VehicleService

router = APIRouter(
    prefix="/vehicles",
    tags=["Vehicles"],
)


@router.post(
    "/",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    current_user: User = Depends(require_customer),
    service: VehicleService = Depends(get_vehicle_service),
):
    return await service.create_vehicle(
        vehicle_data=vehicle_data,
        customer_id=current_user.customer.id,
    )

@router.get(
    "/",
    response_model=list[VehicleResponse],
)
async def get_vehicles(
    current_user: User = Depends(require_customer),
    service: VehicleService = Depends(get_vehicle_service),
):
    return await service.get_customer_vehicles(
        current_user.customer.id,
    )

@router.get(
    "/{vehicle_id}",
    response_model=VehicleResponse,
)
async def get_vehicle(
    vehicle_id: UUID,
    current_user: User = Depends(require_customer),
    service: VehicleService = Depends(get_vehicle_service),
):
    return await service.get_vehicle(
        vehicle_id,
        current_user.customer.id,
    )
    
async def get_customer_vehicles(
    customer_id: UUID,
    service: VehicleService = Depends(get_vehicle_service),
):
    return await service.get_customer_vehicles(customer_id)


@router.put(
    "/{vehicle_id}",
    response_model=VehicleResponse,
)
async def update_vehicle(
    vehicle_id: UUID,
    vehicle_data: VehicleUpdate,
    current_user: User = Depends(require_customer),
    service: VehicleService = Depends(get_vehicle_service),
):
    return await service.update_vehicle(
        vehicle_id,
        vehicle_data,
        current_user.customer.id,
    )

@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_vehicle(
    vehicle_id: UUID,
    current_user: User = Depends(require_customer),
    service: VehicleService = Depends(get_vehicle_service),
):
    await service.delete_vehicle(
        vehicle_id,
        current_user.customer.id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )