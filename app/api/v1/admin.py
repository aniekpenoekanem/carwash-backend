from fastapi import APIRouter, Depends

from app.dependencies.admin import get_admin_service
from app.dependencies.auth import require_admin
from app.models.user import User
from app.schemas.admin import DashboardResponse
from app.services.admin_service import AdminService

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.get(
    "/dashboard",
    response_model=DashboardResponse,
)
async def dashboard(
    admin: User = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
):
    return await service.dashboard()