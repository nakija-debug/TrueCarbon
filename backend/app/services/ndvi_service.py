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

    async def calculate_temperature_time_series(
        self,
        farm_geojson: dict,
        start_date: str,
        end_date: str,
    ) -> List[dict]:
        """
        Calculate air temperature time series for a farm using ERA5-Land data.

        Args:
            farm_geojson: GeoJSON geometry of farm boundary
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            List of dicts with keys: date (YYYY-MM-DD), temperature_celsius (float),
            std (float), min_temp (float), max_temp (float)

        Raises:
            InvalidGeometryError: If GeoJSON is invalid
            InvalidDateRangeError: If dates are invalid
            EarthEngineQuotaError: If GEE quota is exceeded
            EarthEngineError: For other GEE failures
        """
        self._validate_geojson(farm_geojson)
        self._validate_date_range(start_date, end_date)

        self.ee_manager.initialize()

        try:
            result = await asyncio.to_thread(
                self._compute_temperature_sync,
                farm_geojson,
                start_date,
                end_date,
            )
            return result
        except Exception as e:
            logger.error(f"Temperature calculation failed: {e}")
            raise

    def _compute_temperature_sync(
        self,
        farm_geojson: dict,
        start_date: str,
        end_date: str,
    ) -> List[dict]:
        """Synchronous temperature computation using ERA5-Land dataset."""
        try:
            geometry = self._geojson_to_ee_geometry(farm_geojson)

            # Load ERA5-Land hourly data
            collection = (
                ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY")
                .filterBounds(geometry)
                .filterDate(start_date, end_date)
                .select("temperature_2m")
            )

            size = collection.size().getInfo()
            if size == 0:
                logger.warning(
                    f"No ERA5-Land temperature data found for {start_date} to {end_date}"
                )
                return []

            logger.info(f"Found {size} ERA5-Land images for temperature calculation")

            # Convert temperature from Kelvin to Celsius and calculate daily stats
            def process_image(img):
                # Convert Kelvin to Celsius and rename band
                temp_celsius = img.expression("b('temperature_2m') - 273.15").rename("temperature_celsius")
                
                return ee.Feature(
                    None,
                    {
                        "date": ee.Date(img.get("system:time_start")).format("YYYY-MM-dd"),
                        "temperature_celsius": temp_celsius.reduceRegion(
                            reducer=ee.Reducer.mean(),
                            geometry=geometry,
                            scale=9000,
                            maxPixels=1e9,
                        ).get("temperature_celsius"),
                        "std": temp_celsius.reduceRegion(
                            reducer=ee.Reducer.stdDev(),
                            geometry=geometry,
                            scale=9000,
                            maxPixels=1e9,
                        ).get("temperature_celsius"),
                        "min_temp": temp_celsius.reduceRegion(
                            reducer=ee.Reducer.min(),
                            geometry=geometry,
                            scale=9000,
                            maxPixels=1e9,
                        ).get("temperature_celsius"),
                        "max_temp": temp_celsius.reduceRegion(
                            reducer=ee.Reducer.max(),
                            geometry=geometry,
                            scale=9000,
                            maxPixels=1e9,
                        ).get("temperature_celsius"),
                    },
                )

            temp_stats = collection.map(process_image)
            data = temp_stats.getInfo()
            features = data.get("features", [])

            # Aggregate to daily means
            daily_temps = {}
            for feature in features:
                props = feature.get("properties", {})
                date = props.get("date")
                temp = props.get("temperature_celsius")

                if date and temp is not None:
                    if date not in daily_temps:
                        daily_temps[date] = []
                    daily_temps[date].append(
                        {
                            "temp": float(temp),
                            "std": float(props.get("std", 0)),
                            "min": float(props.get("min_temp", 0)),
                            "max": float(props.get("max_temp", 0)),
                        }
                    )

            # Calculate daily statistics
            results = []
            for date in sorted(daily_temps.keys()):
                temps = daily_temps[date]
                if temps:
                    avg_temp = sum(t["temp"] for t in temps) / len(temps)
                    avg_std = sum(t["std"] for t in temps) / len(temps)
                    min_temp = min(t["min"] for t in temps)
                    max_temp = max(t["max"] for t in temps)

                    self._validate_environmental_data(avg_temp)

                    results.append(
                        {
                            "date": date,
                            "temperature_celsius": round(avg_temp, 2),
                            "std": round(avg_std, 2),
                            "min_temp": round(min_temp, 2),
                            "max_temp": round(max_temp, 2),
                        }
                    )

            logger.info(f"Successfully calculated temperature for {len(results)} dates")
            return results

        except ee.EEException as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "limit" in error_msg:
                raise EarthEngineQuotaError(str(e)) from e
            raise EarthEngineError(str(e)) from e

    async def calculate_humidity_time_series(
        self,
        farm_geojson: dict,
        start_date: str,
        end_date: str,
    ) -> List[dict]:
        """
        Calculate relative humidity time series using ERA5-Land data.

        Args:
            farm_geojson: GeoJSON geometry of farm boundary
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            List of dicts with keys: date (YYYY-MM-DD), humidity_percent (float), std (float)

        Raises:
            InvalidGeometryError: If GeoJSON is invalid
            InvalidDateRangeError: If dates are invalid
            EarthEngineQuotaError: If GEE quota is exceeded
            EarthEngineError: For other GEE failures
        """
        self._validate_geojson(farm_geojson)
        self._validate_date_range(start_date, end_date)

        self.ee_manager.initialize()

        try:
            result = await asyncio.to_thread(
                self._compute_humidity_sync,
                farm_geojson,
                start_date,
                end_date,
            )
            return result
        except Exception as e:
            logger.error(f"Humidity calculation failed: {e}")
            raise

    def _compute_humidity_sync(
        self,
        farm_geojson: dict,
        start_date: str,
        end_date: str,
    ) -> List[dict]:
        """Synchronous humidity computation using ERA5-Land dataset."""
        try:
            geometry = self._geojson_to_ee_geometry(farm_geojson)

            # Load ERA5-Land data with temperature and dewpoint
            collection = (
                ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY")
                .filterBounds(geometry)
                .filterDate(start_date, end_date)
                .select(["temperature_2m", "dewpoint_temperature_2m"])
            )

            size = collection.size().getInfo()
            if size == 0:
                logger.warning(
                    f"No ERA5-Land humidity data found for {start_date} to {end_date}"
                )
                return []

            logger.info(f"Found {size} ERA5-Land images for humidity calculation")

            def process_image(img):
                # Calculate RH using Magnus formula
                rh = self._calculate_relative_humidity(img)
                
                return ee.Feature(
                    None,
                    {
                        "date": ee.Date(img.get("system:time_start")).format("YYYY-MM-dd"),
                        "humidity_percent": rh.reduceRegion(
                            reducer=ee.Reducer.mean(),
                            geometry=geometry,
                            scale=9000,
                            maxPixels=1e9,
                        ).get("RH"),
                        "std": rh.reduceRegion(
                            reducer=ee.Reducer.stdDev(),
                            geometry=geometry,
                            scale=9000,
                            maxPixels=1e9,
                        ).get("RH"),
                    },
                )

            humidity_stats = collection.map(process_image)
            data = humidity_stats.getInfo()
            features = data.get("features", [])

            # Aggregate to daily means
            daily_humidity = {}
            for feature in features:
                props = feature.get("properties", {})
                date = props.get("date")
                humidity = props.get("humidity_percent")

                if date and humidity is not None:
                    if date not in daily_humidity:
                        daily_humidity[date] = []
                    daily_humidity[date].append(
                        {
                            "humidity": float(humidity),
                            "std": float(props.get("std", 0)),
                        }
                    )

            # Calculate daily statistics
            results = []
            for date in sorted(daily_humidity.keys()):
                humidities = daily_humidity[date]
                if humidities:
                    avg_humidity = sum(h["humidity"] for h in humidities) / len(humidities)
                    avg_std = sum(h["std"] for h in humidities) / len(humidities)

                    # Validate humidity in range [0, 100]
                    if 0 <= avg_humidity <= 100:
                        results.append(
                            {
                                "date": date,
                                "humidity_percent": round(avg_humidity, 2),
                                "std": round(avg_std, 2),
                            }
                        )

            logger.info(f"Successfully calculated humidity for {len(results)} dates")
            return results

        except ee.EEException as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "limit" in error_msg:
                raise EarthEngineQuotaError(str(e)) from e
            raise EarthEngineError(str(e)) from e

    async def calculate_land_surface_temperature(
        self,
        farm_geojson: dict,
        start_date: str,
        end_date: str,
    ) -> List[dict]:
        """
        Calculate land surface temperature using MODIS data.

        Args:
            farm_geojson: GeoJSON geometry of farm boundary
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            List of dicts with keys: date (YYYY-MM-DD), lst_day_celsius (float),
            lst_night_celsius (float), std (float)

        Raises:
            InvalidGeometryError: If GeoJSON is invalid
            InvalidDateRangeError: If dates are invalid
            EarthEngineQuotaError: If GEE quota is exceeded
            EarthEngineError: For other GEE failures
        """
        self._validate_geojson(farm_geojson)
        self._validate_date_range(start_date, end_date)

        self.ee_manager.initialize()

        try:
            result = await asyncio.to_thread(
                self._compute_lst_sync,
                farm_geojson,
                start_date,
                end_date,
            )
            return result
        except Exception as e:
            logger.error(f"LST calculation failed: {e}")
            raise

    def _compute_lst_sync(
        self,
        farm_geojson: dict,
        start_date: str,
        end_date: str,
    ) -> List[dict]:
        """Synchronous LST computation using MODIS dataset."""
        try:
            geometry = self._geojson_to_ee_geometry(farm_geojson)

            # Load MODIS LST data
            collection = (
                ee.ImageCollection("MODIS/061/MOD11A1")
                .filterBounds(geometry)
                .filterDate(start_date, end_date)
                .select(["LST_Day_1km", "LST_Night_1km", "QC_Day", "QC_Night"])
            )

            size = collection.size().getInfo()
            if size == 0:
                logger.warning(
                    f"No MODIS LST data found for {start_date} to {end_date}"
                )
                return []

            logger.info(f"Found {size} MODIS images for LST calculation")

            def process_image(img):
                # Filter by quality flags (keep only good quality pixels)
                day_filtered = self._filter_by_quality_flags(img, "QC_Day", "LST_Day_1km")
                night_filtered = self._filter_by_quality_flags(img, "QC_Night", "LST_Night_1km")

                # Convert from Kelvin to Celsius (scale: 0.02)
                lst_day_celsius = day_filtered.expression("b('LST_Day_1km') * 0.02 - 273.15")
                lst_night_celsius = night_filtered.expression("b('LST_Night_1km') * 0.02 - 273.15")

                return ee.Feature(
                    None,
                    {
                        "date": ee.Date(img.get("system:time_start")).format("YYYY-MM-dd"),
                        "lst_day_celsius": lst_day_celsius.reduceRegion(
                            reducer=ee.Reducer.mean(),
                            geometry=geometry,
                            scale=1000,
                            maxPixels=1e9,
                        ).get("LST_Day_1km"),
                        "lst_night_celsius": lst_night_celsius.reduceRegion(
                            reducer=ee.Reducer.mean(),
                            geometry=geometry,
                            scale=1000,
                            maxPixels=1e9,
                        ).get("LST_Night_1km"),
                        "std": img.select(["LST_Day_1km"]).reduceRegion(
                            reducer=ee.Reducer.stdDev(),
                            geometry=geometry,
                            scale=1000,
                            maxPixels=1e9,
                        ).get("LST_Day_1km"),
                    },
                )

            lst_stats = collection.map(process_image)
            data = lst_stats.getInfo()
            features = data.get("features", [])

            # Format results
            results = []
            for feature in features:
                props = feature.get("properties", {})
                lst_day = props.get("lst_day_celsius")
                lst_night = props.get("lst_night_celsius")
                date = props.get("date")

                if date and lst_day is not None and lst_night is not None:
                    results.append(
                        {
                            "date": date,
                            "lst_day_celsius": round(float(lst_day), 2),
                            "lst_night_celsius": round(float(lst_night), 2),
                            "std": round(float(props.get("std", 0)), 2),
                        }
                    )

            logger.info(f"Successfully calculated LST for {len(results)} dates")
            return results

        except ee.EEException as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "limit" in error_msg:
                raise EarthEngineQuotaError(str(e)) from e
            raise EarthEngineError(str(e)) from e

    def _validate_environmental_data(self, value: float) -> None:
        """
        Validate temperature/humidity ranges.

        Raises:
            ValueError: If value is outside reasonable ranges
        """
        if not isinstance(value, (int, float)):
            raise ValueError(f"Environmental value must be numeric, got {type(value)}")

    def _calculate_relative_humidity(self, img: ee.Image) -> ee.Image:
        """
        Calculate relative humidity using Magnus formula.

        Formula (in Celsius):
        - es = 6.112 * exp((17.67 * T) / (T + 243.5))
        - e = 6.112 * exp((17.67 * Td) / (Td + 243.5))
        - RH = (e / es) * 100

        Args:
            img: Earth Engine image with temperature_2m and dewpoint_temperature_2m bands (in Kelvin)

        Returns:
            Image with RH band calculated
        """
        # Convert Kelvin to Celsius and rename bands
        T_celsius = img.select("temperature_2m").expression("b('temperature_2m') - 273.15").rename("T_celsius")
        Td_celsius = img.select("dewpoint_temperature_2m").expression("b('dewpoint_temperature_2m') - 273.15").rename("Td_celsius")

        # Calculate saturation vapor pressure (es) using Celsius temperature
        es = T_celsius.expression("6.112 * exp((17.67 * b('T_celsius')) / (b('T_celsius') + 243.5))")

        # Calculate actual vapor pressure (e) using Celsius dewpoint
        e = Td_celsius.expression("6.112 * exp((17.67 * b('Td_celsius')) / (b('Td_celsius') + 243.5))")

        # Calculate relative humidity
        rh = e.divide(es).multiply(100).rename("RH")

        return rh

    def _filter_by_quality_flags(
        self, img: ee.Image, qc_band: str, data_band: str
    ) -> ee.Image:
        """
        Filter image by quality control flags.

        Keeps only pixels with good quality flags (typically 0 or 1).

        Args:
            img: Earth Engine image
            qc_band: Name of quality control band
            data_band: Name of data band to filter

        Returns:
            Filtered image with only good quality pixels
        """
        qc = img.select(qc_band)
        # Keep pixels where QC is 0 or 1 (good/acceptable quality)
        mask = qc.lte(1)
        return img.select(data_band).updateMask(mask)
