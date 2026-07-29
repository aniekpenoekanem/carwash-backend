from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.schemas.booking_history import BookingHistoryResponse

from app.dependencies.auth import require_customer
from app.dependencies.booking import get_booking_service
from app.models.user import User
from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    BookingUpdate,
)
from app.services.booking_service import BookingService

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(require_customer),
    service: BookingService = Depends(get_booking_service),
):
    return await service.create_booking(
        booking_data=booking_data,
        customer_id=current_user.customer.id,
    )


@router.get(
    "/",
    response_model=list[BookingResponse],
)
async def get_bookings(
    current_user: User = Depends(require_customer),
    service: BookingService = Depends(get_booking_service),
):
    return await service.get_customer_bookings(
        current_user.customer.id,
    )

@router.get(
    "/history",
    response_model=list[BookingHistoryResponse],
)
async def get_booking_history(
    current_user: User = Depends(require_customer),
    service: BookingService = Depends(get_booking_service),
):
    return await service.get_booking_history(
        current_user.customer.id,
    )

@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
)
async def get_booking(
    booking_id: UUID,
    current_user: User = Depends(require_customer),
    service: BookingService = Depends(get_booking_service),
):
    return await service.get_booking(
        booking_id=booking_id,
        customer_id=current_user.customer.id,
    )


@router.put(
    "/{booking_id}",
    response_model=BookingResponse,
)
async def update_booking(
    booking_id: UUID,
    booking: BookingUpdate,
    current_user: User = Depends(require_customer),
    service: BookingService = Depends(get_booking_service),
):
    return await service.update_booking(
        booking_id=booking_id,
        booking_data=booking,
        customer_id=current_user.customer.id,
    )


@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_booking(
    booking_id: UUID,
    current_user: User = Depends(require_customer),
    service: BookingService = Depends(get_booking_service),
):
    await service.delete_booking(
        booking_id=booking_id,
        customer_id=current_user.customer.id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )