from uuid import UUID

from fastapi import HTTPException, status
from decimal import Decimal
from app.repositories.admin_customer_repository import (
    AdminCustomerRepository,
)
from app.schemas.admin_customer import (
    AdminCustomerResponse,
    AdminCustomerDetailsResponse,
    CustomerListResponse,
    CustomerStatusUpdate,
)


class AdminCustomerService:
    def __init__(self, repository: AdminCustomerRepository):
        self.repository = repository

    async def get_all_customers(
        self,
        page: int = 1,
        size: int = 20,
        search: str | None = None,
    ) -> CustomerListResponse:

        customers, total = await self.repository.get_all(
            page=page,
            size=size,
            search=search,
        )

        return CustomerListResponse(
            items=[
                AdminCustomerResponse.model_validate(customer)
                for customer in customers
            ],
            total=total,
            page=page,
            size=size,
        )

    async def get_customer(
        self,
        customer_id: UUID,
    ) -> AdminCustomerResponse:

        customer = await self.repository.get_by_id(
            customer_id,
        )

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )

        return AdminCustomerResponse.model_validate(
            customer,
        )

    async def update_status(
        self,
        customer_id: UUID,
        status_data: CustomerStatusUpdate,
    ) -> AdminCustomerResponse:

        customer = await self.repository.get_by_id(
            customer_id,
        )

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )

        customer.is_active = status_data.is_active

        customer = await self.repository.update(
            customer,
        )

        return AdminCustomerResponse.model_validate(
            customer,
        )
        
    async def get_customer_details(
        self,
        customer_id: UUID,
    ) -> AdminCustomerDetailsResponse:

        customer = await self.repository.get_customer_details(
            customer_id,
        )

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )

        total_spent = sum(
            (
                booking.price_at_booking
                for booking in customer.bookings
            ),
            Decimal("0.00"),
        )

        return AdminCustomerDetailsResponse(
            **AdminCustomerResponse.model_validate(
                customer
            ).model_dump(),
            vehicles=customer.vehicles,
            bookings=customer.bookings,
            total_bookings=len(customer.bookings),
            total_spent=total_spent,
        )