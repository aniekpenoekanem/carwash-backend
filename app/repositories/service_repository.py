from uuid import UUID

from sqlalchemy import select

from app.models.service import Service
from app.repositories.base import BaseRepository


class ServiceRepository(BaseRepository[Service]):
    def __init__(self, session):
        super().__init__(session, Service)

    async def create(
        self,
        service: Service,
    ) -> Service:
        self.session.add(service)
        await self.session.flush()
        await self.session.refresh(service)
        return service

    async def get_by_id(
        self,
        service_id: UUID,
    ) -> Service | None:
        return await self.session.get(Service, service_id)

    async def get_by_name(
        self,
        name: str,
    ) -> Service | None:
        result = await self.session.execute(
            select(Service).where(Service.name == name)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        active_only: bool = True,
    ) -> list[Service]:

        query = select(Service)

        if active_only:
            query = query.where(
                Service.is_active.is_(True)
            )

        result = await self.session.execute(
            query.order_by(Service.name)
        )

        return list(result.scalars().all())

    async def delete(
        self,
        service: Service,
    ) -> None:
        service.is_active = False

        await self.session.commit()
        await self.session.refresh(service)