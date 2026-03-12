import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "visamap")

conn_str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(conn_str)

# Path to shapefile
shp_path = r"D:\Projects\visa-map\backend\data\ne_110m_admin_0_countries\ne_110m_admin_0_countries.shp"

print("Reading shapefile...")
gdf = gpd.read_file(shp_path)

# Select and rename columns
gdf = gdf[['ADMIN', 'ISO_A3', 'geometry']].copy()
gdf = gdf.rename(columns={
    'ADMIN': 'name',
    'ISO_A3': 'iso_code'
})

# Remove rows without ISO code
gdf = gdf.dropna(subset=['iso_code'])
gdf = gdf[gdf['iso_code'] != '-99']  # Remove invalid codes

print(f"Loaded {len(gdf)} countries")

# Set SRID to 4326 (WGS84)
gdf = gdf.set_crs(epsg=4326)

# Write to database
print("Writing to database...")
gdf.to_postgis(
    name='countries',
    con=engine,
    if_exists='replace',  # Replace entire table
    index=False,
    dtype={'geometry': 'geometry(MULTIPOLYGON, 4326)'}
)

print("Done! Countries loaded successfully.")

# Verify
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM countries"))
    count = result.scalar()
    print(f"Total countries in database: {count}")