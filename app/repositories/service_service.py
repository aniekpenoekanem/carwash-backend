from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.service import Service
from app.repositories.service_repository import ServiceRepository
from app.schemas.service import (
    ServiceCreate,
    ServiceRead,
)


class ServiceService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ServiceRepository(session)

    async def create_service(
        self,
        service_data: ServiceCreate,
    ) -> ServiceRead:

        existing = await self.repository.get_by_name(
            service_data.name
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A service with this name already exists.",
            )

        service = Service(
            name=service_data.name,
            description=service_data.description,
            price=service_data.price,
        )

        await self.repository.create(service)

        await self.session.commit()

        await self.session.refresh(service)

        return ServiceRead.model_validate(service)

    async def list_services(self) -> list[ServiceRead]:
        services = await self.repository.list_all()

        return [
            ServiceRead.model_validate(service)
            for service in services
        ]