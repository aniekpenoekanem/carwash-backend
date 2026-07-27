from datetime import datetime
from uuid import UUID
from app.core.enums import BodyType

from pydantic import BaseModel, ConfigDict


class CarModelCreate(BaseModel):
    brand_id: UUID
    name: str
    body_type: BodyType


class CarModelUpdate(BaseModel):
    brand_id: UUID | None = None
    name: str | None = None
    body_type: BodyType | None = None
    

class CarModelResponse(BaseModel):
    id: UUID
    brand_id: UUID
    name: str
    body_type: BodyType
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)