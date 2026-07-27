from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status

from app.models.vehicle import Vehicle
from app.repositories.car_brand_repository import CarBrandRepository
from app.repositories.car_model_repository import CarModelRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.booking_repository import BookingRepository
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


class VehicleService:
    def __init__(
        self,
        vehicle_repository: VehicleRepository,
        customer_repository: CustomerRepository,
        car_brand_repository: CarBrandRepository,
        car_model_repository: CarModelRepository,
        booking_repository: BookingRepository,
    ):
        self.vehicle_repository = vehicle_repository
        self.customer_repository = customer_repository
        self.car_brand_repository = car_brand_repository
        self.car_model_repository = car_model_repository
        self.booking_repository = booking_repository

    async def create_vehicle(
        self,
        vehicle_data: VehicleCreate,
        customer_id: UUID,
    ) -> Vehicle:
        customer = await self.customer_repository.get_by_id(
            customer_id,
        )
        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )

        brand = await self.car_brand_repository.get_by_id(
            vehicle_data.brand_id,
        )
        if brand is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Car brand not found.",
            )

        car_model = await self.car_model_repository.get_by_id(
            vehicle_data.car_model_id,
        )
        if car_model is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Car model not found.",
            )

        if car_model.brand_id != vehicle_data.brand_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected car model does not belong to the selected brand.",
            )

        registration_number = (
            vehicle_data.registration_number.strip().upper()
        )
        vehicle_data.registration_number = registration_number

        existing_vehicle = (
            await self.vehicle_repository.get_by_registration_number(
                registration_number,
            )
        )

        if existing_vehicle is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Registration number already exists.",
            )
        vehicle_payload = vehicle_data.model_dump()
        vehicle_payload["customer_id"] = customer_id
        
        return await self.vehicle_repository.create(vehicle_payload)

    async def get_vehicles(
        self,
    ) -> list[Vehicle]:
        return await self.vehicle_repository.get_all()

    async def get_vehicle(
        self,
        vehicle_id: UUID,
        customer_id: UUID,
    ) -> Vehicle:
        vehicle = await self.vehicle_repository.get_by_id(
            vehicle_id,
        )

        if vehicle is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found.",
            )

        if vehicle.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this vehicle.",
            )
        return vehicle

    async def get_customer_vehicles(
        self,
        customer_id: UUID,
    ) -> list[Vehicle]:
        customer = await self.customer_repository.get_by_id(
            customer_id,
        )

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )

        return await self.vehicle_repository.get_by_customer(
            customer_id,
        )

    async def update_vehicle(
        self,
        vehicle_id: UUID,
        vehicle_data: VehicleUpdate,
        customer_id: UUID,
    ) -> Vehicle:
        vehicle = await self.vehicle_repository.get_by_id(
            vehicle_id,
        )

        if vehicle is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found.",
            )

        if vehicle.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this vehicle.",
            )
        
        if vehicle_data.brand_id is not None:
            brand = await self.car_brand_repository.get_by_id(
                vehicle_data.brand_id,
            )

            if brand is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Car brand not found.",
                )

        if vehicle_data.car_model_id is not None:
            car_model = await self.car_model_repository.get_by_id(
                vehicle_data.car_model_id,
            )

            if car_model is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Car model not found.",
                )

            brand_id = (
                vehicle_data.brand_id
                if vehicle_data.brand_id is not None
                else vehicle.brand_id
            )

            if car_model.brand_id != brand_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Selected car model does not belong to the selected brand.",
                )

        if vehicle_data.registration_number is not None:
            registration_number = (
                vehicle_data.registration_number.strip().upper()
            )

            existing_vehicle = (
                await self.vehicle_repository.get_by_registration_number(
                    registration_number,
                )
            )

            if (
                existing_vehicle is not None
                and existing_vehicle.id != vehicle.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Registration number already exists.",
                )

            vehicle_data.registration_number = registration_number

        return await self.vehicle_repository.update(
            vehicle,
            vehicle_data,
        )

    async def delete_vehicle(
        self,
        vehicle_id: UUID,
        customer_id: UUID,
    ) -> None:
        vehicle = await self.vehicle_repository.get_by_id(
            vehicle_id,
        )

        if vehicle is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found.",
            )

        if vehicle.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this vehicle.",
            )

        bookings = await self.booking_repository.get_by_vehicle(
            vehicle.id,
        )

        if bookings:
            raise HTTPException(
                status_code=409,
                detail="Vehicle cannot be deleted because it has existing bookings.",
            )
        
        await self.vehicle_repository.delete(vehicle)