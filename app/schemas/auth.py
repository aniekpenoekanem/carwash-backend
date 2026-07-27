from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.core.enums import UserRole


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    role: UserRole
    is_active: bool
    is_verified: bool