from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Query

from app.db.database import get_session
from app.dependencies.auth import require_admin
from app.models.user import User
from app.schemas.service import (
    ServiceCreate,
    ServiceRead,
    ServiceUpdate,
)
from app.services.service_service import ServiceService

router = APIRouter(
    prefix="/services",
    tags=["Services"],
)


@router.post(
    "",
    response_model=ServiceRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_service(
    service: ServiceCreate,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    return await ServiceService(session).create_service(service)


@router.get(
    "",
    response_model=list[ServiceRead],
)
async def list_services(
    active_only: bool = Query(True),
    session: AsyncSession = Depends(get_session),
):
    return await ServiceService(session).list_services(
        active_only=active_only,
    )


@router.put(
    "/{service_id}",
    response_model=ServiceRead,
)
async def update_service(
    service_id: UUID,
    service: ServiceUpdate,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    return await ServiceService(session).update_service(
        service_id,
        service,
    )

@router.get(
    "/{service_id}",
    response_model=ServiceRead,
)
async def get_service(
    service_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    return await ServiceService(session).get_service(
        service_id,
    )

@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_service(
    service_id: UUID,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    await ServiceService(session).delete_service(
        service_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )