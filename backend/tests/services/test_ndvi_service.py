"""Tests for NDVI service."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from app.services.ndvi_service import NDVIService
from app.services.exceptions import (
    InvalidGeometryError,
    InvalidDateRangeError,
)


class TestNDVIService:
    """Test NDVI service calculations."""

    @pytest.fixture
    def service(self):
        """Create NDVI service instance."""
        with patch("app.services.ndvi_service.EarthEngineManager"):
            return NDVIService()

    @pytest.fixture
    def valid_geojson(self):
        """Valid farm GeoJSON."""
        return {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [0.0, 0.0],
                        [1.0, 0.0],
                        [1.0, 1.0],
                        [0.0, 1.0],
                        [0.0, 0.0],
                    ]
                ],
            },
        }

    def test_validate_geojson_valid(self, service, valid_geojson):
        """Test validation passes for valid GeoJSON."""
        # Should not raise
        service._validate_geojson(valid_geojson)

    def test_validate_geojson_missing_geometry(self, service):
        """Test validation fails for missing geometry."""
        geojson = {"type": "Feature"}

        with pytest.raises(InvalidGeometryError):
            service._validate_geojson(geojson)

    def test_validate_geojson_empty_coordinates(self, service):
        """Test validation fails for empty coordinates."""
        geojson = {
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": []},
        }

        with pytest.raises(InvalidGeometryError):
            service._validate_geojson(geojson)

    def test_validate_geojson_invalid_type(self, service):
        """Test validation fails for invalid geometry type."""
        geojson = {
            "type": "Feature",
            "geometry": {
                "type": "InvalidType",
                "coordinates": [[0, 0]],
            },
        }

        with pytest.raises(InvalidGeometryError):
            service._validate_geojson(geojson)

    def test_validate_date_range_valid(self, service):
        """Test validation passes for valid date range."""
        # Should not raise
        service._validate_date_range("2023-01-01", "2023-12-31")

    def test_validate_date_range_invalid_format(self, service):
        """Test validation fails for invalid date format."""
        with pytest.raises(InvalidDateRangeError):
            service._validate_date_range("2023-1-1", "2023-12-31")

    def test_validate_date_range_start_after_end(self, service):
        """Test validation fails when start after end."""
        with pytest.raises(InvalidDateRangeError):
            service._validate_date_range("2023-12-31", "2023-01-01")

    def test_validate_date_range_start_equals_end(self, service):
        """Test validation fails when start equals end."""
        with pytest.raises(InvalidDateRangeError):
            service._validate_date_range("2023-01-01", "2023-01-01")

    def test_validate_date_range_too_large(self, service):
        """Test validation fails for date range > 5 years."""
        with pytest.raises(InvalidDateRangeError):
            service._validate_date_range("2015-01-01", "2025-01-01")

    @pytest.mark.asyncio
    async def test_calculate_ndvi_time_series_calls_sync(self, service, valid_geojson):
        """Test that async method calls sync computation in thread."""
        with patch.object(service, "_compute_ndvi_sync") as mock_sync:
            mock_sync.return_value = []

            result = await service.calculate_ndvi_time_series(
                valid_geojson, "2023-01-01", "2023-12-31"
            )

            assert result == []
            mock_sync.assert_called_once()

    def test_geojson_to_ee_geometry_polygon(self, service):
        """Test GeoJSON to EE geometry conversion for Polygon."""
        with patch("app.services.ndvi_service.ee"):
            geojson = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
                },
            }

            with patch("app.services.ndvi_service.ee.Geometry.Polygon") as mock_poly:
                service._geojson_to_ee_geometry(geojson)
                mock_poly.assert_called_once()

    def test_geojson_to_ee_geometry_point(self, service):
        """Test GeoJSON to EE geometry conversion for Point."""
        with patch("app.services.ndvi_service.ee"):
            geojson = {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [0.5, 0.5]},
            }

            with patch("app.services.ndvi_service.ee.Geometry.Point") as mock_point:
                service._geojson_to_ee_geometry(geojson)
                mock_point.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
