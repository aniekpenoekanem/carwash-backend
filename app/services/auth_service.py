from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

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
        )

    async def login(
        self,
        payload: LoginRequest,
    ) -> TokenResponse:

        user = await self.user_repo.get_by_email(
            payload.email,
        )

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
        )