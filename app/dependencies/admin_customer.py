from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.repositories.admin_customer_repository import (
    AdminCustomerRepository,
)
from app.services.admin_customer_service import (
    AdminCustomerService,
)


def get_admin_customer_service(
    session: AsyncSession = Depends(get_session),
) -> AdminCustomerService:
    return AdminCustomerService(
        AdminCustomerRepository(session),
    )