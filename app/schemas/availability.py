from datetime import date

from pydantic import BaseModel


class AvailabilityResponse(BaseModel):
    date: date
    available_slots: list[str]