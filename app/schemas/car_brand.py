from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CarBrandCreate(BaseModel):
    name: str


class CarBrandUpdate(BaseModel):
    name: str | None = None


class CarBrandResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)