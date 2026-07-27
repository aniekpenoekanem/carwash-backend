from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from app.integrations.paystack_client import PaystackClient

from app.repositories.booking_repository import BookingRepository
from app.repositories.payment_repository import PaymentRepository

from datetime import datetime, timezone

from app.core.enums import BookingStatus, PaymentStatus
from app.schemas.booking import BookingUpdate
from app.schemas.payment import PaymentUpdate


class PaymentService:
    def __init__(
        self,
        payment_repository: PaymentRepository,
        booking_repository: BookingRepository,
        paystack_client: PaystackClient,
    ):
        self.payment_repository = payment_repository
        self.booking_repository = booking_repository
        self.paystack_client = paystack_client

    def generate_reference(self) -> str:
        return f"CW-{uuid4().hex.upper()}"

    async def initialize_payment(
        self,
        booking_id: UUID,
        customer_id: UUID,
        customer_email: str,
    ) -> dict:

        # Retrieve booking
        booking = await self.booking_repository.get_by_id(
            booking_id,
        )

        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )

        if booking.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to pay for this booking.",
            )

        # Prevent payment for cancelled bookings
        if booking.status == BookingStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cancelled bookings cannot be paid.",
            )

        # Prevent paying an already-paid booking
        if booking.payment_status == PaymentStatus.PAID:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking has already been paid.",
            )

        # Prevent duplicate payment initialization
        existing_payment = (
            await self.payment_repository.get_by_booking(
                booking_id,
            )
        )

        if existing_payment is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Payment has already been initialized for this booking.",
            )

        reference = self.generate_reference()

        amount_in_kobo = int(
            booking.price_at_booking * 100,
        )

        payment_data = await self.paystack_client.initialize_transaction(
            email=customer_email,
            amount=amount_in_kobo,
            reference=reference,
            metadata={
                "booking_id": str(booking.id),
            }
        )

        await self.payment_repository.create(
            {
                "booking_id": booking.id,
                "amount": booking.price_at_booking,
                "reference": payment_data["reference"],
                "access_code": payment_data["access_code"],
                "authorization_url": payment_data[
                    "authorization_url"
                ],
            }
        )

        return {
            "authorization_url": payment_data[
                "authorization_url"
            ],
            "access_code": payment_data["access_code"],
            "reference": payment_data["reference"],
        }
        
    async def verify_payment(
        self,
        reference: str,
    ) -> dict:
        
        gateway_data = await self.paystack_client.verify_transaction(
            reference,
        )

        return await self._update_payment_status(
            reference,
            gateway_data,
        )
        
    async def _update_payment_status(
        self,
        reference: str,
        gateway_data: dict[str, Any]
    ) -> dict:

        payment = await self.payment_repository.get_by_reference(
            reference,
        )

        if payment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found.",
            )

        if payment.status == PaymentStatus.PAID:
            return {
                "message": "Duplicate webhook ignored. Payment already verified.",
                "reference": payment.reference,
                "booking_id": str(payment.booking_id),
            }

        print("Paystack verification response:")
        print(gateway_data)

        if gateway_data.get("status") != "success":
            payment = await self.payment_repository.update(
                payment,
                PaymentUpdate(
                    status=PaymentStatus.FAILED,
                    gateway_response=gateway_data.get(
                        "gateway_response",
                    ),
                ),
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment was not successful.",
            )

        gateway_amount = gateway_data.get("amount")

        if gateway_amount is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment amount not returned by Paystack.",
            )

        expected_amount = int(payment.amount * 100)

        if gateway_amount != expected_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment amount mismatch.",
            )
            
        payment = await self.payment_repository.update(
            payment,
            PaymentUpdate(
                status=PaymentStatus.PAID,
                gateway_response=gateway_data.get(
                    "gateway_response",
                ),
                paid_at=datetime.now(timezone.utc),
            ),
        )

        booking = await self.booking_repository.get_by_id(
            payment.booking_id,
        )

        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )
        
        await self.booking_repository.update(
            booking,
            BookingUpdate(
                status=BookingStatus.CONFIRMED,
                payment_status=PaymentStatus.PAID,
            ),
        )

        return {
            "message": "Payment verified successfully.",
            "reference": payment.reference,
            "booking_id": str(payment.booking_id),
        }

    async def process_webhook(
        self,
        payload: dict,
    ) -> dict:

        if payload.get("event") != "charge.success":
            return {
                "message": "Event ignored.",
            }

        gateway_data = payload["data"]

        return await self._update_payment_status(
            gateway_data["reference"],
            gateway_data,
        ) 
    