"""Comprehensive unit tests for CarbonService with IPCC Tier 2 methodology.

Tests cover:
- Allometric parameter selection
- Monte Carlo simulation
- Confidence interval calculation
- LULC data integration
- Error handling and validation
- Backward compatibility
- Performance
"""

import pytest
import numpy as np
from datetime import date
from unittest.mock import Mock, patch, MagicMock

from app.services.carbon_service import (
    CarbonService,
    CarbonCalculationError,
    AllometricParameterError,
    LULCIntegrationError,
    MonteCarloSimulationError,
)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_ndvi_data():
    """Sample NDVI time-series data."""
    return [
        {"date": "2023-01-15", "ndvi": 0.45},
        {"date": "2023-02-15", "ndvi": 0.52},
        {"date": "2023-03-15", "ndvi": 0.58},
        {"date": "2023-04-15", "ndvi": 0.62},
        {"date": "2023-05-15", "ndvi": 0.65},
    ]


@pytest.fixture
def sample_ndvi_data_with_std():
    """Sample NDVI data with uncertainty."""
    return [
        {"date": "2023-01-15", "ndvi": 0.45, "ndvi_std": 0.03},
        {"date": "2023-02-15", "ndvi": 0.52, "ndvi_std": 0.04},
        {"date": "2023-03-15", "ndvi": 0.58, "ndvi_std": 0.02},
    ]


@pytest.fixture
def sample_lulc_data_trees():
    """Sample LULC data with Trees as dominant class."""
    return {
        "dominant_class": "Trees",
        "total_area_ha": 100.0,
        "classes": [
            {"id": 1, "name": "Trees", "area_ha": 60.0, "percentage": 60.0},
            {"id": 2, "name": "Grass", "area_ha": 30.0, "percentage": 30.0},
            {"id": 4, "name": "Crops", "area_ha": 10.0, "percentage": 10.0},
        ],
        "analysis_period": {"start": "2023-01-01", "end": "2023-12-31"},
    }


@pytest.fixture
def sample_lulc_data_crops():
    """Sample LULC data with Crops as dominant class."""
    return {
        "dominant_class": "Crops",
        "total_area_ha": 100.0,
        "classes": [
            {"id": 4, "name": "Crops", "area_ha": 70.0, "percentage": 70.0},
            {"id": 2, "name": "Grass", "area_ha": 30.0, "percentage": 30.0},
        ],
        "analysis_period": {"start": "2023-01-01", "end": "2023-12-31"},
    }


@pytest.fixture
def sample_area_ha():
    """Sample farm area."""
    return 100.0


# ============================================================================
# Test Allometric Parameter Selection
# ============================================================================


class TestAllometricParameterSelection:
    """Test allometric parameter selection from LULC data."""

    def test_select_params_trees(self, sample_lulc_data_trees):
        """Verify Trees class selects correct parameters."""
        land_use_class, params = CarbonService._select_allometric_params(
            sample_lulc_data_trees
        )

        assert land_use_class == "Trees"
        assert params["a_mean"] == 185.5
        assert params["a_std"] == 15.2
        assert params["b_mean"] == 1.75
        assert params["b_std"] == 0.12

    def test_select_params_crops(self, sample_lulc_data_crops):
        """Verify Crops class selects correct parameters."""
        land_use_class, params = CarbonService._select_allometric_params(
            sample_lulc_data_crops
        )

        assert land_use_class == "Crops"
        assert params["a_mean"] == 95.3
        assert params["b_mean"] == 1.45

    def test_select_params_default_fallback(self):
        """Verify fallback when LULC data missing."""
        with pytest.raises(LULCIntegrationError):
            CarbonService._select_allometric_params({})

    def test_select_params_unknown_class(self):
        """Verify handling of unknown land use classes."""
        lulc_data = {"dominant_class": "Unknown Class"}
        with pytest.raises(LULCIntegrationError):
            CarbonService._select_allometric_params(lulc_data)

    def test_select_params_missing_dominant_class(self):
        """Verify error when no dominant class."""
        lulc_data = {"classes": []}
        with pytest.raises(LULCIntegrationError):
            CarbonService._select_allometric_params(lulc_data)


# ============================================================================
# Test Monte Carlo Simulation
# ============================================================================


