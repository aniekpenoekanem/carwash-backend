from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.service import (
    ServiceCreate,
    ServiceRead,
    ServiceUpdate,
)
from app.services.service_service import ServiceService

router = APIRouter(
    prefix="/admin/services",
    tags=["Admin Services"],
)


@router.get(
    "",
    response_model=list[ServiceRead],
)
async def list_services(
    active_only: bool = Query(False),
    session: AsyncSession = Depends(get_session),
):
    service = ServiceService(session)
    return await service.list_services(active_only=active_only)


@router.get(
    "/{service_id}",
    response_model=ServiceRead,
)
async def get_service(
    service_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    service = ServiceService(session)
    return await service.get_service(service_id)


@router.post(
    "",
    response_model=ServiceRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_service(
    service_data: ServiceCreate,
    session: AsyncSession = Depends(get_session),
):
    service = ServiceService(session)
    return await service.create_service(service_data)


@router.put(
    "/{service_id}",
    response_model=ServiceRead,
)
async def update_service(
    service_id: UUID,
    service_data: ServiceUpdate,
    session: AsyncSession = Depends(get_session),
):
    service = ServiceService(session)
    return await service.update_service(
        service_id,
        service_data,
    )


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_service(
    service_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    service = ServiceService(session)
    await service.delete_service(service_id)