from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_customers: int
    total_vehicles: int
    total_bookings: int

    pending_bookings: int
    confirmed_bookings: int
    completed_bookings: int
    cancelled_bookings: int

    today_bookings: int

    today_revenue: float
    monthly_revenue: float