class TestMonteCarloSimulation:
    """Test Monte Carlo simulation functionality."""

    def test_monte_carlo_output_shape(self):
        """Verify output array has correct shape."""
        params = {
            "a_mean": 142.9,
            "a_std": 5.2,
            "b_mean": 1.60,
            "b_std": 0.08,
        }
        results = CarbonService._run_monte_carlo_simulation(
            ndvi_value=0.5,
            ndvi_std=0.05,
            allometric_params=params,
            n_iterations=1000,
        )

        assert results.shape == (1000,)
        assert isinstance(results, np.ndarray)

    def test_monte_carlo_deterministic(self):
        """With zero std, verify results are consistent."""
        params = {
            "a_mean": 100.0,
            "a_std": 0.0,  # Zero variance
            "b_mean": 1.5,
            "b_std": 0.0,  # Zero variance
        }

        # Run with zero NDVI std
        results = CarbonService._run_monte_carlo_simulation(
            ndvi_value=0.5,
            ndvi_std=0.0,
            allometric_params=params,
            n_iterations=100,
        )

        # All results should be identical (or very close)
        assert np.allclose(results, results[0], atol=1e-10)

    def test_monte_carlo_variability(self):
        """With non-zero std, verify results vary appropriately."""
        params = {
            "a_mean": 142.9,
            "a_std": 15.2,  # Non-zero variance
            "b_mean": 1.60,
            "b_std": 0.08,
        }

        results = CarbonService._run_monte_carlo_simulation(
            ndvi_value=0.5,
            ndvi_std=0.05,
            allometric_params=params,
            n_iterations=1000,
        )

        # Results should have variance (std > 0)
        assert np.std(results) > 0
        # Results should be within reasonable bounds
        assert np.all(results >= 0)  # Non-negative

    def test_monte_carlo_negative_ndvi_handling(self):
        """Verify handling of negative NDVI values."""
        params = {
            "a_mean": 142.9,
            "a_std": 5.2,
            "b_mean": 1.60,
            "b_std": 0.08,
        }

        results = CarbonService._run_monte_carlo_simulation(
            ndvi_value=-0.2,  # Negative NDVI (water body)
            ndvi_std=0.05,
            allometric_params=params,
            n_iterations=100,
        )

        # Should handle gracefully (zero or near-zero values)
        assert len(results) == 100
        assert np.all(results >= 0)

    def test_monte_carlo_no_nan_values(self):
        """Verify simulation doesn't produce NaN or Inf."""
        params = {
            "a_mean": 142.9,
            "a_std": 15.2,
            "b_mean": 1.60,
            "b_std": 0.08,
        }

        results = CarbonService._run_monte_carlo_simulation(
            ndvi_value=0.75,
            ndvi_std=0.05,
            allometric_params=params,
            n_iterations=10000,
        )

        assert not np.isnan(results).any()
        assert not np.isinf(results).any()


# ============================================================================
# Test Confidence Interval Calculation
# ============================================================================


class TestConfidenceMetrics:
    """Test confidence interval and confidence score calculation."""

    def test_confidence_intervals_calculation(self):
        """Verify 95% CI bounds are calculated correctly."""
        # Create test data with known mean
        test_data = np.array([10.0] * 950 + [20.0] * 50)  # 95% at 10, 5% at 20
        metrics = CarbonService._calculate_confidence_metrics(test_data)

        assert "ci_lower" in metrics
        assert "ci_upper" in metrics
        assert "median" in metrics
        assert metrics["ci_lower"] < metrics["median"] < metrics["ci_upper"]

    def test_confidence_score_high_certainty(self):
        """Low variance should yield high confidence score."""
        # Low variance data
        test_data = np.array([50.0 + np.random.normal(0, 1) for _ in range(1000)])
        metrics = CarbonService._calculate_confidence_metrics(test_data)

        # Low variance should give high confidence score
        assert metrics["confidence_score"] > 80

    def test_confidence_score_low_certainty(self):
        """High variance should yield low confidence score."""
        # High variance data
        test_data = np.array([50.0 + np.random.normal(0, 20) for _ in range(1000)])
        metrics = CarbonService._calculate_confidence_metrics(test_data)

        # High variance should give low confidence score
        assert metrics["confidence_score"] < 60

    def test_median_vs_mean(self):
        """Verify median is used as central estimate, not mean."""
        # Skewed distribution
        test_data = np.concatenate([np.random.normal(50, 5, 950), np.array([1000.0])])
        metrics = CarbonService._calculate_confidence_metrics(test_data)

        # Median should be close to 50, mean would be much higher
        assert 45 < metrics["median"] < 55
        assert metrics["median"] != np.mean(test_data)

    def test_zero_variance_confidence(self):
        """Zero variance should give max confidence."""
        test_data = np.array([50.0] * 1000)
        metrics = CarbonService._calculate_confidence_metrics(test_data)

        # Should handle zero std without issues
        assert metrics["confidence_score"] == CarbonService.MAX_CONFIDENCE_SCORE


