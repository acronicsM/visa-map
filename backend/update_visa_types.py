import asyncio
from sqlalchemy import update
from app.database import AsyncSessionLocal
from app.models import Country

async def update_visa_types():
    visa_data = {
        "RUS": "visa_free",
        "USA": "embassy",
        "TUR": "evisa",
        "EGY": "visa_on_arrival",
        "PRK": "restricted",
        "CAN": "embassy",
        "GBR": "embassy",
        "DEU": "visa_free",
        "FRA": "visa_free",
        "JPN": "visa_free",
    }
    
    async with AsyncSessionLocal() as session:
        for iso_code, visa_type in visa_data.items():
            stmt = update(Country).where(Country.iso_code == iso_code).values(visa_type=visa_type)
            await session.execute(stmt)
            print(f"Updated {iso_code} -> {visa_type}")
        
        await session.commit()
        print("All updates committed!")

if __name__ == "__main__":
    asyncio.run(update_visa_types())