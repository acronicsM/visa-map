import asyncio
import sys
from pathlib import Path

# Support running as script: python add_test_data.py (from any dir)
backend = Path(__file__).resolve().parent.parent
if str(backend) not in sys.path:
    sys.path.insert(0, str(backend))

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import Country


TEST_COUNTRIES = [
    {"name": "France", "iso_code": "FRA", "visa_type": "visa-free"},
    {"name": "Japan", "iso_code": "JPN", "visa_type": "visa-free"},
    {"name": "India", "iso_code": "IND", "visa_type": "e-visa"},
    {"name": "Turkey", "iso_code": "TUR", "visa_type": "visa-on-arrival"},
    {"name": "Russia", "iso_code": "RUS", "visa_type": "visa-required"},
]


async def add_test_countries() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Country))
        existing = {c.iso_code for c in result.scalars().all()}

        for data in TEST_COUNTRIES:
            if data["iso_code"] in existing:
                print(f"  Skipping {data['name']} ({data['iso_code']}) - already exists")
                continue
            country = Country(**data)
            session.add(country)
            print(f"  Added {data['name']} ({data['iso_code']}) - {data['visa_type']}")

        await session.commit()
        print("Done.")


if __name__ == "__main__":
    print("Adding test countries...")
    asyncio.run(add_test_countries())
