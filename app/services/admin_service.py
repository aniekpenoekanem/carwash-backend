from app.repositories.admin_repository import AdminRepository
from app.schemas.admin import DashboardResponse

class AdminService:
    def __init__(
        self,
        repository: AdminRepository,
    ):
        self.repository = repository
        
    async def dashboard(self) -> DashboardResponse:
        return DashboardResponse(
            total_customers=await self.repository.total_customers(),
            total_vehicles=await self.repository.total_vehicles(),
            total_bookings=await self.repository.total_bookings(),

            pending_bookings=await self.repository.pending_bookings(),
            confirmed_bookings=await self.repository.confirmed_bookings(),
            completed_bookings=await self.repository.completed_bookings(),
            cancelled_bookings=await self.repository.cancelled_bookings(),

            today_bookings=await self.repository.today_bookings(),

            today_revenue=float(
                await self.repository.today_revenue()
            ),
            monthly_revenue=float(
                await self.repository.monthly_revenue()
            ),
        )