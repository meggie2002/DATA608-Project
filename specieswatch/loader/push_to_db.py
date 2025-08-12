import os
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# --- Build DB connection string from secrets ---
db_url = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
print("DB URL:", db_url)  # Optional: for debugging
engine = create_engine(db_url)

# --- Push Parquet Data ---
def push_parquet():
    try:
        df = pd.read_parquet("species_dataMap_clean.parquet")
        df.to_sql("species_data", engine, if_exists="replace", index=False)
        print(" Parquet data pushed to 'species_data'")
    except Exception as e:
        print(" Error pushing parquet data:", e)

# --- Push GeoJSON Data ---
def push_geojson():
    try:
        gdf = gpd.read_file("final_species.geojson")
        gdf = gdf.dropna(subset=["sci_name", "habitat", "category", "geometry"])
        gdf["sci_name"] = gdf["sci_name"].str.strip()
        gdf["habitat"] = gdf["habitat"].str.strip()
        gdf.to_postgis("species_geo", engine, if_exists="replace", index=False)
        print(" GeoJSON data pushed to 'species_geo'")
    except Exception as e:
        print(" Error pushing GeoJSON data:", e)

# --- Run Both ---
if __name__ == "__main__":
    print("Connecting to database...")
    try:
        with engine.connect() as conn:
            print(" Connected to database")
            push_parquet()
            push_geojson()
    except SQLAlchemyError as err:
        print("Database connection failed:", err)
