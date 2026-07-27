from fastapi import HTTPException, status

from datetime import date, datetime, time, timedelta

from app.repositories.availability_repository import (
    AvailabilityRepository,
)
from app.schemas.availability import (
    AvailabilityResponse,
)


class AvailabilityService:
    def __init__(
        self,
        repository: AvailabilityRepository,
    ):
        self.repository = repository
    
    WORKING_DAYS = {
        0,  # Monday
        1,  # Tuesday
        2,  # Wednesday
        3,  # Thursday
        4,  # Friday
        5,  # Saturday
    }

    BUSINESS_START = time(8, 0)
    BUSINESS_END = time(17, 0)
    SLOT_DURATION = timedelta(hours=1)

    async def get_availability(
        self,
        scheduled_date: date,
    ) -> AvailabilityResponse:

        today = date.today()
        
        # Reject past dates
        if scheduled_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot check availability for a past date.",
            )
        
        # Reject non-working days
        if scheduled_date.weekday() not in self.WORKING_DAYS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bookings are not available on this day.",
            )
        
        booked_slots = await self.repository.get_booked_slots(
            scheduled_date,
        )

        booked_set = {
            slot.strftime("%H:%M")
            for slot in booked_slots
        }

        available_slots: list[str] = []

        current = datetime.combine(
            scheduled_date,
            self.BUSINESS_START,
        )

        end = datetime.combine(
            scheduled_date,
            self.BUSINESS_END,
        )

        now = datetime.now()

        while current < end:

            slot = current.strftime("%H:%M")

            if slot not in booked_set:

                if (
                    scheduled_date != now.date()
                    or current > now
                ):
                    available_slots.append(slot)

            current += self.SLOT_DURATION

        return AvailabilityResponse(
            date=scheduled_date,
            available_slots=available_slots,
        )