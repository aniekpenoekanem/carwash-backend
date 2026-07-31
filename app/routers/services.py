from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.service import ServiceRead
from app.services.service_service import ServiceService

router = APIRouter(
    prefix="/services",
    tags=["Services"],
)


@router.get(
    "",
    response_model=list[ServiceRead],
)
async def list_services(
    session: AsyncSession = Depends(get_session),
):
    service = ServiceService(session)
    return await service.list_services(active_only=True)