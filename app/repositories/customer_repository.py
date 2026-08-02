from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer


class CustomerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, customer_id: UUID) -> Customer | None:
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> Customer | None:
        result = await self.db.execute(
            select(Customer).where(Customer.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, customer: Customer) -> Customer:
        self.db.add(customer)
        await self.db.flush()
        await self.db.refresh(customer)
        return customer
    
    async def update(
        self,
        customer: Customer,
    ) -> Customer:
        self.db.add(customer)

        await self.db.flush()

        await self.db.refresh(customer)

        return customer