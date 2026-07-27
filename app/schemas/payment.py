from datetime import datetime

from pydantic import BaseModel

from app.core.enums import PaymentStatus


class PaymentUpdate(BaseModel):
    status: PaymentStatus | None = None
    gateway_response: str | None = None
    authorization_url: str | None = None
    access_code: str | None = None
    paid_at: datetime | None = None