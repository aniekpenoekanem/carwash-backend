from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Request,
    status,
)

from app.core.config import settings
from app.dependencies.payment import get_payment_service
from app.integrations.paystack_webhook import PaystackWebhook
from app.services.payment_service import PaymentService

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)


@router.post("/paystack")
async def paystack_webhook(
    request: Request,
    service: PaymentService = Depends(
        get_payment_service,
    ),
    x_paystack_signature: str = Header(),
    
):
    body = await request.body()

    if not PaystackWebhook.verify_signature(
        body,
        x_paystack_signature,
        settings.PAYSTACK_SECRET_KEY,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature.",
        )

    payload = await request.json()

    return await service.process_webhook(
        payload,
    )