from fastapi import APIRouter, Depends, Query
from uuid import UUID

from app.core.enums import PaymentStatus
from app.dependencies.admin import get_admin_service
from app.dependencies.payment import get_payment_service
from app.dependencies.auth import require_admin
from app.schemas.admin_payment import (AdminPaymentDetails, AdminPaymentListResponse)
from app.models.user import User
from app.schemas.admin import DashboardResponse

from app.services.admin_service import AdminService
from app.services.payment_service import PaymentService

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.get(
    "/dashboard",
    response_model=DashboardResponse,
)
async def dashboard(
    admin: User = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
):
    return await service.dashboard()


@router.get(
    "/payments",
    response_model=AdminPaymentListResponse,
)
async def get_payments(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    status: PaymentStatus | None = None,
    admin: User = Depends(require_admin),
    service: PaymentService = Depends(get_payment_service),
):
    return await service.get_payments(
        page=page,
        size=size,
        search=search,
        status=status,
    )


@router.get(
    "/payments/{payment_id}",
    response_model=AdminPaymentDetails,
)
async def get_payment(
    payment_id: UUID,
    admin: User = Depends(require_admin),
    service: PaymentService = Depends(get_payment_service),
):
    return await service.get_payment_details(
        payment_id,
    )