"""LULC (Land Use/Land Cover) service using Dynamic World classification."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

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

# Dynamic World class mapping (ID to name)
LULC_CLASS_NAMES = {
    0: "Water",
    1: "Trees",
    2: "Grass",
    3: "Flooded Vegetation",
    4: "Crops",
    5: "Shrub/Scrub",
    6: "Built Area",
    7: "Bare Ground",
    8: "Snow/Ice",
}


class LULCService:
    """
    Service for land use/land cover classification using Dynamic World.

    Provides async methods to classify land cover types over a farm area
    and calculate areas per class. Uses Google's Dynamic World dataset
    for near real-time classification.
    """

    def __init__(self):
        """Initialize LULC service with Earth Engine manager."""
        self.ee_manager = EarthEngineManager.get_instance()

    async def classify_land_use(
        self,
        farm_geojson: dict,
        start_date: str,
        end_date: str,
    ) -> Dict:
        """
        Classify land use/cover for a farm over a date range.

        Args:
            farm_geojson: GeoJSON geometry of farm boundary
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            Dictionary with keys:
            - total_area_ha: Total farm area in hectares
            - classes: List of dicts with name, area_ha, percentage
            - dominant_class: Most common class name
            - analysis_period: {start, end}

        Raises:
            InvalidGeometryError: If GeoJSON is invalid
            InvalidDateRangeError: If dates are invalid
            EarthEngineQuotaError: If GEE quota is exceeded
            EarthEngineError: For other GEE failures
        """
        # Validate inputs
        self._validate_geojson(farm_geojson)
        self._validate_date_range(start_date, end_date)
        self._validate_geometry_size(farm_geojson)

        # Initialize Earth Engine
        self.ee_manager.initialize()

        # Run synchronous GEE computation in thread pool
        try:
            result = await asyncio.to_thread(
                self._compute_lulc_sync,
                farm_geojson,
                start_date,
                end_date,
            )
            return result
        except Exception as e:
            logger.error(f"LULC classification failed: {e}")
            raise

    def _compute_lulc_sync(
        self,
        farm_geojson: dict,
        start_date: str,
        end_date: str,
    ) -> Dict:
        """
        Synchronous LULC computation (wrapped by async caller).

        Loads Dynamic World collection, filters by bounds and date,
        calculates area per class.
        """
        try:
            # Convert GeoJSON to EE Geometry
            geometry = self._geojson_to_ee_geometry(farm_geojson)

            # Load Dynamic World collection
            dw_collection = (
                ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
                .filterBounds(geometry)
                .filterDate(start_date, end_date)
                .select("label")
            )

            # Check if collection is empty
            size = dw_collection.size().getInfo()
            if size == 0:
                logger.warning(
                    f"No Dynamic World data found for date range {start_date} to {end_date}"
                )
                return {
                    "total_area_ha": 0.0,
                    "classes": [],
                    "dominant_class": None,
                    "analysis_period": {"start": start_date, "end": end_date},
                }

            logger.info(f"Found {size} Dynamic World images for LULC classification")

            # Calculate mode (most common class) across time period
            mode_image = dw_collection.mode()

            # Calculate areas per class
            class_stats = self._calculate_class_areas(mode_image, geometry)

            # Format response
            response = self._format_lulc_response(class_stats, start_date, end_date)

            logger.info(
                f"Successfully classified {len(response['classes'])} LULC classes"
            )
            return response

        except ee.EEException as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "limit" in error_msg:
                raise EarthEngineQuotaError(str(e)) from e
            raise EarthEngineError(str(e)) from e

    def _calculate_class_areas(
        self, image: ee.Image, geometry: ee.Geometry
    ) -> Dict[int, float]:
        """
        Calculate area per LULC class.

        Returns dict mapping class ID to area in hectares.
        """
        # Create pixel area image (in square meters)
        pixel_area = ee.Image.pixelArea()

        # Calculate area per class
        class_areas = {}

        for class_id in range(9):  # 0-8 are the valid Dynamic World classes
            # Create mask for this class
            mask = image.eq(class_id)

            # Calculate total area
            area_sqm = (
                pixel_area.updateMask(mask)
                .reduceRegion(
                    reducer=ee.Reducer.sum(),
                    geometry=geometry,
                    scale=10,
                    maxPixels=1e9,
                )
                .getInfo()
            )

            # Convert to hectares (1 ha = 10,000 m²)
            area_value = area_sqm.get("area", 0)
            area_ha = area_value / 10000.0 if area_value else 0

            if area_ha > 0:
                class_areas[class_id] = area_ha

        return class_areas

    def _format_lulc_response(
        self,
        class_areas: Dict[int, float],
        start_date: str,
        end_date: str,
    ) -> Dict:
        """Format raw class areas into API response."""
        total_area_ha = sum(class_areas.values())

        # Build class list with percentages
        classes = []
        dominant_class = None
        max_area = 0

        for class_id, area_ha in sorted(class_areas.items()):
            percentage = (area_ha / total_area_ha * 100) if total_area_ha > 0 else 0

            class_name = LULC_CLASS_NAMES.get(class_id, f"Unknown ({class_id})")

            classes.append(
                {
                    "id": class_id,
                    "name": class_name,
                    "area_ha": round(area_ha, 2),
                    "percentage": round(percentage, 2),
                }
            )

            # Track dominant class
            if area_ha > max_area:
                max_area = area_ha
                dominant_class = class_name

        return {
            "total_area_ha": round(total_area_ha, 2),
            "classes": classes,
            "dominant_class": dominant_class,
            "analysis_period": {"start": start_date, "end": end_date},
        }

    def _validate_geojson(self, geojson: dict) -> None:
        """Validate GeoJSON structure."""
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
        """Validate date format and range."""
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

    def _validate_geometry_size(self, geojson: dict) -> None:
        """
        Validate that farm geometry is not too large.

        Prevents quota issues from processing huge areas.
        Max 10,000 hectares (~100 km²).

        Raises:
            InvalidGeometryError: If farm is too large
        """
        try:
            geometry = self._geojson_to_ee_geometry(geojson)
            area_sqm = geometry.area(maxError=30).getInfo()
            area_ha = area_sqm / 10000.0

            if area_ha > 10000:
                raise InvalidGeometryError(
                    f"Farm geometry too large: {area_ha:.0f} ha (max 10,000 ha)"
                )

        except InvalidGeometryError:
            raise
        except Exception as e:
            logger.warning(f"Could not validate geometry size: {e}")

    @staticmethod
    def _geojson_to_ee_geometry(geojson: dict) -> ee.Geometry:
        """Convert GeoJSON to Earth Engine Geometry."""
        geometry = geojson["geometry"]

        if geometry["type"] == "Polygon":
            return ee.Geometry.Polygon(geometry["coordinates"])
        elif geometry["type"] == "MultiPolygon":
            polys = [ee.Geometry.Polygon(coords) for coords in geometry["coordinates"]]
            return ee.Geometry.MultiPolygon(
                [poly.coordinates().getInfo() for poly in polys]
            )
        elif geometry["type"] == "Point":
            coords = geometry["coordinates"]
            return ee.Geometry.Point(coords)
        else:
            raise InvalidGeometryError(f"Unsupported geometry type: {geometry['type']}")
