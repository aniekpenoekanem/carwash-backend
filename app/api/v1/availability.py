from datetime import date

from fastapi import APIRouter, Depends, Query

from app.dependencies.availability import (
    get_availability_service,
)
from app.schemas.availability import (
    AvailabilityResponse,
)
from app.services.availability_service import (
    AvailabilityService,
)

router = APIRouter(
    prefix="/availability",
    tags=["Availability"],
)


@router.get(
    "",
    response_model=AvailabilityResponse,
)
async def get_availability(
    date: date = Query(...),
    service: AvailabilityService = Depends(
        get_availability_service,
    ),
):
    return await service.get_availability(date)