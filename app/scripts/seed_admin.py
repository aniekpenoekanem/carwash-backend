from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.user import User
from app.core.enums import UserRole


ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Admin@123"
ADMIN_PHONE = "08000000000"


async def seed_admin():
    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(User.email == ADMIN_EMAIL)
        )

        admin = result.scalar_one_or_none()

        if admin:
            print("✅ Admin user already exists.")
            return

        admin = User(
            first_name="System",
            last_name="Administrator",
            email=ADMIN_EMAIL,
            phone_number=ADMIN_PHONE,
            password_hash=hash_password(ADMIN_PASSWORD),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
        )

        session.add(admin)
        await session.commit()

        print("✅ Admin user created successfully!")
        print(f"Email: {ADMIN_EMAIL}")
        print(f"Password: {ADMIN_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(seed_admin())