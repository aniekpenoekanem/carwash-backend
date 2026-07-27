from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from app.core.enums import BookingStatus, PaymentStatus
from app.dependencies.admin_booking import get_admin_booking_service
from app.dependencies.auth import require_admin
from app.models.user import User
from app.schemas.admin_booking import (
    AdminBookingResponse,
    BookingListResponse,
    BookingStatusUpdate,
)
from app.services.admin_booking_service import (
    AdminBookingService,
)

router = APIRouter(
    prefix="/admin/bookings",
    tags=["Admin Bookings"],
)


@router.get(
    "",
    response_model=BookingListResponse,
)
async def get_bookings(
    admin: User = Depends(require_admin),
    service: AdminBookingService = Depends(
        get_admin_booking_service,
    ),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: BookingStatus | None = None,
    payment_status: PaymentStatus | None = None,
    scheduled_date: date | None = None,
):
    return await service.get_all_bookings(
        page=page,
        size=size,
        status=status,
        payment_status=payment_status,
        scheduled_date=scheduled_date,
    )


@router.get(
    "/{booking_id}",
    response_model=AdminBookingResponse,
)
async def get_booking(
    booking_id: UUID,
    admin: User = Depends(require_admin),
    service: AdminBookingService = Depends(
        get_admin_booking_service,
    ),
):
    return await service.get_booking(
        booking_id,
    )


@router.patch(
    "/{booking_id}/status",
    response_model=AdminBookingResponse,
)
async def update_booking_status(
    booking_id: UUID,
    payload: BookingStatusUpdate,
    admin: User = Depends(require_admin),
    service: AdminBookingService = Depends(
        get_admin_booking_service,
    ),
):
    return await service.update_status(
        booking_id=booking_id,
        booking_status=payload.status,
    )


@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_booking(
    booking_id: UUID,
    admin: User = Depends(require_admin),
    service: AdminBookingService = Depends(
        get_admin_booking_service,
    ),
):
    await service.delete_booking(
        booking_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )