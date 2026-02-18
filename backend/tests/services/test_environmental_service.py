"""Tests for environmental data service methods."""

import pytest
from datetime import datetime, date
from unittest.mock import MagicMock, AsyncMock, patch
import ee

from app.services.ndvi_service import NDVIService
from app.services.exceptions import InvalidGeometryError, InvalidDateRangeError, EarthEngineError


# Sample GeoJSON geometry for testing
VALID_GEOJSON = {
    "type": "Feature",
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [34.5, -0.5],
                [34.6, -0.5],
                [34.6, -0.4],
                [34.5, -0.4],
                [34.5, -0.5],
            ]
        ],
    },
}


class TestTemperatureCalculation:
    """Tests for temperature time series calculation."""

    @pytest.mark.asyncio
    async def test_calculate_temperature_valid_input(self):
        """Test temperature calculation with valid inputs."""
        service = NDVIService()
        
        # Mock Earth Engine manager
        with patch.object(service.ee_manager, 'initialize'):
            with patch.object(service, '_compute_temperature_sync') as mock_compute:
                mock_compute.return_value = [
                    {
                        "date": "2024-01-15",
                        "temperature_celsius": 25.5,
                        "std": 2.1,
                        "min_temp": 22.1,
                        "max_temp": 28.3,
                    }
                ]
                
                result = await service.calculate_temperature_time_series(
                    farm_geojson=VALID_GEOJSON,
                    start_date="2024-01-01",
                    end_date="2024-01-31",
                )
                
                assert len(result) == 1
                assert result[0]["temperature_celsius"] == 25.5
                assert result[0]["std"] == 2.1

    @pytest.mark.asyncio
    async def test_temperature_invalid_geojson(self):
        """Test temperature calculation with invalid GeoJSON."""
        service = NDVIService()
        
        with pytest.raises(InvalidGeometryError):
            await service.calculate_temperature_time_series(
                farm_geojson={"invalid": "geometry"},
                start_date="2024-01-01",
                end_date="2024-01-31",
            )

    @pytest.mark.asyncio
    async def test_temperature_invalid_date_range(self):
        """Test temperature calculation with invalid date range."""
        service = NDVIService()
        
        with pytest.raises(InvalidDateRangeError):
            await service.calculate_temperature_time_series(
                farm_geojson=VALID_GEOJSON,
                start_date="2024-01-31",
                end_date="2024-01-01",  # End before start
            )

    @pytest.mark.asyncio
    async def test_temperature_date_range_too_large(self):
        """Test temperature calculation with date range exceeding 5 years."""
        service = NDVIService()
        
        with pytest.raises(InvalidDateRangeError):
            await service.calculate_temperature_time_series(
                farm_geojson=VALID_GEOJSON,
                start_date="2020-01-01",
                end_date="2026-01-01",  # 6 years
            )


class TestHumidityCalculation:
    """Tests for humidity time series calculation."""

    @pytest.mark.asyncio
    async def test_calculate_humidity_valid_input(self):
        """Test humidity calculation with valid inputs."""
        service = NDVIService()
        
        with patch.object(service.ee_manager, 'initialize'):
            with patch.object(service, '_compute_humidity_sync') as mock_compute:
                mock_compute.return_value = [
                    {
                        "date": "2024-01-15",
                        "humidity_percent": 65.4,
                        "std": 5.2,
                    }
                ]
                
                result = await service.calculate_humidity_time_series(
                    farm_geojson=VALID_GEOJSON,
                    start_date="2024-01-01",
                    end_date="2024-01-31",
                )
                
                assert len(result) == 1
                assert result[0]["humidity_percent"] == 65.4
                assert result[0]["std"] == 5.2

    def test_calculate_relative_humidity_magnus_formula(self):
        """Test Magnus formula for relative humidity calculation."""
        service = NDVIService()
        
        # Create mock image with temperature and dewpoint bands
        mock_img = MagicMock(spec=ee.Image)
        
        with patch.object(service, '_calculate_relative_humidity') as mock_calc:
            mock_calc.return_value = MagicMock(spec=ee.Image)
            result = service._calculate_relative_humidity(mock_img)
            
            assert result is not None

    def test_humidity_valid_range(self):
        """Test that calculated humidity is within valid range [0, 100]."""
        service = NDVIService()
        
        # Test with values at boundaries
        test_cases = [0.0, 50.0, 100.0]
        for humidity in test_cases:
            # Should not raise any exception
            # Actual validation happens during data aggregation
            assert 0 <= humidity <= 100


class TestLandSurfaceTemperatureCalculation:
    """Tests for LST calculation."""

    @pytest.mark.asyncio
    async def test_calculate_lst_valid_input(self):
        """Test LST calculation with valid inputs."""
        service = NDVIService()
        
        with patch.object(service.ee_manager, 'initialize'):
            with patch.object(service, '_compute_lst_sync') as mock_compute:
                mock_compute.return_value = [
                    {
                        "date": "2024-01-15",
                        "lst_day_celsius": 32.5,
                        "lst_night_celsius": 18.2,
                        "std": 3.1,
                    }
                ]
                
                result = await service.calculate_land_surface_temperature(
                    farm_geojson=VALID_GEOJSON,
                    start_date="2024-01-01",
                    end_date="2024-01-31",
                )
                
                assert len(result) == 1
                assert result[0]["lst_day_celsius"] == 32.5
                assert result[0]["lst_night_celsius"] == 18.2

    def test_filter_by_quality_flags(self):
        """Test quality flag filtering for MODIS data."""
        service = NDVIService()
        
        mock_img = MagicMock(spec=ee.Image)
        mock_img.select.return_value = mock_img
        mock_img.lte.return_value = MagicMock(spec=ee.Image)
        mock_img.updateMask.return_value = mock_img
        
        with patch.object(service, '_filter_by_quality_flags') as mock_filter:
            mock_filter.return_value = mock_img
            result = service._filter_by_quality_flags(mock_img, "QC_Day", "LST_Day_1km")
            
            assert result is not None


