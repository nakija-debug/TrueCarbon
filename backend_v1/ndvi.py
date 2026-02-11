# ndvi.py
# This file talks to Google Earth Engine and calculates NDVI
# DEPRECATED: Use backend/app/services/ndvi_service.py instead

import ee
import datetime


def calculate_ndvi_time_series(farm_geojson, start_date, end_date):
    """
    INPUT:
    - farm_geojson: GeoJSON polygon from frontend
    - start_date: 'YYYY-MM-DD'
    - end_date: 'YYYY-MM-DD'

    OUTPUT:
    - List of {date, ndvi}
    
    NOTE: Earth Engine initialization must be performed via the unified
    backend's EarthEngineManager singleton (backend/app/services/earth_engine.py)
    to ensure thread-safe, production-grade initialization with proper error
    handling and retry logic.
    """

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