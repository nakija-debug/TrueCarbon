"""NDVI (Normalized Difference Vegetation Index) service for carbon measurement."""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional

import ee

from app.core.config import settings
from app.services.earth_engine import EarthEngineManager
from app.services.exceptions import (
    InvalidGeometryError,
    InvalidDateRangeError,
    EarthEngineError,
    EarthEngineQuotaError,
)

logger = logging.getLogger(__name__)


class NDVIService:
    """
    Service for calculating NDVI (Normalized Difference Vegetation Index).

    Uses Sentinel-2 surface reflectance data to compute NDVI time series
    over a farm geometry. Provides async wrappers to prevent blocking
    the FastAPI event loop.
    """

    def __init__(self):
        """Initialize NDVI service with Earth Engine manager."""
        self.ee_manager = EarthEngineManager.get_instance()

    async def calculate_ndvi_time_series(
        self,
        farm_geojson: dict,
        start_date: str,
        end_date: str,
    ) -> List[dict]:
        """
        Calculate NDVI time series for a farm over a date range.

        Args:
            farm_geojson: GeoJSON geometry of farm boundary
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            List of dicts with keys: date (YYYY-MM-DD), ndvi (float), std (float)

        Raises:
            InvalidGeometryError: If GeoJSON is invalid
            InvalidDateRangeError: If dates are invalid
            EarthEngineQuotaError: If GEE quota is exceeded
            EarthEngineError: For other GEE failures
        """
        # Validate inputs
        self._validate_geojson(farm_geojson)
        self._validate_date_range(start_date, end_date)

        # Initialize Earth Engine
        self.ee_manager.initialize()

        # Run synchronous GEE computation in thread pool
        try:
            result = await asyncio.to_thread(
                self._compute_ndvi_sync,
                farm_geojson,
                start_date,
                end_date,
            )
            return result
        except Exception as e:
            logger.error(f"NDVI calculation failed: {e}")
            raise

    def _compute_ndvi_sync(
        self,
        farm_geojson: dict,
        start_date: str,
        end_date: str,
    ) -> List[dict]:
        """
        Synchronous NDVI computation (wrapped by async caller).

        Filters Sentinel-2 SR collection by bounds, date, and cloud cover.
        Calculates NDVI using B8 (NIR) and B4 (Red) bands.
        """
        try:
            # Convert GeoJSON to EE Geometry
            geometry = self._geojson_to_ee_geometry(farm_geojson)

            # Load Sentinel-2 SR collection
            collection = (
                ee.ImageCollection("COPERNICUS/S2_SR")
                .filterBounds(geometry)
                .filterDate(start_date, end_date)
                .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
            )

            # Check if collection is empty
            size = collection.size().getInfo()
            if size == 0:
                logger.warning(
                    f"No Sentinel-2 images found for date range {start_date} to {end_date}"
                )
                return []

            logger.info(f"Found {size} Sentinel-2 images for NDVI calculation")

            # Calculate NDVI for each image
            ndvi_collection = collection.map(
                lambda img: img.normalizedDifference(["B8", "B4"])
                .rename("NDVI")
                .set("system:time_start", img.get("system:time_start"))
            )

            # Reduce to mean NDVI per date
            ndvi_stats = ndvi_collection.map(
                lambda img: (
                    ee.Feature(
                        None,
                        {
                            "date": ee.Date(img.get("system:time_start")).format(
                                "YYYY-MM-dd"
                            ),
                            "ndvi": img.reduceRegion(
                                reducer=ee.Reducer.mean(),
                                geometry=geometry,
                                scale=10,
                                maxPixels=1e9,
                            ).get("NDVI"),
                            "std": img.reduceRegion(
                                reducer=ee.Reducer.stdDev(),
                                geometry=geometry,
                                scale=10,
                                maxPixels=1e9,
                            ).get("NDVI"),
                        },
                    )
                )
            )

            # Extract data
            data = ndvi_stats.getInfo()
            features = data.get("features", [])

            # Format results, filtering out null values
            results = []
            for feature in features:
                props = feature.get("properties", {})
                ndvi_value = props.get("ndvi")

                if ndvi_value is not None:
                    results.append(
                        {
                            "date": props.get("date"),
                            "ndvi": float(ndvi_value),
                            "std": float(props.get("std", 0)),
                        }
                    )

            logger.info(f"Successfully calculated NDVI for {len(results)} dates")
            return sorted(results, key=lambda x: x["date"])

        except ee.EEException as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "limit" in error_msg:
                raise EarthEngineQuotaError(str(e)) from e
            raise EarthEngineError(str(e)) from e

    def _validate_geojson(self, geojson: dict) -> None:
        """
        Validate GeoJSON structure.

        Raises:
            InvalidGeometryError: If GeoJSON is invalid
        """
        try:
            if "geometry" not in geojson:
                raise InvalidGeometryError("GeoJSON must contain 'geometry' field")

            geometry = geojson["geometry"]
            if "type" not in geometry or "coordinates" not in geometry:
                raise InvalidGeometryError(
                    "GeoJSON geometry must contain 'type' and 'coordinates'"
                )

            if geometry["type"] not in [
                "Point",
                "Polygon",
                "MultiPolygon",
                "LineString",
            ]:
                raise InvalidGeometryError(
                    f"Unsupported geometry type: {geometry['type']}"
                )

            if not geometry["coordinates"]:
                raise InvalidGeometryError("GeoJSON coordinates are empty")

        except (KeyError, TypeError) as e:
            raise InvalidGeometryError(f"Invalid GeoJSON structure: {str(e)}") from e

    def _validate_date_range(self, start_date: str, end_date: str) -> None:
        """
        Validate date format and range.

        Raises:
            InvalidDateRangeError: If dates are invalid
        """
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")

            if start >= end:
                raise InvalidDateRangeError(
                    f"Start date must be before end date: {start_date} >= {end_date}"
                )

            # Check if range is not too large (max 5 years)
            days_diff = (end - start).days
            if days_diff > 365 * 5:
                raise InvalidDateRangeError(
                    f"Date range too large: {days_diff} days (max 5 years)"
                )

        except ValueError as e:
            raise InvalidDateRangeError(
                f"Invalid date format. Use YYYY-MM-DD: {str(e)}"
            ) from e

    @staticmethod
    def _geojson_to_ee_geometry(geojson: dict) -> ee.Geometry:
        """Convert GeoJSON to Earth Engine Geometry."""
        geometry = geojson["geometry"]

        if geometry["type"] == "Polygon":
            return ee.Geometry.Polygon(geometry["coordinates"])
        elif geometry["type"] == "MultiPolygon":
            # Use bounding box of all polygons
            polys = [ee.Geometry.Polygon(coords) for coords in geometry["coordinates"]]
            return ee.Geometry.MultiPolygon([poly.coordinates().getInfo() for poly in polys])
        elif geometry["type"] == "Point":
            coords = geometry["coordinates"]
            return ee.Geometry.Point(coords)
        else:
            raise InvalidGeometryError(f"Unsupported geometry type: {geometry['type']}")
