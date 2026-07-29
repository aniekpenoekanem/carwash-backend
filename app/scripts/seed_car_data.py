from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.core.enums import BodyType
from app.db.database import SessionLocal
from app.models.car_brand import CarBrand
from app.models.car_model import CarModel


CAR_DATA = {
    "Toyota": [
        ("Corolla", BodyType.SEDAN),
        ("Camry", BodyType.SEDAN),
        ("Highlander", BodyType.SUV),
        ("RAV4", BodyType.SUV),
    ],
    "Honda": [
        ("Accord", BodyType.SEDAN),
        ("Civic", BodyType.SEDAN),
        ("CR-V", BodyType.SUV),
    ],
    "Lexus": [
        ("RX 350", BodyType.SUV),
        ("ES 350", BodyType.SEDAN),
    ],
    "Mercedes": [
        ("C300", BodyType.SEDAN),
        ("E350", BodyType.SEDAN),
    ],
}


async def seed_car_data():
    async with SessionLocal() as session:
        for brand_name, models in CAR_DATA.items():

            result = await session.execute(
                select(CarBrand).where(CarBrand.name == brand_name)
            )

            brand = result.scalar_one_or_none()

            if brand is None:
                brand = CarBrand(name=brand_name)
                session.add(brand)
                await session.flush()

                print(f"Created brand: {brand_name}")

            for model_name, body_type in models:

                result = await session.execute(
                    select(CarModel).where(
                        CarModel.brand_id == brand.id,
                        CarModel.name == model_name,
                    )
                )

                existing = result.scalar_one_or_none()

                if existing:
                    continue

                session.add(
                    CarModel(
                        brand_id=brand.id,
                        name=model_name,
                        body_type=body_type,
                    )
                )

                print(f"  Added model: {model_name}")

        await session.commit()

        print("\n✅ Car brands and models seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_car_data())