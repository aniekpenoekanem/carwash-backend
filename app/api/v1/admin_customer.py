from uuid import UUID

from fastapi import APIRouter, Depends, Query
from decimal import Decimal
from app.dependencies.admin_customer import (
    get_admin_customer_service,
)
from app.dependencies.auth import require_admin
from app.models.user import User
from app.schemas.admin_customer import (
    AdminCustomerResponse,
    AdminCustomerDetailsResponse,
    CustomerListResponse,
    CustomerStatusUpdate,
)
from app.services.admin_customer_service import (
    AdminCustomerService,
)

router = APIRouter(
    prefix="/admin/customers",
    tags=["Admin Customers"],
)


@router.get(
    "",
    response_model=CustomerListResponse,
)
async def list_customers(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    admin: User = Depends(require_admin),
    service: AdminCustomerService = Depends(
        get_admin_customer_service,
    ),
):
    return await service.get_all_customers(
        page=page,
        size=size,
        search=search,
    )


@router.get(
    "/{customer_id}",
    response_model=AdminCustomerResponse,
)
async def get_customer(
    customer_id: UUID,
    admin: User = Depends(require_admin),
    service: AdminCustomerService = Depends(
        get_admin_customer_service,
    ),
):
    return await service.get_customer(
        customer_id,
    )


@router.patch(
    "/{customer_id}/status",
    response_model=AdminCustomerResponse,
)
async def update_customer_status(
    customer_id: UUID,
    status_data: CustomerStatusUpdate,
    admin: User = Depends(require_admin),
    service: AdminCustomerService = Depends(
        get_admin_customer_service,
    ),
):
    return await service.update_status(
        customer_id,
        status_data,
    )

    
@router.get(
    "/{customer_id}/details",
    response_model=AdminCustomerDetailsResponse,
)
async def get_customer_details(
    customer_id: UUID,
    admin: User = Depends(require_admin),
    service: AdminCustomerService = Depends(
        get_admin_customer_service,
    ),
):
    return await service.get_customer_details(
        customer_id,
    )    