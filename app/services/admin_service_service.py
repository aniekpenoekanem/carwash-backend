from uuid import UUID

from fastapi import HTTPException, status

from app.models.service import Service
from app.repositories.admin_service_repository import (
    AdminServiceRepository,
)
from app.schemas.admin_service import ServiceListResponse
from app.schemas.service import (
    ServiceCreate,
    ServiceRead,
    ServiceUpdate,
)


class AdminServiceService:
    def __init__(
        self,
        repository: AdminServiceRepository,
    ):
        self.repository = repository

    async def get_all_services(
        self,
        page: int = 1,
        size: int = 20,
    ) -> ServiceListResponse:

        services, total = await self.repository.get_all(
            page=page,
            size=size,
        )

        return ServiceListResponse(
            items=[
                ServiceRead.model_validate(service)
                for service in services
            ],
            total=total,
            page=page,
            size=size,
        )

    async def get_service(
        self,
        service_id: UUID,
    ) -> ServiceRead:

        service = await self.repository.get_by_id(
            service_id,
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        return ServiceRead.model_validate(service)

    async def create_service(
        self,
        data: ServiceCreate,
    ) -> ServiceRead:

        existing = await self.repository.get_by_name(
            data.name,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service name already exists.",
            )

        service = Service(
            name=data.name,
            description=data.description,
            price=data.price,
        )

        service = await self.repository.create(
            service,
        )

        return ServiceRead.model_validate(service)

    async def update_service(
        self,
        service_id: UUID,
        data: ServiceUpdate,
    ) -> ServiceRead:

        service = await self.repository.get_by_id(
            service_id,
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        if (
            data.name is not None
            and data.name != service.name
        ):
            existing = await self.repository.get_by_name(
                data.name,
            )

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Service name already exists.",
                )

            service.name = data.name

        if data.description is not None:
            service.description = data.description

        if data.price is not None:
            service.price = data.price

        if data.is_active is not None:
            service.is_active = data.is_active

        service = await self.repository.update(
            service,
        )

        return ServiceRead.model_validate(service)

    async def delete_service(
        self,
        service_id: UUID,
    ) -> ServiceRead:

        service = await self.repository.get_by_id(
            service_id,
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        service = await self.repository.soft_delete(
            service,
        )

        return ServiceRead.model_validate(service)