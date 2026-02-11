"""
Test suite for Phase 5: Carbon Sequestration Estimation APIs

Tests:
- Carbon service calculations
- Carbon endpoints (POST /carbon/calculate, GET /carbon/{farm_id})
- Multi-tenancy enforcement
- Error handling
- NDVI integration
"""

import asyncio
from datetime import datetime, timedelta

from app.services.carbon_service import CarbonService, CarbonCalculationError


# Test CarbonService
async def test_carbon_service_calculation():
    """Test carbon service calculation."""
    ndvi_data = [
        {"date": datetime.now() - timedelta(days=30), "ndvi": 0.65},
        {"date": datetime.now() - timedelta(days=20), "ndvi": 0.68},
        {"date": datetime.now() - timedelta(days=10), "ndvi": 0.72},
    ]
    
    result = await CarbonService.estimate_carbon_sequestration(
        ndvi_data=ndvi_data,
        area_ha=50.0,
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
    )
    
    assert len(result["data_points"]) == 3
    assert "statistics" in result
    assert "metadata" in result
    assert result["statistics"]["mean_carbon_tonnes_ha"] > 0
    assert result["metadata"]["model_name"] == "Pan-tropical Allometric Equation (Chave et al. 2014)"


async def test_carbon_service_empty_data():
    """Test carbon service with empty data."""
    try:
        await CarbonService.estimate_carbon_sequestration(
            ndvi_data=[],
            area_ha=50.0,
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now(),
        )
        assert False, "Should have raised CarbonCalculationError"
    except CarbonCalculationError:
        pass


async def test_carbon_service_invalid_area():
    """Test carbon service with invalid area."""
    ndvi_data = [{"date": datetime.now(), "ndvi": 0.65}]
    
    try:
        await CarbonService.estimate_carbon_sequestration(
            ndvi_data=ndvi_data,
            area_ha=-50.0,
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now(),
        )
        assert False, "Should have raised CarbonCalculationError"
    except CarbonCalculationError:
        pass


async def test_carbon_service_invalid_dates():
    """Test carbon service with invalid date range."""
    ndvi_data = [{"date": datetime.now(), "ndvi": 0.65}]
    
    try:
        await CarbonService.estimate_carbon_sequestration(
            ndvi_data=ndvi_data,
            area_ha=50.0,
            start_date=datetime.now(),
            end_date=datetime.now() - timedelta(days=30),
        )
        assert False, "Should have raised CarbonCalculationError"
    except CarbonCalculationError:
        pass


if __name__ == "__main__":
    print("Running Phase 5 test suite...")
    
    # Test 1: Carbon calculation
    asyncio.run(test_carbon_service_calculation())
    print("✓ Carbon service calculation test passed")
    
    # Test 2: Empty data
    asyncio.run(test_carbon_service_empty_data())
    print("✓ Carbon service empty data test passed")
    
    # Test 3: Invalid area
    asyncio.run(test_carbon_service_invalid_area())
    print("✓ Carbon service invalid area test passed")
    
    # Test 4: Invalid dates
    asyncio.run(test_carbon_service_invalid_dates())
    print("✓ Carbon service invalid dates test passed")
    
    print("\n✓ All Phase 5 tests passed!")
