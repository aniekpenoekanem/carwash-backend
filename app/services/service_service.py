from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.service import Service
from app.repositories.service_repository import ServiceRepository
from app.schemas.service import (
    ServiceCreate,
    ServiceRead,
    ServiceUpdate,
)
from uuid import UUID


class ServiceService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ServiceRepository(session)

    async def create_service(self, service_data: ServiceCreate) -> ServiceRead:
        existing = await self.repository.get_by_name(service_data.name)

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
    
    async def get_service(
        self,
        service_id: UUID,
    ) -> ServiceRead:

        service = await self.repository.get_by_id(service_id)

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        return ServiceRead.model_validate(service)
    
    async def update_service(
        self,
        service_id: UUID,
        service_data: ServiceUpdate,
    ) -> ServiceRead:

        service = await self.repository.get_by_id(service_id)

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        if (
            service_data.name is not None
            and service_data.name != service.name
        ):
            existing = await self.repository.get_by_name(
                service_data.name,
            )

            if existing is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A service with this name already exists.",
                )

        for field, value in service_data.model_dump(
            exclude_unset=True,
        ).items():
            setattr(service, field, value)

        await self.session.commit()
        await self.session.refresh(service)

        return ServiceRead.model_validate(service)
    
    
    async def delete_service(
        self,
        service_id: UUID,
    ) -> None:

        service = await self.repository.get_by_id(
            service_id,
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        service.is_active = False
        
        await self.session.commit()
        await self.session.refresh(service)
        
    async def list_services(
        self,
        active_only: bool = True,
    ) -> list[ServiceRead]:

        services = await self.repository.list_all(
            active_only=active_only,
        )

        return [
            ServiceRead.model_validate(service)
            for service in services
        ]