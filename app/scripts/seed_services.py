from __future__ import annotations

import asyncio
from decimal import Decimal

from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.service import Service


SERVICES = [
    {
        "name": "Exterior Wash",
        "description": "Exterior hand wash and rinse",
        "price": Decimal("2000.00"),
    },
    {
        "name": "Interior Wash",
        "description": "Interior vacuum and cleaning",
        "price": Decimal("3000.00"),
    },
    {
        "name": "Complete Wash",
        "description": "Complete interior and exterior wash",
        "price": Decimal("5000.00"),
    },
]


async def seed_services():
    async with SessionLocal() as session:

        for service_data in SERVICES:

            result = await session.execute(
                select(Service).where(
                    Service.name == service_data["name"]
                )
            )

            existing = result.scalar_one_or_none()

            if existing:
                print(f"Service already exists: {existing.name}")
                continue

            session.add(
                Service(
                    name=service_data["name"],
                    description=service_data["description"],
                    price=service_data["price"],
                    is_active=True,
                )
            )

            print(f"Created service: {service_data['name']}")

        await session.commit()

        print("\n✅ Services seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_services())