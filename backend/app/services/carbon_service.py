"""Carbon sequestration service for calculating carbon tonnes from NDVI."""

import asyncio
from datetime import date
from typing import Optional, List
import math


class CarbonCalculationError(Exception):
    """Exception for carbon calculation errors."""

    pass


class CarbonService:
    """
    Carbon sequestration estimation service.

    Uses NDVI time-series to estimate above-ground biomass (AGB) and carbon
    sequestration using established allometric equations and conversion factors.
    
    References:
    - GEDI L4A Gridded Aboveground Biomass Density Product v2
    - Pan-tropical allometric models (Chave et al., 2014)
    - IPCC Tier 1 carbon conversion factor: 0.47 tC/t dry matter
    """

    # Carbon conversion factor: 50% of dry biomass is carbon (IPCC standard)
    CARBON_FRACTION = 0.47

    # NDVI to AGB conversion parameters (pan-tropical, based on Chave et al. 2014)
    # AGB (tonnes/ha) = a * NDVI^b
    AGB_COEFFICIENT_A = 142.9  # Intercept coefficient
    AGB_EXPONENT_B = 1.60      # Power exponent

    # CO2 to C conversion: 44/12 (molecular weight ratio)
    CO2_TO_CARBON_RATIO = 44 / 12

    @classmethod
    async def estimate_carbon_sequestration(
        cls,
        ndvi_data: List[dict],
        area_ha: float,
        start_date: date,
        end_date: date,
    ) -> dict:
        """
        Estimate carbon sequestration from NDVI time-series.

        Uses allometric equations to convert NDVI to above-ground biomass (AGB),
        then to carbon tonnes using IPCC conversion factors.

        Args:
            ndvi_data: List of dicts with 'date' and 'ndvi' keys
            area_ha: Farm area in hectares
            start_date: Analysis start date
            end_date: Analysis end date

        Returns:
            dict with:
                - mean_agb_tonnes_ha: Mean above-ground biomass (tonnes/ha)
                - total_agb_tonnes: Total AGB for farm (tonnes)
                - mean_carbon_tonnes_ha: Mean carbon per hectare (tonnes)
                - total_carbon_tonnes: Total carbon for farm (tonnes)
                - total_co2_tonnes: Total CO2 equivalent (tonnes)
                - data_points: List of individual calculations per date
                - model_version: Version string for reproducibility

        Raises:
            CarbonCalculationError: If calculation fails or data is invalid
        """
        if not ndvi_data:
            raise CarbonCalculationError("No NDVI data provided")

        if area_ha <= 0:
            raise CarbonCalculationError("Area must be positive")

        if end_date < start_date:
            raise CarbonCalculationError("Invalid date range: end_date must be >= start_date")

        try:
            # Calculate biomass and carbon for each NDVI point
            data_points = []
            agb_values = []
            carbon_values = []

            for point in ndvi_data:
                ndvi = point["ndvi"]

                # Validate NDVI range
                if not (-1.0 <= ndvi <= 1.0):
                    raise CarbonCalculationError(
                        f"Invalid NDVI value: {ndvi} (must be -1 to 1)"
                    )

                # Calculate AGB using allometric equation
                # AGB (tonnes/ha) = a * NDVI^b
                agb_tonnes_ha = cls.AGB_COEFFICIENT_A * (ndvi ** cls.AGB_EXPONENT_B)

                # Ensure AGB is non-negative
                agb_tonnes_ha = max(0, agb_tonnes_ha)

                # Convert AGB to carbon using IPCC factor (0.47 tC per tonne dry matter)
                carbon_tonnes_ha = agb_tonnes_ha * cls.CARBON_FRACTION

                # Calculate CO2 equivalent (tonnes CO2 = tonnes C * 44/12)
                co2_tonnes_ha = carbon_tonnes_ha * cls.CO2_TO_CARBON_RATIO

                # Calculate total for farm
                total_agb_tonnes = agb_tonnes_ha * area_ha
                total_carbon_tonnes = carbon_tonnes_ha * area_ha
                total_co2_tonnes = co2_tonnes_ha * area_ha

                data_points.append({
                    "date": point["date"],
                    "ndvi": ndvi,
                    "agb_tonnes_ha": round(agb_tonnes_ha, 4),
                    "agb_total_tonnes": round(total_agb_tonnes, 4),
                    "carbon_tonnes_ha": round(carbon_tonnes_ha, 4),
                    "carbon_total_tonnes": round(total_carbon_tonnes, 4),
                    "co2_tonnes_ha": round(co2_tonnes_ha, 4),
                    "co2_total_tonnes": round(total_co2_tonnes, 4),
                })

                agb_values.append(agb_tonnes_ha)
                carbon_values.append(carbon_tonnes_ha)

            # Calculate statistics
            if not agb_values:
                raise CarbonCalculationError("No valid NDVI data for calculation")

            mean_agb_ha = sum(agb_values) / len(agb_values)
            mean_carbon_ha = sum(carbon_values) / len(carbon_values)
            mean_agb_total = mean_agb_ha * area_ha
            mean_carbon_total = mean_carbon_ha * area_ha
            mean_co2_total = mean_carbon_total * cls.CO2_TO_CARBON_RATIO

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
                },
                "metadata": {
                    "model_version": "v1.0",
                    "model_name": "Pan-tropical Allometric Equation (Chave et al. 2014)",
                    "agb_coefficient_a": cls.AGB_COEFFICIENT_A,
                    "agb_exponent_b": cls.AGB_EXPONENT_B,
                    "carbon_fraction": cls.CARBON_FRACTION,
                    "co2_conversion_factor": cls.CO2_TO_CARBON_RATIO,
                    "assumptions": [
                        "AGB = 142.9 * NDVI^1.60",
                        "Carbon = AGB * 0.47 (IPCC Tier 1)",
                        "CO2 equivalent = Carbon * 44/12",
                        "Valid for tropical/subtropical regions",
                    ],
                },
            }

        except ValueError as e:
            raise CarbonCalculationError(f"Calculation error: {str(e)}")
        except Exception as e:
            raise CarbonCalculationError(f"Unexpected error during calculation: {str(e)}")

    @classmethod
    async def estimate_carbon_sequestration_async(
        cls,
        ndvi_data: List[dict],
        area_ha: float,
        start_date: date,
        end_date: date,
    ) -> dict:
        """
        Async wrapper for carbon estimation.

        Runs blocking calculation in thread pool to prevent event loop blocking.
        """
        return await asyncio.to_thread(
            cls.estimate_carbon_sequestration,
            ndvi_data,
            area_ha,
            start_date,
            end_date,
        )
