from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from geoalchemy2.functions import ST_AsGeoJSON
from sqlalchemy.ext.asyncio import AsyncSession
import json

from .database import Base, engine, get_db
from .models import Country
from .schemas import CountryDetail

app = FastAPI(title="Visa Map API", description="API for the Visa Map project")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Visa Map API is running"}


@app.get("/countries", response_model=list[CountryDetail])
async def list_countries(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Country))
    countries = result.scalars().all()
    return [CountryDetail.model_validate(c) for c in countries]

@app.get("/countries.geojson")
async def get_countries_geojson(db: AsyncSession = Depends(get_db)):
    # Using raw SQL for GeoJSON aggregation
    query = text("""
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', json_agg(
                json_build_object(
                    'type', 'Feature',
                    'geometry', ST_AsGeoJSON(geometry)::json,
                    'properties', json_build_object(
                        'name', name,
                        'iso_code', iso_code,
                        'visa_type', COALESCE(visa_type, 'unknown')
                    )
                )
            )
        ) as geojson
        FROM countries
        WHERE geometry IS NOT NULL
    """)
    
    result = await db.execute(query)
    geojson = result.scalar()
    return geojson
