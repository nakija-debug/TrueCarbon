# ndvi.py
# This file talks to Google Earth Engine and calculates NDVI

import ee
import datetime


def init_earth_engine():
    """
    Safely initialize Google Earth Engine.
    Runs ONLY when needed (on first API call).
    
    Features:
    - Avoids crash on import
    - Works in reload mode
    - Production-safe
    - Handles auth errors gracefully
    """
    try:
        # Try normal initialization
        ee.Initialize(project="student-research-carbon")
    except Exception:
        # If not authenticated, force auth
        ee.Authenticate()
        ee.Initialize(project="student-research-carbon")


def calculate_ndvi_time_series(farm_geojson, start_date, end_date):
    """
    INPUT:
    - farm_geojson: GeoJSON polygon from frontend
    - start_date: 'YYYY-MM-DD'
    - end_date: 'YYYY-MM-DD'

    OUTPUT:
    - List of {date, ndvi}
    """
    
    # 🔑 Initialize EE only when NDVI is requested
    init_earth_engine()

    # Convert GeoJSON to Earth Engine Geometry
    farm_geometry = ee.Geometry.Polygon(farm_geojson["coordinates"])

    # Load Sentinel-2 Surface Reflectance dataset
    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR")
        .filterBounds(farm_geometry)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
    )

    # Function to calculate NDVI for each image
    def add_ndvi(image):
        ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
        return image.addBands(ndvi)

    # Apply NDVI function
    ndvi_collection = collection.map(add_ndvi)

    # Reduce each image to mean NDVI over the farm
    def extract_ndvi(image):
        mean_ndvi = image.select("NDVI").reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=farm_geometry,
            scale=10,
            maxPixels=1e9
        )

        return ee.Feature(
            None,
            {
                "date": image.date().format("YYYY-MM-dd"),
                "ndvi": mean_ndvi.get("NDVI")
            }
        )

    # Convert ImageCollection → FeatureCollection
    ndvi_features = ndvi_collection.map(extract_ndvi)

    # Get results to Python
    result = ndvi_features.getInfo()

    # Clean output
    ndvi_list = []
    for f in result["features"]:
        if f["properties"]["ndvi"] is not None:
            ndvi_list.append({
                "date": f["properties"]["date"],
                "ndvi": round(f["properties"]["ndvi"], 3)
            })

    return ndvi_list