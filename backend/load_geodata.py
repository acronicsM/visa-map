import os
import geopandas as gpd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Database connection
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "visamap")

conn_str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(conn_str)

# Находим путь к данным относительно скрипта
script_dir = Path(__file__).parent.absolute()
shp_path = script_dir / "data" / "ne_110m_admin_0_countries" / "ne_110m_admin_0_countries.shp"
shp_path = str(shp_path)

print(f"Looking for shapefile at: {shp_path}")
print(f"File exists: {os.path.exists(shp_path)}")

if not os.path.exists(shp_path):
    print("ERROR: Shapefile not found!")
    print(f"Current directory: {os.getcwd()}")
    print("Contents of current directory:")
    for item in os.listdir(script_dir):
        print(f"  - {item}")
    print("\nContents of data folder (if exists):")
    data_dir = script_dir / "data"
    if data_dir.exists():
        for item in os.listdir(data_dir):
            print(f"  - {item}")
    exit(1)

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
gdf = gdf[gdf['iso_code'] != '-99']

print(f"Loaded {len(gdf)} countries")

# Set SRID to 4326
gdf = gdf.set_crs(epsg=4326)

gdf['visa_type'] = 'unknown'

# Write to database
print("Writing to database...")
gdf.to_postgis(
    name='countries',
    con=engine,
    if_exists='replace',
    index=False,
    dtype={'geometry': 'geometry(MULTIPOLYGON, 4326)'}
)

print("Done! Countries loaded successfully.")

# Verify
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM countries"))
    count = result.scalar()
    print(f"Total countries in database: {count}")