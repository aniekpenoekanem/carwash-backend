from uuid import UUID

from sqlalchemy import select

from app.models.customer import Customer
from app.repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, session):
        super().__init__(session, Customer)

    async def get_by_id(self, customer_id: UUID) -> Customer | None:
        return await self.session.get(Customer, customer_id)

    async def get_by_email(self, email: str) -> Customer | None:
        result = await self.session.execute(
            select(Customer).where(Customer.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, customer: Customer) -> Customer:
        self.session.add(customer)
        await self.session.flush()
        await self.session.refresh(customer)
        return customer