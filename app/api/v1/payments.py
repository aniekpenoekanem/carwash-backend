from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)

from app.dependencies.auth import require_customer
from app.dependencies.payment import get_payment_service
from app.models.customer import Customer
from app.services.payment_service import PaymentService
from app.models.user import User

router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@router.post("/initialize")
async def initialize_payment(
    booking_id: UUID,
    service: PaymentService = Depends(get_payment_service),
    current_user: User = Depends(require_customer),
):
    return await service.initialize_payment(
        booking_id=booking_id,
        customer_id=current_user.customer.id,
        customer_email=current_user.email,
    )
    
@router.get("/verify/{reference}")
async def verify_payment(
    reference: str,
    service: PaymentService = Depends(
        get_payment_service,
    ),
):
    return await service.verify_payment(
        reference,
    )
    
@router.post("/webhook")
async def payment_webhook(
    request: Request,
    service: PaymentService = Depends(
        get_payment_service,
    ),
):
    payload = await request.body()

    signature = request.headers.get(
        "x-paystack-signature",
    )

    if signature is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Paystack signature.",
        )

    if not service.verify_webhook_signature(
        payload,
        signature,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Paystack signature.",
        )

    return await service.process_webhook(
        await request.json(),
    )