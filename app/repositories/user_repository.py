import email
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.customer))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.customer))
            .where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def exists_by_email(
        self,
        email: str,
    ) -> bool:
        return (
            await self.get_by_email(email)
    ) is not None
        
    async def exists_by_phone_number(
        self,
        phone_number: str,
    ) -> bool:
        return (
            await self.get_by_phone_number(phone_number)
    ) is not None    

    async def get_by_phone_number(self, phone_number: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.phone_number == phone_number)
        )
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user