# ============================================================================
# Test LULC Data Validation
# ============================================================================


class TestLULCValidation:
    """Test LULC data validation."""

    def test_validate_lulc_valid_data(self, sample_lulc_data_trees):
        """Verify valid LULC data passes validation."""
        # Should not raise
        CarbonService._validate_lulc_data(sample_lulc_data_trees)

    def test_validate_lulc_not_dict(self):
        """Verify error when LULC data is not a dict."""
        with pytest.raises(LULCIntegrationError):
            CarbonService._validate_lulc_data([])

    def test_validate_lulc_missing_dominant_class(self):
        """Verify error when dominant_class is missing."""
        with pytest.raises(LULCIntegrationError):
            CarbonService._validate_lulc_data({"classes": []})

    def test_validate_lulc_invalid_class_name(self):
        """Verify error for unknown land use class."""
        with pytest.raises(LULCIntegrationError):
            CarbonService._validate_lulc_data({"dominant_class": "InvalidClass"})


# ============================================================================
# Test Allometric Parameter Validation
# ============================================================================


class TestAllometricValidation:
    """Test allometric parameter validation."""

    def test_validate_params_valid(self):
        """Verify valid parameters pass validation."""
        params = {
            "a_mean": 100.0,
            "a_std": 10.0,
            "b_mean": 1.5,
            "b_std": 0.1,
        }
        # Should not raise
        CarbonService._validate_allometric_params(params)

    def test_validate_params_missing_key(self):
        """Verify error when required key is missing."""
        params = {"a_mean": 100.0, "a_std": 10.0}  # Missing b_mean and b_std
        with pytest.raises(AllometricParameterError):
            CarbonService._validate_allometric_params(params)

    def test_validate_params_negative_value(self):
        """Verify error for negative parameter values."""
        params = {
            "a_mean": -100.0,  # Negative
            "a_std": 10.0,
            "b_mean": 1.5,
            "b_std": 0.1,
        }
        with pytest.raises(AllometricParameterError):
            CarbonService._validate_allometric_params(params)

    def test_validate_params_non_numeric(self):
        """Verify error for non-numeric values."""
        params = {
            "a_mean": "not a number",
            "a_std": 10.0,
            "b_mean": 1.5,
            "b_std": 0.1,
        }
        with pytest.raises(AllometricParameterError):
            CarbonService._validate_allometric_params(params)


# ============================================================================
# Test Integration with LULC Data
# ============================================================================


class TestIntegrationWithLULC:
    """Test full integration with LULC data."""

    @pytest.mark.slow
    def test_estimate_with_lulc_data(self, sample_ndvi_data, sample_lulc_data_trees, sample_area_ha):
        """Test full integration with LULC classification."""
        result = CarbonService.estimate_carbon_sequestration(
            ndvi_data=sample_ndvi_data,
            area_ha=sample_area_ha,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            lulc_data=sample_lulc_data_trees,
        )

        assert "data_points" in result
        assert "statistics" in result
        assert "metadata" in result

        # Verify metadata shows Tier 2
        assert result["metadata"]["model_version"] == "v2.0"
        assert result["metadata"]["land_use_class"] == "Trees"
        assert len(result["data_points"]) == 5

        # Verify confidence metrics in data points
        for dp in result["data_points"]:
            assert "confidence_score" in dp
            assert "ci_lower" in dp
            assert "ci_upper" in dp
            assert "std_dev" in dp
            assert 0 <= dp["confidence_score"] <= 100

    @pytest.mark.slow
    def test_estimate_without_lulc_data(self, sample_ndvi_data, sample_area_ha):
        """Test fallback behavior when LULC data is unavailable."""
        result = CarbonService.estimate_carbon_sequestration(
            ndvi_data=sample_ndvi_data,
            area_ha=sample_area_ha,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            lulc_data=None,
        )

        assert result["metadata"]["land_use_class"] is None
        # Should fall back to Tier 1
        assert "Tier 1" in result["metadata"]["assumptions"][0]

    def test_lulc_class_mapping(self):
        """Verify correct mapping from class names to IDs."""
        for class_name, class_id in CarbonService.LULC_CLASS_NAME_TO_ID.items():
            assert 0 <= class_id <= 8
            assert class_name in CarbonService.ALLOMETRIC_PARAMS[class_id]["description"]


