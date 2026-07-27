from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session

from app.repositories.booking_repository import BookingRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.vehicle_repository import VehicleRepository

from app.services.booking_service import BookingService


def get_booking_service(
    db: AsyncSession = Depends(get_session),
) -> BookingService:
    booking_repository = BookingRepository(db)
    customer_repository = CustomerRepository(db)
    vehicle_repository = VehicleRepository(db)
    service_repository = ServiceRepository(db)

    return BookingService(
        booking_repository=booking_repository,
        customer_repository=customer_repository,
        vehicle_repository=vehicle_repository,
        service_repository=service_repository,
    )