from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.security import require_admin
from app.dependencies.admin_service import (
    get_admin_service_service,
)
from app.models.user import User
from app.schemas.admin_service import ServiceListResponse
from app.schemas.service import (
    ServiceCreate,
    ServiceRead,
    ServiceUpdate,
)
from app.services.admin_service_service import (
    AdminServiceService,
)

router = APIRouter(
    prefix="/admin/services",
    tags=["Admin Services"],
)


@router.get(
    "",
    response_model=ServiceListResponse,
)
async def get_services(
    page: int = 1,
    size: int = 20,
    _: User = Depends(require_admin),
    service: AdminServiceService = Depends(
        get_admin_service_service,
    ),
):
    return await service.get_all_services(
        page,
        size,
    )


@router.get(
    "/{service_id}",
    response_model=ServiceRead,
)
async def get_service(
    service_id: UUID,
    _: User = Depends(require_admin),
    service: AdminServiceService = Depends(
        get_admin_service_service,
    ),
):
    return await service.get_service(service_id)


@router.post(
    "",
    response_model=ServiceRead,
    status_code=201,
)
async def create_service(
    data: ServiceCreate,
    _: User = Depends(require_admin),
    service: AdminServiceService = Depends(
        get_admin_service_service,
    ),
):
    return await service.create_service(data)


@router.patch(
    "/{service_id}",
    response_model=ServiceRead,
)
async def update_service(
    service_id: UUID,
    data: ServiceUpdate,
    _: User = Depends(require_admin),
    service: AdminServiceService = Depends(
        get_admin_service_service,
    ),
):
    return await service.update_service(
        service_id,
        data,
    )


@router.delete(
    "/{service_id}",
    response_model=ServiceRead,
)
async def delete_service(
    service_id: UUID,
    _: User = Depends(require_admin),
    service: AdminServiceService = Depends(
        get_admin_service_service,
    ),
):
    return await service.delete_service(
        service_id,
    )