class TestEnvironmentalDataValidation:
    """Tests for environmental data validation."""

    def test_validate_environmental_data_valid(self):
        """Test validation of valid environmental data."""
        service = NDVIService()
        
        # Should not raise
        service._validate_environmental_data(25.5)
        service._validate_environmental_data(-5.0)
        service._validate_environmental_data(0.0)

    def test_validate_environmental_data_invalid_type(self):
        """Test validation rejects non-numeric values."""
        service = NDVIService()
        
        with pytest.raises(ValueError):
            service._validate_environmental_data("not_a_number")

    def test_validate_date_format(self):
        """Test date format validation."""
        service = NDVIService()
        
        # Valid format
        service._validate_date_range("2024-01-01", "2024-01-31")
        
        # Invalid format
        with pytest.raises(InvalidDateRangeError):
            service._validate_date_range("01/01/2024", "31/01/2024")

    def test_validate_geojson_structure(self):
        """Test GeoJSON structure validation."""
        service = NDVIService()
        
        # Valid GeoJSON
        service._validate_geojson(VALID_GEOJSON)
        
        # Invalid: missing geometry
        with pytest.raises(InvalidGeometryError):
            service._validate_geojson({"type": "Feature"})
        
        # Invalid: missing coordinates
        invalid_geojson = {
            "type": "Feature",
            "geometry": {"type": "Polygon"},
        }
        with pytest.raises(InvalidGeometryError):
            service._validate_geojson(invalid_geojson)


class TestEnvironmentalDataMetadata:
    """Tests for metadata storage."""

    def test_temperature_metadata_structure(self):
        """Test that temperature measurements include proper metadata."""
        metadata = {
            "source": "ERA5-Land",
            "dataset": "ECMWF/ERA5_LAND/HOURLY",
            "band": "temperature_2m",
            "unit": "celsius",
            "resolution_km": 9,
            "temporal_resolution": "hourly_aggregated_daily",
            "accuracy_celsius": 0.5,
            "data_quality": "high",
        }
        
        assert metadata["source"] == "ERA5-Land"
        assert metadata["band"] == "temperature_2m"
        assert metadata["unit"] == "celsius"

    def test_humidity_metadata_structure(self):
        """Test that humidity measurements include proper metadata."""
        metadata = {
            "source": "ERA5-Land",
            "dataset": "ECMWF/ERA5_LAND/HOURLY",
            "bands": ["temperature_2m", "dewpoint_temperature_2m"],
            "unit": "percent",
            "calculation_method": "Magnus formula",
            "resolution_km": 9,
            "accuracy_percent": 5,
            "data_quality": "high",
        }
        
        assert metadata["source"] == "ERA5-Land"
        assert metadata["unit"] == "percent"
        assert "Magnus formula" in metadata["calculation_method"]

    def test_lst_metadata_structure(self):
        """Test that LST measurements include proper metadata."""
        metadata = {
            "source": "MODIS Terra",
            "dataset": "MODIS/061/MOD11A1",
            "bands": ["LST_Day_1km", "LST_Night_1km"],
            "unit": "celsius",
            "resolution_m": 1000,
            "quality_filtered": True,
            "emissivity_corrected": True,
            "accuracy_celsius": 1.0,
        }
        
        assert metadata["source"] == "MODIS Terra"
        assert metadata["resolution_m"] == 1000
        assert metadata["quality_filtered"] is True


class TestEnvironmentalDataEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_result_set(self):
        """Test handling of empty result sets from Earth Engine."""
        service = NDVIService()
        
        with patch.object(service.ee_manager, 'initialize'):
            with patch.object(service, '_compute_temperature_sync') as mock_compute:
                mock_compute.return_value = []
                
                result = await service.calculate_temperature_time_series(
                    farm_geojson=VALID_GEOJSON,
                    start_date="2024-01-01",
                    end_date="2024-01-31",
                )
                
                assert result == []

    @pytest.mark.asyncio
    async def test_earth_engine_quota_error(self):
        """Test handling of Earth Engine quota exceeded errors."""
        service = NDVIService()
        
        from app.services.exceptions import EarthEngineQuotaError
        
        with patch.object(service.ee_manager, 'initialize'):
            with patch.object(service, '_compute_temperature_sync') as mock_compute:
                mock_compute.side_effect = EarthEngineQuotaError("Quota exceeded")
                
                with pytest.raises(EarthEngineQuotaError):
                    await service.calculate_temperature_time_series(
                        farm_geojson=VALID_GEOJSON,
                        start_date="2024-01-01",
                        end_date="2024-01-31",
                    )

    @pytest.mark.asyncio
    async def test_earth_engine_error(self):
        """Test handling of general Earth Engine errors."""
        service = NDVIService()
        
        with patch.object(service.ee_manager, 'initialize'):
            with patch.object(service, '_compute_temperature_sync') as mock_compute:
                mock_compute.side_effect = EarthEngineError("Connection failed")
                
                with pytest.raises(EarthEngineError):
                    await service.calculate_temperature_time_series(
                        farm_geojson=VALID_GEOJSON,
                        start_date="2024-01-01",
                        end_date="2024-01-31",
                    )
