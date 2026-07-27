from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.service import Service


class AdminServiceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
        self,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Service], int]:

        total = await self.session.scalar(
            select(func.count()).select_from(Service)
        )

        result = await self.session.scalars(
            select(Service)
            .order_by(Service.name)
            .offset((page - 1) * size)
            .limit(size)
        )

        return list(result.all()), total or 0

    async def get_by_id(
        self,
        service_id: UUID,
    ) -> Service | None:

        return await self.session.get(
            Service,
            service_id,
        )

    async def get_by_name(
        self,
        name: str,
    ) -> Service | None:

        result = await self.session.scalar(
            select(Service).where(Service.name == name)
        )

        return result

    async def create(
        self,
        service: Service,
    ) -> Service:

        self.session.add(service)
        await self.session.commit()
        await self.session.refresh(service)

        return service

    async def update(
        self,
        service: Service,
    ) -> Service:

        await self.session.commit()
        await self.session.refresh(service)

        return service

    async def soft_delete(
        self,
        service: Service,
    ) -> Service:

        service.is_active = False

        await self.session.commit()
        await self.session.refresh(service)

        return service