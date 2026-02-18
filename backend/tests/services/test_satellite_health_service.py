"""Comprehensive tests for SatelliteHealthService.

Tests cover:
- Health check status calculation (operational/degraded/offline)
- Earth Engine API integration with mocked responses
- Error handling and exception propagation
- Database record creation and updates
- Parallel execution of satellite checks
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from app.services.satellite_health_service import SatelliteHealthService
from app.services.exceptions import (
    SatelliteHealthCheckError,
    EarthEngineQuotaError,
)
from app.models.satellite_status import SatelliteStatus


# Mock ee module for tests
class MockEEException(Exception):
    """Mock Earth Engine exception."""
    pass


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def mock_ee_manager_setup():
    """Setup mock Earth Engine manager and ee module for all tests."""
    with patch("app.services.satellite_health_service.EarthEngineManager") as mock_manager, \
         patch("app.services.satellite_health_service.ee") as mock_ee:
        manager_instance = MagicMock()
        manager_instance.initialize = Mock()
        mock_manager.get_instance.return_value = manager_instance
        
        # Setup ee mock for exception handling
        mock_ee.EEException = MockEEException
        mock_ee.ImageCollection = MagicMock()
        
        yield manager_instance, mock_ee


@pytest.fixture
def satellite_service_and_mocks(mock_ee_manager_setup):
    """Create a SatelliteHealthService instance with mocks in place."""
    manager_instance, mock_ee = mock_ee_manager_setup
    service = SatelliteHealthService()
    # Override the ee_manager with our mocked one
    service.ee_manager = manager_instance
    return service, manager_instance, mock_ee


@pytest.fixture
def satellite_service(satellite_service_and_mocks):
    """Create a SatelliteHealthService instance."""
    service, _, _ = satellite_service_and_mocks
    return service


@pytest.fixture
def mock_ee_manager(satellite_service_and_mocks):
    """Get the mocked ee module."""
    _, _, mock_ee = satellite_service_and_mocks
    return mock_ee


@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock()


@pytest.fixture
def sample_satellite_health_data():
    """Sample satellite health data."""
    return {
        "coverage_percent": 95.5,
        "accuracy_percent": 92.3,
        "status": "operational",
        "data_quality": "high",
        "uptime_percent": 98.7,
        "metadata": {
            "total_images": 150,
            "low_cloud_images": 143,
            "average_cloud_cover": 4.5,
        },
    }


# ============================================================================
# Sentinel-2 Health Check Tests
# ============================================================================


@pytest.mark.asyncio
async def test_sentinel2_health_operational(satellite_service, mock_ee_manager):
    """Test Sentinel-2 health check with operational status."""
    # Mock successful Earth Engine query
    mock_collection = MagicMock()
    mock_filtered = MagicMock()
    mock_low_cloud = MagicMock()

    mock_ee_manager.ImageCollection.return_value = mock_collection
    mock_collection.filterDate.return_value = mock_filtered
    mock_filtered.filter.return_value = mock_low_cloud
    
    # Mock size query
    mock_low_cloud.size.return_value.getInfo.return_value = 143
    mock_filtered.size.return_value.getInfo.return_value = 150

    result = await satellite_service.check_sentinel2_health()

    assert result["status"] == "operational"
    assert result["coverage_percent"] == pytest.approx(95.33, rel=1)
    assert result["data_quality"] == "high"
    assert 0 <= result["coverage_percent"] <= 100


@pytest.mark.asyncio
async def test_sentinel2_health_degraded(satellite_service, mock_ee_manager):
    """Test Sentinel-2 health check with degraded status."""
    mock_collection = MagicMock()
    mock_filtered = MagicMock()
    mock_low_cloud = MagicMock()

    mock_ee_manager.ImageCollection.return_value = mock_collection
    mock_collection.filterDate.return_value = mock_filtered
    mock_filtered.filter.return_value = mock_low_cloud
    
    # Low coverage - degraded status
    mock_low_cloud.size.return_value.getInfo.return_value = 70
    mock_filtered.size.return_value.getInfo.return_value = 150

    result = await satellite_service.check_sentinel2_health()

    assert result["status"] == "degraded"
    assert 50 <= result["coverage_percent"] < 90


@pytest.mark.asyncio
async def test_sentinel2_health_offline(satellite_service, mock_ee_manager):
    """Test Sentinel-2 health check with offline status."""
    mock_collection = MagicMock()
    mock_filtered = MagicMock()

    mock_ee_manager.ImageCollection.return_value = mock_collection
    mock_collection.filterDate.return_value = mock_filtered
    
    # No data - offline status
    mock_filtered.size.return_value.getInfo.return_value = 0

    result = await satellite_service.check_sentinel2_health()

    assert result["status"] == "offline"
    assert result["coverage_percent"] == 0


@pytest.mark.asyncio
async def test_sentinel2_quota_error(satellite_service, mock_ee_manager):
    """Test Sentinel-2 health check with quota error."""
    mock_ee_manager.ImageCollection.side_effect = MockEEException(
        "Quota exceeded"
    )

    with pytest.raises(EarthEngineQuotaError):
        await satellite_service.check_sentinel2_health()


# ============================================================================
# Landsat-8 Health Check Tests
# ============================================================================


@pytest.mark.asyncio
async def test_landsat8_health_operational(satellite_service, mock_ee_manager):
    """Test Landsat-8 health check with operational status."""
    mock_collection = MagicMock()
    mock_filtered = MagicMock()
    mock_good = MagicMock()

    mock_ee_manager.ImageCollection.return_value = mock_collection
    mock_collection.filterDate.return_value = mock_filtered
    mock_filtered.filter.return_value = mock_good
    
    mock_good.size.return_value.getInfo.return_value = 82
    mock_filtered.size.return_value.getInfo.return_value = 89

    result = await satellite_service.check_landsat8_health()

    assert result["status"] == "operational"
    assert 90 <= result["coverage_percent"] <= 100
    assert result["data_quality"] == "high"


@pytest.mark.asyncio
async def test_landsat8_health_degraded(satellite_service, mock_ee_manager):
    """Test Landsat-8 health check with degraded status."""
    mock_collection = MagicMock()
    mock_filtered = MagicMock()
    mock_good = MagicMock()

    mock_ee_manager.ImageCollection.return_value = mock_collection
    mock_collection.filterDate.return_value = mock_filtered
    mock_filtered.filter.return_value = mock_good
    
    mock_good.size.return_value.getInfo.return_value = 60
    mock_filtered.size.return_value.getInfo.return_value = 89

    result = await satellite_service.check_landsat8_health()

    assert result["status"] == "degraded"
    assert 50 <= result["coverage_percent"] < 90


# ============================================================================
# ERA5-Land Health Check Tests
# ============================================================================


@pytest.mark.asyncio
async def test_era5_health_operational(satellite_service, mock_ee_manager):
    """Test ERA5-Land health check with operational status."""
    mock_collection = MagicMock()
    mock_filtered = MagicMock()

    mock_ee_manager.ImageCollection.return_value = mock_collection
    mock_collection.filterDate.return_value = mock_filtered
    
    # 99.7% availability (717 out of 720 hourly records)
    mock_filtered.size.return_value.getInfo.return_value = 717

    result = await satellite_service.check_era5_health()

    assert result["status"] == "operational"
    assert result["accuracy_percent"] == 99.0
    assert result["coverage_percent"] > 95


@pytest.mark.asyncio
async def test_era5_health_degraded(satellite_service, mock_ee_manager):
    """Test ERA5-Land health check with degraded status."""
    mock_collection = MagicMock()
    mock_filtered = MagicMock()

    mock_ee_manager.ImageCollection.return_value = mock_collection
    mock_collection.filterDate.return_value = mock_filtered
    
    # 90% availability (648 out of 720)
    mock_filtered.size.return_value.getInfo.return_value = 648

    result = await satellite_service.check_era5_health()

    assert result["status"] == "degraded"
    assert 80 <= result["coverage_percent"] < 95


# ============================================================================
# Database Update Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_all_satellite_status_success(satellite_service, mock_db):
    """Test updating all satellite status records successfully."""
    with patch.object(
        satellite_service, "check_sentinel2_health", return_value={
            "status": "operational",
            "coverage_percent": 95.5,
            "accuracy_percent": 92.3,
            "data_quality": "high",
            "uptime_percent": 98.7,
            "metadata": {},
        }
    ), patch.object(
        satellite_service, "check_landsat8_health", return_value={
            "status": "operational",
            "coverage_percent": 92.1,
            "accuracy_percent": 88.9,
            "data_quality": "high",
            "uptime_percent": 97.2,
            "metadata": {},
        }
    ), patch.object(
        satellite_service, "check_era5_health", return_value={
            "status": "operational",
            "coverage_percent": 99.7,
            "accuracy_percent": 99.0,
            "data_quality": "high",
            "uptime_percent": 99.5,
            "metadata": {},
        }
    ):
        # Setup mock database
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        mock_db.add = AsyncMock()
        mock_db.commit = AsyncMock()

        await satellite_service.update_all_satellite_status(mock_db)

        # Verify database operations
        assert mock_db.commit.awaited
        # Should have 3 database adds for the 3 satellites
        assert mock_db.add.call_count >= 3


@pytest.mark.asyncio
async def test_update_all_satellite_status_with_error(satellite_service, mock_db):
    """Test satellite status update with error handling."""
    with patch.object(
        satellite_service, "check_sentinel2_health", side_effect=ee.EEException("API error")
    ):
        # Should handle the error gracefully
        with pytest.raises(SatelliteHealthCheckError):
            await satellite_service.update_all_satellite_status(mock_db)

        # Rollback should be called on error
        assert mock_db.rollback.awaited


# ============================================================================
# Summary Retrieval Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_satellite_health_summary_no_records(satellite_service, mock_db):
    """Test health summary retrieval when no records exist."""
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    result = await satellite_service.get_satellite_health_summary(mock_db)

    assert result["total_satellites"] == 0
    assert result["operational_count"] == 0
    assert result["degraded_count"] == 0
    assert result["offline_count"] == 0
    assert result["average_uptime"] == 0.0


@pytest.mark.asyncio
async def test_get_satellite_health_summary_with_records(satellite_service, mock_db):
    """Test health summary retrieval with satellite records."""
    # Create mock satellite status records
    mock_satellites = [
        Mock(
            satellite_name="sentinel-2",
            status="operational",
            uptime_percent=98.7,
        ),
        Mock(
            satellite_name="landsat-8",
            status="operational",
            uptime_percent=97.2,
        ),
        Mock(
            satellite_name="era5-land",
            status="degraded",
            uptime_percent=95.0,
        ),
    ]
    
    mock_db.execute.return_value.scalars.return_value.all.return_value = mock_satellites

    result = await satellite_service.get_satellite_health_summary(mock_db)

    assert result["total_satellites"] == 3
    assert result["operational_count"] == 2
    assert result["degraded_count"] == 1
    assert result["offline_count"] == 0
    assert result["average_uptime"] == pytest.approx(96.97, rel=0.1)


# ============================================================================
# Health History Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_health_history(satellite_service, mock_db):
    """Test retrieving satellite health history."""
    mock_records = [
        Mock(
            satellite_name="sentinel-2",
            status="operational",
            coverage_percent=95.5,
            accuracy_percent=92.3,
            data_quality="high",
            uptime_percent=98.7,
            last_update=datetime.utcnow(),
        ),
    ]
    
    mock_db.execute.return_value.scalars.return_value.all.return_value = mock_records

    result = await satellite_service.get_health_history(
        mock_db, 
        satellite_name="sentinel-2",
        days=7
    )

    assert len(result) == 1
    assert result[0]["satellite_name"] == "sentinel-2"
    assert result[0]["status"] == "operational"


# ============================================================================
# Validation Tests
# ============================================================================


def test_coverage_threshold_constants():
    """Test that coverage thresholds are properly configured."""
    service = SatelliteHealthService()
    
    assert service.COVERAGE_THRESHOLD_OPERATIONAL == 90.0
    assert service.COVERAGE_THRESHOLD_DEGRADED == 50.0
    assert service.COVERAGE_THRESHOLD_OPERATIONAL > service.COVERAGE_THRESHOLD_DEGRADED


@pytest.mark.asyncio
async def test_health_check_metadata_structure(satellite_service, mock_ee_manager):
    """Test that health check returns proper metadata structure."""
    mock_collection = MagicMock()
    mock_filtered = MagicMock()
    mock_low_cloud = MagicMock()

    mock_ee_manager.ImageCollection.return_value = mock_collection
    mock_collection.filterDate.return_value = mock_filtered
    mock_filtered.filter.return_value = mock_low_cloud
    
    mock_low_cloud.size.return_value.getInfo.return_value = 143
    mock_filtered.size.return_value.getInfo.return_value = 150

    result = await satellite_service.check_sentinel2_health()

    assert "metadata" in result
    assert isinstance(result["metadata"], dict)
    assert "total_images" in result["metadata"]
    assert "check_date" in result["metadata"]
    assert "date_range_days" in result["metadata"]
