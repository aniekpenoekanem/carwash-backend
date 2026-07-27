from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from app.models.customer import Customer
from app.repositories.base import BaseRepository


class AdminCustomerRepository(
    BaseRepository[Customer],
):
    def __init__(self, session):
        super().__init__(session, Customer)

    async def get_all(
        self,
        page: int = 1,
        size: int = 20,
        search: str | None = None,
    ) -> tuple[list[Customer], int]:

        query = select(Customer)

        if search:
            query = query.where(
                or_(
                    Customer.first_name.ilike(f"%{search}%"),
                    Customer.last_name.ilike(f"%{search}%"),
                    Customer.email.ilike(f"%{search}%"),
                    Customer.phone.ilike(f"%{search}%"),
                )
            )

        count_query = select(
            func.count()
        ).select_from(query.subquery())

        total = await self.session.scalar(count_query)

        result = await self.session.execute(
            query.order_by(Customer.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )

        return (
            list(result.scalars().all()),
            total or 0,
        )

    async def get_by_id(
        self,
        customer_id: UUID,
    ) -> Customer | None:
        return await self.session.get(
            Customer,
            customer_id,
        )

    async def update(
        self,
        customer: Customer,
    ) -> Customer:

        await self.session.commit()
        await self.session.refresh(customer)

        return customer
    
    async def get_customer_details(
        self,
        customer_id: UUID,
    ) -> Customer | None:

        result = await self.session.execute(
            select(Customer)
            .where(Customer.id == customer_id)
            .options(
                selectinload(Customer.vehicles),
                selectinload(Customer.bookings),
            )
        )

        return result.scalar_one_or_none()