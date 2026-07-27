from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.models.customer import Customer
from app.models.vehicle import Vehicle

from decimal import Decimal

from app.core.enums import BookingStatus, PaymentStatus

class AdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def total_customers(self) -> int:
        result = await self.db.execute(
            select(func.count(Customer.id))
        )
        return result.scalar_one()


    async def total_vehicles(self) -> int:
        result = await self.db.execute(
            select(func.count(Vehicle.id))
        )
        return result.scalar_one()


    async def total_bookings(self) -> int:
        result = await self.db.execute(
            select(func.count(Booking.id))
        )
        return result.scalar_one()    

    async def today_bookings(self) -> int:
        result = await self.db.execute(
            select(func.count(Booking.id)).where(
                Booking.scheduled_date == date.today(),
            )
        )
        return result.scalar_one()


    async def pending_bookings(self) -> int:
        result = await self.db.execute(
            select(func.count(Booking.id)).where(
                Booking.status == BookingStatus.PENDING,
            )
        )
        return result.scalar_one()


    async def confirmed_bookings(self) -> int:
        result = await self.db.execute(
            select(func.count(Booking.id)).where(
                Booking.status == BookingStatus.CONFIRMED,
            )
        )
        return result.scalar_one()


    async def completed_bookings(self) -> int:
        result = await self.db.execute(
            select(func.count(Booking.id)).where(
                Booking.status == BookingStatus.COMPLETED,
            )
        )
        return result.scalar_one()


    async def cancelled_bookings(self) -> int:
        result = await self.db.execute(
            select(func.count(Booking.id)).where(
                Booking.status == BookingStatus.CANCELLED,
            )
        )
        return result.scalar_one()

    async def today_revenue(self) -> Decimal:
        result = await self.db.execute(
            select(
                func.coalesce(
                    func.sum(Booking.price_at_booking),
                    0,
                )
            ).where(
                Booking.scheduled_date == date.today(),
                Booking.payment_status == PaymentStatus.PAID,
            )
        )
        return result.scalar_one()


    async def monthly_revenue(self) -> Decimal:
        today = date.today()

        result = await self.db.execute(
            select(
                func.coalesce(
                    func.sum(Booking.price_at_booking),
                    0,
                )
            ).where(
                func.extract("year", Booking.scheduled_date)
                == today.year,
                func.extract("month", Booking.scheduled_date)
                == today.month,
                Booking.payment_status == PaymentStatus.PAID,
            )
        )
        return result.scalar_one()