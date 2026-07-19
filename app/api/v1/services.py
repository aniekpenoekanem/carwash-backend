from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.schemas.service import ServiceCreate, ServiceRead
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
    session: AsyncSession = Depends(get_session),
):
    return await ServiceService(session).create_service(service)


@router.get(
    "",
    response_model=list[ServiceRead],
)
async def list_services(
    session: AsyncSession = Depends(get_session),
):
    return await ServiceService(session).list_services()