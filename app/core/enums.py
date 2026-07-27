from enum import Enum


class BodyType(str, Enum):
    SEDAN = "Sedan"
    SUV = "SUV"
    HATCHBACK = "Hatchback"
    PICKUP = "Pickup"
    COUPE = "Coupe"
    VAN = "Van"


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    
class UserRole(str, Enum):
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"    