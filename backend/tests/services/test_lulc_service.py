"""Tests for LULC service."""

import pytest
from unittest.mock import patch, MagicMock

from app.services.lulc_service import LULCService, LULC_CLASS_NAMES
from app.services.exceptions import InvalidGeometryError, InvalidDateRangeError


class TestLULCService:
    """Test LULC service classification."""

    @pytest.fixture
    def service(self):
        """Create LULC service instance."""
        with patch("app.services.lulc_service.EarthEngineManager"):
            return LULCService()

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
                        [0.1, 0.0],
                        [0.1, 0.1],
                        [0.0, 0.1],
                        [0.0, 0.0],
                    ]
                ],
            },
        }

    def test_validate_geojson_valid(self, service, valid_geojson):
        """Test validation passes for valid GeoJSON."""
        service._validate_geojson(valid_geojson)

    def test_validate_geojson_invalid(self, service):
        """Test validation fails for invalid GeoJSON."""
        with pytest.raises(InvalidGeometryError):
            service._validate_geojson({"type": "Feature"})

    def test_validate_date_range_valid(self, service):
        """Test validation passes for valid date range."""
        service._validate_date_range("2023-01-01", "2023-12-31")

    def test_validate_date_range_invalid(self, service):
        """Test validation fails for invalid date range."""
        with pytest.raises(InvalidDateRangeError):
            service._validate_date_range("2023-12-31", "2023-01-01")

    def test_lulc_class_names_complete(self):
        """Test that all LULC class names are defined."""
        assert len(LULC_CLASS_NAMES) == 9
        assert LULC_CLASS_NAMES[0] == "Water"
        assert LULC_CLASS_NAMES[1] == "Trees"
        assert LULC_CLASS_NAMES[4] == "Crops"

    def test_format_lulc_response(self, service):
        """Test LULC response formatting."""
        class_areas = {1: 100.0, 4: 200.0, 6: 50.0}

        response = service._format_lulc_response(
            class_areas, "2023-01-01", "2023-12-31"
        )

        assert response["total_area_ha"] == 350.0
        assert response["dominant_class"] == "Crops"
        assert len(response["classes"]) == 3
        assert response["analysis_period"]["start"] == "2023-01-01"
        assert response["classes"][1]["name"] == "Crops"
        assert response["classes"][1]["area_ha"] == 200.0
        assert abs(response["classes"][1]["percentage"] - 57.14) < 0.1

    def test_format_lulc_response_empty(self, service):
        """Test LULC response formatting with no classes."""
        class_areas = {}

        response = service._format_lulc_response(
            class_areas, "2023-01-01", "2023-12-31"
        )

        assert response["total_area_ha"] == 0.0
        assert response["dominant_class"] is None
        assert len(response["classes"]) == 0

    @pytest.mark.asyncio
    async def test_classify_land_use_calls_sync(self, service, valid_geojson):
        """Test that async method calls sync computation."""
        with patch.object(service, "_compute_lulc_sync") as mock_sync:
            mock_sync.return_value = {
                "total_area_ha": 0,
                "classes": [],
                "dominant_class": None,
                "analysis_period": {"start": "2023-01-01", "end": "2023-12-31"},
            }

            result = await service.classify_land_use(
                valid_geojson, "2023-01-01", "2023-12-31"
            )

            assert result["total_area_ha"] == 0
            mock_sync.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