# ============================================================================
# Test Error Handling and Validation
# ============================================================================


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_ndvi_range(self, sample_area_ha):
        """Verify error for NDVI outside [-1, 1]."""
        bad_data = [{"date": "2023-01-15", "ndvi": 1.5}]  # NDVI > 1
        with pytest.raises(CarbonCalculationError):
            CarbonService.estimate_carbon_sequestration(
                ndvi_data=bad_data,
                area_ha=sample_area_ha,
                start_date=date(2023, 1, 1),
                end_date=date(2023, 12, 31),
            )

    def test_negative_area(self, sample_ndvi_data):
        """Verify error for negative area."""
        with pytest.raises(CarbonCalculationError):
            CarbonService.estimate_carbon_sequestration(
                ndvi_data=sample_ndvi_data,
                area_ha=-100.0,  # Negative
                start_date=date(2023, 1, 1),
                end_date=date(2023, 12, 31),
            )

    def test_empty_ndvi_data(self, sample_area_ha):
        """Verify error for empty data."""
        with pytest.raises(CarbonCalculationError):
            CarbonService.estimate_carbon_sequestration(
                ndvi_data=[],
                area_ha=sample_area_ha,
                start_date=date(2023, 1, 1),
                end_date=date(2023, 12, 31),
            )

    def test_invalid_date_range(self, sample_ndvi_data, sample_area_ha):
        """Verify error for invalid date range."""
        with pytest.raises(CarbonCalculationError):
            CarbonService.estimate_carbon_sequestration(
                ndvi_data=sample_ndvi_data,
                area_ha=sample_area_ha,
                start_date=date(2023, 12, 31),
                end_date=date(2023, 1, 1),  # End before start
            )

    def test_zero_area(self, sample_ndvi_data):
        """Verify error for zero area."""
        with pytest.raises(CarbonCalculationError):
            CarbonService.estimate_carbon_sequestration(
                ndvi_data=sample_ndvi_data,
                area_ha=0.0,
                start_date=date(2023, 1, 1),
                end_date=date(2023, 12, 31),
            )


# ============================================================================
# Test Backward Compatibility
# ============================================================================


class TestBackwardCompatibility:
    """Test backward compatibility with Tier 1 approach."""

    @pytest.mark.slow
    def test_tier1_fallback(self, sample_ndvi_data, sample_area_ha):
        """Verify Tier 1 calculations still work when LULC unavailable."""
        result = CarbonService.estimate_carbon_sequestration(
            ndvi_data=sample_ndvi_data,
            area_ha=sample_area_ha,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
        )

        # Should work without LULC data
        assert len(result["data_points"]) > 0
        assert result["statistics"]["total_carbon_tonnes"] > 0

    def test_simple_carbon_estimate(self):
        """Test simple fallback carbon estimate."""
        estimate = CarbonService._simple_carbon_estimate(50.0)
        assert estimate == 50.0 * 120.0  # 120 t/ha


# ============================================================================
# Test Performance
# ============================================================================


class TestPerformance:
    """Performance and efficiency tests."""

    @pytest.mark.slow
    def test_monte_carlo_performance(self):
        """Verify 10,000 iterations complete in reasonable time."""
        import time

        params = {
            "a_mean": 142.9,
            "a_std": 5.2,
            "b_mean": 1.60,
            "b_std": 0.08,
        }

        start_time = time.time()
        results = CarbonService._run_monte_carlo_simulation(
            ndvi_value=0.5,
            ndvi_std=0.05,
            allometric_params=params,
            n_iterations=10000,
        )
        elapsed = time.time() - start_time

        # Should complete in under 5 seconds
        assert elapsed < 5.0
        assert len(results) == 10000

    @pytest.mark.slow
    def test_full_calculation_performance(self, sample_ndvi_data, sample_area_ha):
        """Test full calculation performance with confidence metrics."""
        import time

        start_time = time.time()
        result = CarbonService.estimate_carbon_sequestration(
            ndvi_data=sample_ndvi_data,
            area_ha=sample_area_ha,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
        )
        elapsed = time.time() - start_time

        # 5 data points × 10,000 iterations should complete quickly
        # Allow up to 10 seconds for full calculation
        assert elapsed < 10.0
        assert len(result["data_points"]) == 5
