from pydantic import BaseModel

from app.schemas.service import ServiceRead


class ServiceListResponse(BaseModel):
    items: list[ServiceRead]

    total: int
    page: int
    size: int