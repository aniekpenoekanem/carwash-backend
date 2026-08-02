from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from fastapi import HTTPException, status
from app.core.enums import UserRole
from app.core.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.customer import Customer
from app.models.user import User
from app.repositories.customer_repository import CustomerRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    UpdateProfileRequest,
    ChangePasswordRequest,
)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.customer_repo = CustomerRepository(db)

    async def register(
        self,
        payload: RegisterRequest,
    ) -> TokenResponse:

        existing_email = await self.user_repo.get_by_email(
            payload.email
        )

        if existing_email:
            raise UserAlreadyExistsError(
                "Email already registered."
            )

        existing_phone = await self.user_repo.get_by_phone_number(
            payload.phone_number
        )

        if existing_phone:
            raise UserAlreadyExistsError(
                "Phone number already registered."
            )

        user = User(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            phone_number=payload.phone_number,
            password_hash=hash_password(payload.password),
            role=UserRole.CUSTOMER,
        )

        await self.user_repo.create(user)

        customer = Customer(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone_number,
        )

        await self.customer_repo.create(customer)

        await self.db.commit()

        token = create_access_token(
            subject=str(user.id),
        )

        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user),
        )

    async def login(
        self,
        payload: LoginRequest,
    ) -> TokenResponse:

        user = await self.user_repo.get_by_email(
            payload.email,
        )

        print("\n========== LOGIN DEBUG ==========")
        print(f"Email entered : {payload.email}")
        print(f"User found: {user is not None}")
        
        if user:
            print(f"Database email: {user.email}")
            print(
                "Password verified:",
                verify_password(
                    payload.password,
                    user.password_hash,
                ),
            )
        print("=================================\n")
        
        if not user:
            raise InvalidCredentialsError(
                "Invalid email or password."
            )

        if not verify_password(
            payload.password,
            user.password_hash,
        ):
            raise InvalidCredentialsError(
                "Invalid email or password."
            )

        if not user.is_active:
            raise InactiveUserError(
                "User account is inactive."
            )

        token = create_access_token(
            subject=str(user.id),
        )

        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user),
        )
        
    async def update_profile(
        self,
        customer_id,
        payload: UpdateProfileRequest,
    ) -> UserResponse:

        customer = await self.customer_repo.get_by_id(
            customer_id,
        )

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )

        user = await self.user_repo.get_by_id(
            customer.user_id,
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        customer.first_name = payload.first_name
        customer.last_name = payload.last_name
        customer.phone = payload.phone_number

        user.first_name = payload.first_name
        user.last_name = payload.last_name
        user.phone_number = payload.phone_number

        await self.customer_repo.update(customer)
        await self.user_repo.update(user)
        
        await self.db.commit()

        return UserResponse.model_validate(user)
    
    async def change_password(
        self,
        user_id: UUID,
        payload: ChangePasswordRequest,
    ) -> None:
        user = await self.user_repo.get_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        if not verify_password(
            payload.current_password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )

        user.password_hash = hash_password(payload.new_password)

        await self.user_repo.update(user)
        
        await self.db.commit()