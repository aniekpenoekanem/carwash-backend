from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment
from app.schemas.payment import PaymentUpdate


class PaymentRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create(
        self,
        payment_data: dict,
    ) -> Payment:

        payment = Payment(**payment_data)

        self.session.add(payment)

        await self.session.commit()
        await self.session.refresh(payment)

        return payment

    async def get_by_id(
        self,
        payment_id: UUID,
    ) -> Payment | None:

        return await self.session.get(
            Payment,
            payment_id,
        )

    async def get_by_booking(
        self,
        booking_id: UUID,
    ) -> Payment | None:

        result = await self.session.execute(
            select(Payment).where(
                Payment.booking_id == booking_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_reference(
        self,
        reference: str,
    ) -> Payment | None:

        result = await self.session.execute(
            select(Payment).where(
                Payment.reference == reference,
            )
        )

        return result.scalar_one_or_none()

    async def update(
        self,
        payment: Payment,
        payment_data: PaymentUpdate,
    ) -> Payment:

        update_data = payment_data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(payment, field, value)

        await self.session.commit()
        await self.session.refresh(payment)

        return payment