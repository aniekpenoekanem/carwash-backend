from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.repositories.car_brand_repository import CarBrandRepository
from app.repositories.car_model_repository import CarModelRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.booking_repository import BookingRepository
from app.services.vehicle_service import VehicleService


def get_vehicle_service(
    db: AsyncSession = Depends(get_session),
) -> VehicleService:
    vehicle_repository = VehicleRepository(db)
    customer_repository = CustomerRepository(db)
    car_brand_repository = CarBrandRepository(db)
    car_model_repository = CarModelRepository(db)
    booking_repository = BookingRepository(db)

    return VehicleService(
        vehicle_repository=vehicle_repository,
        customer_repository=customer_repository,
        car_brand_repository=car_brand_repository,
        car_model_repository=car_model_repository,
        booking_repository=booking_repository,
    )