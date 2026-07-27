from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session

from app.integrations.paystack_client import PaystackClient
from app.repositories.booking_repository import BookingRepository
from app.repositories.payment_repository import PaymentRepository
from app.services.payment_service import PaymentService


def get_payment_service(
    session: AsyncSession = Depends(get_session),
) -> PaymentService:

    booking_repository = BookingRepository(session)
    payment_repository = PaymentRepository(session)
    paystack_client = PaystackClient()

    return PaymentService(
        payment_repository=payment_repository,
        booking_repository=booking_repository,
        paystack_client=paystack_client,
    )