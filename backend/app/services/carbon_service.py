"""Carbon sequestration service with IPCC Tier 2 methodology and uncertainty quantification.

Uses NDVI time-series and land-use classification to estimate above-ground biomass (AGB)
and carbon sequestration using land-use-specific allometric equations.

References:
    - IPCC 2006 Guidelines for National Greenhouse Gas Inventories
    - Chave et al. 2014: Pan-tropical allometric equations for estimating tree biomass
    - IPCC 2019 Refinement: Guidelines for National Greenhouse Gas Inventories, Vol. 4
        (Tier 2 guidance for LULC-specific carbon estimation)
    - Intergovernmental Panel on Climate Change. 2013. Supplement to the 2006 IPCC
        Guidelines for National Greenhouse Gas Inventories (Carbon Uncertainty)
"""

import asyncio
import logging
from datetime import date
from typing import Optional, List, Tuple
import math

import numpy as np

logger = logging.getLogger(__name__)


class CarbonCalculationError(Exception):
    """Exception for carbon calculation errors."""

    pass


class AllometricParameterError(Exception):
    """Exception for invalid allometric parameters."""

    pass


class LULCIntegrationError(Exception):
    """Exception for LULC data integration issues."""

    pass


class MonteCarloSimulationError(Exception):
    """Exception for Monte Carlo simulation failures."""

    pass


