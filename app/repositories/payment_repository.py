from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment
from app.models.booking import Booking
from app.models.customer import Customer
from app.core.enums import PaymentStatus
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
    
    async def get_all_paginated(
        self,
        page: int,
        size: int,
        search: str | None = None,
        status: PaymentStatus | None = None,
        ) -> list[Payment]:

        query = (
            select(Payment)
            .options(
                joinedload(Payment.booking)
                    .joinedload(Booking.customer),

                joinedload(Payment.booking)
                    .joinedload(Booking.vehicle),

                joinedload(Payment.booking)
                    .joinedload(Booking.service),
            )
        )

        if status is not None:
            query = query.where(
                Payment.status == status,
            )

        query = (
            query.order_by(Payment.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )

        result = await self.session.execute(query)

        payments = result.scalars().unique().all()

        print("================================")
        print("PAYMENTS FOUND:", len(payments))
        for payment in payments:
            print(payment.id, payment.reference)
        print("================================")

        return payments
    
    
    async def count(
        self,
        search: str | None = None,
        status: PaymentStatus | None = None,
    ) -> int:

        query = (
            select(func.count(Payment.id))
            .join(Payment.booking)
            .join(Booking.customer)
        )

        if search:
            search_term = f"%{search}%"

            query = query.where(
                or_(
                    Payment.reference.ilike(search_term),
                    Customer.first_name.ilike(search_term),
                    Customer.last_name.ilike(search_term),
                    Customer.email.ilike(search_term),
                )
            )

        if status is not None:
            query = query.where(
                Payment.status == status,
            )

        result = await self.session.execute(query)

        return result.scalar_one()

    async def get_admin_by_id(
        self,
        payment_id: UUID,
    ) -> Payment | None:

        result = await self.session.execute(
            select(Payment)
            .where(Payment.id == payment_id)
            .options(
                joinedload(Payment.booking)
                .joinedload(Booking.customer),

                joinedload(Payment.booking)
                .joinedload(Booking.vehicle),

                joinedload(Payment.booking)
                .joinedload(Booking.service),
            )
        )

        return result.scalar_one_or_none()