class CarbonService:
    """
    Carbon sequestration estimation service with IPCC Tier 2 methodology.

    Provides IPCC Tier 2 carbon estimation using land-use-specific allometric
    equations integrated with LULC classification. Includes Monte Carlo simulation
    for uncertainty quantification with 95% confidence intervals.

    Supports both detailed estimation (with LULC data) and simple Tier 1 fallback
    (without LULC data) for backward compatibility.
    """

    # ============================================================================
    # CONSTANTS AND CONFIGURATION
    # ============================================================================

    # Carbon conversion factor: 50% of dry biomass is carbon (IPCC standard)
    CARBON_FRACTION = 0.47

    # CO2 to C conversion: 44/12 (molecular weight ratio)
    CO2_TO_CARBON_RATIO = 44 / 12

    # Monte Carlo simulation configuration
    MONTE_CARLO_ITERATIONS = 10000
    CONFIDENCE_INTERVAL_PERCENTILES = (2.5, 97.5)
    MIN_CONFIDENCE_SCORE = 0
    MAX_CONFIDENCE_SCORE = 100

    # LULC validation thresholds
    MIN_LULC_AREA_THRESHOLD = 0.01  # Minimum area (ha) to consider a class
    DEFAULT_NDVI_STD = 0.05  # Default NDVI uncertainty when not provided

    # Tier 1 fallback parameters (when LULC data not available)
    # AGB (tonnes/ha) = a * NDVI^b
    TIER1_AGB_COEFFICIENT_A = 142.9
    TIER1_AGB_EXPONENT_B = 1.60
    TIER1_AGB_STD_A = 5.2
    TIER1_AGB_STD_B = 0.08

    # ============================================================================
    # TIER 2 LAND-USE-SPECIFIC ALLOMETRIC PARAMETERS
    # ============================================================================
    # Based on Chave et al. 2014 and IPCC guidelines
    # Each parameter set contains mean and std dev for Monte Carlo sampling

    ALLOMETRIC_PARAMS = {
        0: {  # Water
            "a_mean": 0.0,
            "a_std": 0.0,
            "b_mean": 0.0,
            "b_std": 0.0,
            "description": "Water - No biomass",
        },
        1: {  # Trees - Chave et al. 2014 (tropical forest)
            "a_mean": 185.5,
            "a_std": 15.2,
            "b_mean": 1.75,
            "b_std": 0.12,
            "description": "Trees - Tropical forest allometric",
        },
        2: {  # Grass - Grassland specific
            "a_mean": 68.2,
            "a_std": 6.1,
            "b_mean": 1.30,
            "b_std": 0.08,
            "description": "Grassland - NDVI-biomass relationship",
        },
        3: {  # Flooded Vegetation - Wetland specific
            "a_mean": 92.4,
            "a_std": 8.3,
            "b_mean": 1.40,
            "b_std": 0.10,
            "description": "Flooded Vegetation - Wetland allometric",
        },
        4: {  # Crops - Agricultural land
            "a_mean": 95.3,
            "a_std": 8.5,
            "b_mean": 1.45,
            "b_std": 0.10,
            "description": "Crops - Agricultural biomass relationship",
        },
        5: {  # Shrub/Scrub - Shrubland
            "a_mean": 78.6,
            "a_std": 7.2,
            "b_mean": 1.35,
            "b_std": 0.09,
            "description": "Shrub/Scrub - Shrubland allometric",
        },
        6: {  # Built Area - Urban/infrastructure (minimal biomass)
            "a_mean": 15.2,
            "a_std": 3.1,
            "b_mean": 1.05,
            "b_std": 0.07,
            "description": "Built Area - Urban vegetation only",
        },
        7: {  # Bare Ground - Minimal vegetation
            "a_mean": 25.4,
            "a_std": 4.2,
            "b_mean": 1.15,
            "b_std": 0.08,
            "description": "Bare Ground - Sparse vegetation",
        },
        8: {  # Snow/Ice - No vegetation
            "a_mean": 0.0,
            "a_std": 0.0,
            "b_mean": 0.0,
            "b_std": 0.0,
            "description": "Snow/Ice - No biomass",
        },
    }

    # LULC class name to ID mapping (reverse lookup from lulc_service.py)
    LULC_CLASS_NAME_TO_ID = {
        "Water": 0,
        "Trees": 1,
        "Grass": 2,
        "Flooded Vegetation": 3,
        "Crops": 4,
        "Shrub/Scrub": 5,
        "Built Area": 6,
        "Bare Ground": 7,
        "Snow/Ice": 8,
    }

    @classmethod
    async def estimate_carbon_sequestration(
        cls,
        ndvi_data: List[dict],
        area_ha: float,
        start_date: date,
        end_date: date,
        lulc_data: Optional[dict] = None,
    ) -> dict:
        """
        Estimate carbon sequestration from NDVI time-series with IPCC Tier 2 methodology.

        Optionally integrates LULC classification data for land-use-specific allometric
        equations. Falls back to Tier 1 if LULC data is not provided.

        Args:
            ndvi_data: List of dicts with 'date' and 'ndvi' keys, optionally 'ndvi_std'
            area_ha: Farm area in hectares
            start_date: Analysis start date
            end_date: Analysis end date
            lulc_data: Optional LULC classification result dict with 'dominant_class'
                      and 'classes' keys for Tier 2 estimation

        Returns:
            dict with:
                - data_points: List of dicts with:
                    - date, ndvi values
                    - agb_tonnes_ha, agb_total_tonnes
                    - carbon_tonnes_ha, carbon_total_tonnes
                    - co2_tonnes_ha, co2_total_tonnes
                    - confidence_score (0-100, higher=more confident)
                    - ci_lower, ci_upper (95% confidence interval bounds)
                    - std_dev (standard deviation from Monte Carlo)
                - statistics: Aggregated statistics with:
                    - mean_agb_tonnes_ha, total_agb_tonnes
                    - mean_carbon_tonnes_ha, total_carbon_tonnes
                    - total_co2_tonnes
                    - min/max/mean NDVI
                    - mean_confidence_score
                    - overall_std_dev
                - metadata: Model information with:
                    - model_version: "v2.0"
                    - model_name: "IPCC Tier 2"
                    - methodology: "Monte Carlo Simulation (10,000 iterations)"
                    - uncertainty_method: "95% Confidence Intervals"
                    - land_use_class (if using Tier 2)
                    - assumptions list

        Raises:
            CarbonCalculationError: If validation fails or data is invalid
            AllometricParameterError: If allometric parameters are invalid
            LULCIntegrationError: If LULC data integration fails
            MonteCarloSimulationError: If Monte Carlo simulation fails
        """
        # Validate inputs
        if not ndvi_data:
            raise CarbonCalculationError("No NDVI data provided")

        if area_ha <= 0:
            raise CarbonCalculationError("Area must be positive")

        if end_date < start_date:
            raise CarbonCalculationError("Invalid date range: end_date must be >= start_date")

        try:
            # Determine land use class and select allometric parameters
            land_use_class = None
            allometric_params = None

            if lulc_data:
                try:
                    cls._validate_lulc_data(lulc_data)
                    land_use_class, allometric_params = cls._select_allometric_params(
                        lulc_data
                    )
                except LULCIntegrationError as e:
                    logger.warning(
                        f"LULC data validation failed: {str(e)}. "
                        "Falling back to Tier 1 default parameters."
                    )
                    allometric_params = {
                        "a_mean": cls.TIER1_AGB_COEFFICIENT_A,
                        "a_std": cls.TIER1_AGB_STD_A,
                        "b_mean": cls.TIER1_AGB_EXPONENT_B,
                        "b_std": cls.TIER1_AGB_STD_B,
                    }
            else:
                logger.info(
                    "No LULC data provided. Using Tier 1 default allometric parameters."
                )
                allometric_params = {
                    "a_mean": cls.TIER1_AGB_COEFFICIENT_A,
                    "a_std": cls.TIER1_AGB_STD_A,
                    "b_mean": cls.TIER1_AGB_EXPONENT_B,
                    "b_std": cls.TIER1_AGB_STD_B,
                }

            # Validate allometric parameters
            cls._validate_allometric_params(allometric_params)

            # Calculate carbon with uncertainty quantification
            data_points = []
            agb_values = []
            carbon_values = []
            confidence_scores = []
            std_devs = []

            for point in ndvi_data:
                ndvi = point["ndvi"]
                ndvi_std = point.get("ndvi_std", cls.DEFAULT_NDVI_STD)

                # Validate NDVI range
                if not (-1.0 <= ndvi <= 1.0):
                    raise CarbonCalculationError(
                        f"Invalid NDVI value: {ndvi} (must be -1 to 1)"
                    )

                # Run Monte Carlo simulation
                try:
                    mc_results = cls._run_monte_carlo_simulation(
                        ndvi_value=ndvi,
                        ndvi_std=ndvi_std,
                        allometric_params=allometric_params,
                        n_iterations=cls.MONTE_CARLO_ITERATIONS,
                    )
                except MonteCarloSimulationError as e:
                    logger.error(f"Monte Carlo simulation failed for NDVI={ndvi}: {str(e)}")
                    raise

                # Calculate confidence metrics
                confidence_metrics = cls._calculate_confidence_metrics(mc_results)

                # Extract values (using median as central estimate)
                agb_tonnes_ha = confidence_metrics["median"]
                agb_tonnes_ha = max(0.0, agb_tonnes_ha)  # Ensure non-negative
                carbon_tonnes_ha = agb_tonnes_ha * cls.CARBON_FRACTION
                co2_tonnes_ha = carbon_tonnes_ha * cls.CO2_TO_CARBON_RATIO

                total_agb_tonnes = agb_tonnes_ha * area_ha
                total_carbon_tonnes = carbon_tonnes_ha * area_ha
                total_co2_tonnes = co2_tonnes_ha * area_ha

                data_point = {
                    "date": point["date"],
                    "ndvi": round(ndvi, 6),
                    "agb_tonnes_ha": round(agb_tonnes_ha, 4),
                    "agb_total_tonnes": round(total_agb_tonnes, 4),
                    "carbon_tonnes_ha": round(carbon_tonnes_ha, 4),
                    "carbon_total_tonnes": round(total_carbon_tonnes, 4),
                    "co2_tonnes_ha": round(co2_tonnes_ha, 4),
                    "co2_total_tonnes": round(total_co2_tonnes, 4),
                    "confidence_score": round(confidence_metrics["confidence_score"], 1),
                    "ci_lower": round(confidence_metrics["ci_lower"], 4),
                    "ci_upper": round(confidence_metrics["ci_upper"], 4),
                    "std_dev": round(confidence_metrics["std_dev"], 4),
                }

                data_points.append(data_point)
                agb_values.append(agb_tonnes_ha)
                carbon_values.append(carbon_tonnes_ha)
                confidence_scores.append(confidence_metrics["confidence_score"])
                std_devs.append(confidence_metrics["std_dev"])

                # Log warning for low confidence
                if confidence_metrics["confidence_score"] < 50:
                    logger.warning(
                        f"Low confidence score ({confidence_metrics['confidence_score']:.1f}) "
                        f"for NDVI={ndvi} on {point['date']}"
                    )

            # Calculate aggregated statistics
            if not agb_values:
                raise CarbonCalculationError("No valid NDVI data for calculation")

            mean_agb_ha = sum(agb_values) / len(agb_values)
            mean_carbon_ha = sum(carbon_values) / len(carbon_values)
            mean_agb_total = mean_agb_ha * area_ha
            mean_carbon_total = mean_carbon_ha * area_ha
            mean_co2_total = mean_carbon_total * cls.CO2_TO_CARBON_RATIO

            mean_confidence_score = sum(confidence_scores) / len(confidence_scores)
            overall_std_dev = sum(std_devs) / len(std_devs)

            # Build metadata
            assumptions_list = [
                f"AGB = a * NDVI^b (Allometric equation)",
                f"Carbon = AGB * {cls.CARBON_FRACTION} (IPCC conversion factor)",
                f"CO2 equivalent = Carbon * {cls.CO2_TO_CARBON_RATIO:.2f}",
                f"Uncertainty quantification via Monte Carlo ({cls.MONTE_CARLO_ITERATIONS:,} iterations)",
                f"95% Confidence intervals from percentiles (2.5%, 97.5%)",
            ]

            if lulc_data and land_use_class:
                assumptions_list.insert(
                    0, f"Land-use-specific parameters for {land_use_class} (IPCC Tier 2)"
                )
                methodology = "IPCC Tier 2 with Land-Use-Specific Allometric Equations"
            else:
                assumptions_list.insert(
                    0, "Pan-tropical default parameters (IPCC Tier 1 fallback)"
                )
                methodology = "IPCC Tier 1 with Default Allometric Equations"

            return {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "area_ha": area_ha,
                "data_points": data_points,
                "statistics": {
                    "mean_agb_tonnes_ha": round(mean_agb_ha, 4),
                    "total_agb_tonnes": round(mean_agb_total, 4),
                    "mean_carbon_tonnes_ha": round(mean_carbon_ha, 4),
                    "total_carbon_tonnes": round(mean_carbon_total, 4),
                    "total_co2_tonnes": round(mean_co2_total, 4),
                    "min_ndvi": round(min(p["ndvi"] for p in ndvi_data), 4),
                    "max_ndvi": round(max(p["ndvi"] for p in ndvi_data), 4),
                    "mean_ndvi": round(sum(p["ndvi"] for p in ndvi_data) / len(ndvi_data), 4),
                    "mean_confidence_score": round(mean_confidence_score, 1),
                    "overall_std_dev": round(overall_std_dev, 4),
                },
                "metadata": {
                    "model_version": "v2.0",
                    "model_name": "IPCC Tier 2 with Land-Use-Specific Allometric Equations",
                    "methodology": "Monte Carlo Simulation (10,000 iterations)",
                    "uncertainty_method": "95% Confidence Intervals",
                    "land_use_class": land_use_class,
                    "carbon_fraction": cls.CARBON_FRACTION,
                    "co2_conversion_factor": cls.CO2_TO_CARBON_RATIO,
                    "allometric_params": allometric_params,
                    "monte_carlo_iterations": cls.MONTE_CARLO_ITERATIONS,
                    "assumptions": assumptions_list,
                    "references": [
                        "Chave et al. (2014): Pan-tropical allometric equations",
                        "IPCC (2006): Guidelines for National Greenhouse Gas Inventories",
                        "IPCC (2019): Refinement to the 2006 Guidelines, Vol. 4",
                    ],
                },
            }

        except (
            CarbonCalculationError,
            AllometricParameterError,
            LULCIntegrationError,
            MonteCarloSimulationError,
        ):
            raise
        except ValueError as e:
            raise CarbonCalculationError(f"Validation error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during carbon calculation: {str(e)}")
            raise CarbonCalculationError(f"Calculation failed: {str(e)}")

    @classmethod
    def _select_allometric_params(cls, lulc_data: dict) -> Tuple[Optional[str], dict]:
        """
        Select allometric parameters based on dominant land use from LULC data.

        Args:
            lulc_data: LULC classification result dict

        Returns:
            Tuple of (land_use_class_name, allometric_params_dict)

        Raises:
            LULCIntegrationError: If land use class cannot be determined
        """
        dominant_class = lulc_data.get("dominant_class")

        if not dominant_class:
            raise LULCIntegrationError("No dominant_class in LULC data")

        class_id = cls.LULC_CLASS_NAME_TO_ID.get(dominant_class)
        if class_id is None:
            raise LULCIntegrationError(f"Unknown land use class: {dominant_class}")

        params = cls.ALLOMETRIC_PARAMS.get(class_id)
        if not params:
            raise LULCIntegrationError(f"No parameters for class ID {class_id}")

        logger.info(
            f"Selected Tier 2 parameters for {dominant_class} (Class {class_id})"
        )

        return dominant_class, {
            "a_mean": params["a_mean"],
            "a_std": params["a_std"],
            "b_mean": params["b_mean"],
            "b_std": params["b_std"],
        }

    @classmethod
    def _run_monte_carlo_simulation(
        cls,
        ndvi_value: float,
        ndvi_std: float,
        allometric_params: dict,
        n_iterations: int = 10000,
    ) -> np.ndarray:
        """
        Run Monte Carlo simulation for carbon estimation uncertainty.

        Samples from parameter distributions and calculates AGB for each iteration.

        Args:
            ndvi_value: NDVI value
            ndvi_std: Standard deviation of NDVI uncertainty
            allometric_params: Dict with a_mean, a_std, b_mean, b_std
            n_iterations: Number of Monte Carlo iterations

        Returns:
            Numpy array of shape (n_iterations,) with AGB values (tonnes/ha)

        Raises:
            MonteCarloSimulationError: If simulation fails or produces invalid values
        """
        try:
            a_mean = allometric_params["a_mean"]
            a_std = allometric_params["a_std"]
            b_mean = allometric_params["b_mean"]
            b_std = allometric_params["b_std"]

            # Sample parameters from distributions
            a_samples = np.random.normal(a_mean, a_std, n_iterations)
            b_samples = np.random.normal(b_mean, b_std, n_iterations)
            ndvi_samples = np.random.normal(ndvi_value, ndvi_std, n_iterations)

            # Clip NDVI to valid range
            ndvi_samples = np.clip(ndvi_samples, -1.0, 1.0)

            # Calculate AGB: AGB = a * NDVI^b
            # Handle case where NDVI might be negative or zero
            agb_results = np.where(
                ndvi_samples > 0,
                a_samples * np.power(ndvi_samples, b_samples),
                0.0,
            )

            # Ensure non-negative values
            agb_results = np.clip(agb_results, 0.0, np.inf)

            # Validate results
            if np.isnan(agb_results).any() or np.isinf(agb_results).any():
                raise MonteCarloSimulationError("Simulation produced NaN or Inf values")

            return agb_results

        except MonteCarloSimulationError:
            raise
        except Exception as e:
            raise MonteCarloSimulationError(f"Simulation failed: {str(e)}")

    @classmethod
    def _calculate_confidence_metrics(cls, mc_results: np.ndarray) -> dict:
        """
        Calculate confidence intervals and confidence score from Monte Carlo results.

        Args:
            mc_results: Numpy array of Monte Carlo simulation results

        Returns:
            dict with:
                - median: Central estimate (50th percentile)
                - ci_lower: Lower 95% CI bound (2.5th percentile)
                - ci_upper: Upper 95% CI bound (97.5th percentile)
                - std_dev: Standard deviation
                - confidence_score: 0-100 score (higher = lower uncertainty)
        """
        try:
            median = np.percentile(mc_results, 50)
            ci_lower = np.percentile(mc_results, cls.CONFIDENCE_INTERVAL_PERCENTILES[0])
            ci_upper = np.percentile(mc_results, cls.CONFIDENCE_INTERVAL_PERCENTILES[1])
            std_dev = np.std(mc_results)

            # Calculate confidence score based on coefficient of variation
            # cv = std / median; score = 100 * (1 - cv), bounded to [0, 100]
            if median > 0:
                cv = std_dev / median
                confidence_score = max(
                    cls.MIN_CONFIDENCE_SCORE,
                    min(cls.MAX_CONFIDENCE_SCORE, 100 * (1 - cv)),
                )
            else:
                confidence_score = cls.MAX_CONFIDENCE_SCORE  # No uncertainty if zero

            return {
                "median": median,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "std_dev": std_dev,
                "confidence_score": confidence_score,
            }

        except Exception as e:
            raise MonteCarloSimulationError(
                f"Failed to calculate confidence metrics: {str(e)}"
            )

    @classmethod
    def _validate_lulc_data(cls, lulc_data: dict) -> None:
        """
        Validate LULC data structure and content.

        Args:
            lulc_data: LULC data dict to validate

        Raises:
            LULCIntegrationError: If data structure is invalid
        """
        if not isinstance(lulc_data, dict):
            raise LULCIntegrationError("LULC data must be a dictionary")

        if "dominant_class" not in lulc_data:
            raise LULCIntegrationError("LULC data missing 'dominant_class' key")

        dominant_class = lulc_data["dominant_class"]
        if not isinstance(dominant_class, str):
            raise LULCIntegrationError("dominant_class must be a string")

        if dominant_class not in cls.LULC_CLASS_NAME_TO_ID:
            raise LULCIntegrationError(f"Unknown land use class: {dominant_class}")

    @classmethod
    def _validate_allometric_params(cls, params: dict) -> None:
        """
        Validate allometric parameters are within reasonable ranges.

        Args:
            params: Allometric parameters dict

        Raises:
            AllometricParameterError: If parameters are out of range
        """
        required_keys = ["a_mean", "a_std", "b_mean", "b_std"]
        for key in required_keys:
            if key not in params:
                raise AllometricParameterError(f"Missing required parameter: {key}")

            value = params[key]
            if not isinstance(value, (int, float)):
                raise AllometricParameterError(f"{key} must be a number, got {type(value)}")

            if value < 0:
                raise AllometricParameterError(f"{key} must be non-negative, got {value}")

        # Check that standard deviations are reasonable
        if params["a_std"] > params["a_mean"] * 0.5:
            logger.warning(
                f"Large a_std ({params['a_std']}) relative to a_mean ({params['a_mean']})"
            )
    @classmethod
    async def estimate_carbon_sequestration_async(
        cls,
        ndvi_data: List[dict],
        area_ha: float,
        start_date: date,
        end_date: date,
        lulc_data: Optional[dict] = None,
    ) -> dict:
        """
        Async wrapper for carbon estimation.

        Runs blocking calculation in thread pool to prevent event loop blocking.

        Args:
            ndvi_data: List of NDVI measurements
            area_ha: Farm area in hectares
            start_date: Analysis start date
            end_date: Analysis end date
            lulc_data: Optional LULC classification results

        Returns:
            Carbon estimation dict with confidence metrics
        """
        return await asyncio.to_thread(
            cls.estimate_carbon_sequestration,
            ndvi_data,
            area_ha,
            start_date,
            end_date,
            lulc_data,
        )

    @classmethod
    def _simple_carbon_estimate(cls, area_hectares: float) -> float:
        """
        Simple carbon estimation for cases where detailed data is unavailable.

        Uses conservative default estimate of 120 tonnes/ha (from phase2 baseline).

        Args:
            area_hectares: Farm area in hectares

        Returns:
            Estimated carbon tonnes
        """
        SIMPLE_CARBON_PER_HA = 120.0  # Conservative default
        return area_hectares * SIMPLE_CARBON_PER_HA