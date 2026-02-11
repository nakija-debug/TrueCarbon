/**
 * Carbon estimation TypeScript types
 * Based on backend/app/schemas/carbon.py
 */

export interface CarbonDataPoint {
  date: string; // YYYY-MM-DD
  ndvi: number;
  agb_tonnes_ha: number;
  agb_total_tonnes: number;
  carbon_tonnes_ha: number;
  carbon_total_tonnes: number;
  co2_tonnes_ha: number;
  co2_total_tonnes: number;
  confidence_score?: number;
  confidence_interval_lower?: number;
  confidence_interval_upper?: number;
  std_dev?: number;
}

export interface CarbonStatistics {
  mean_agb_tonnes_ha: number;
  total_agb_tonnes: number;
  mean_carbon_tonnes_ha: number;
  total_carbon_tonnes: number;
  total_co2_tonnes: number;
  min_ndvi: number;
  max_ndvi: number;
  mean_ndvi: number;
  mean_confidence_score?: number;
  overall_std_dev?: number;
}

export interface CarbonRequest {
  farm_id: number;
  start_date: string; // YYYY-MM-DD
  end_date: string; // YYYY-MM-DD
}

export interface CarbonMetadata {
  model_version: string;
  model_name: string;
  methodology?: string;
  uncertainty_method?: string;
  land_use_class?: string;
  monte_carlo_iterations?: number;
  assumptions?: string;
  confidence_level?: number;
}

export interface CarbonResponse {
  farm_id: number;
  farm_name: string;
  start_date: string;
  end_date: string;
  data_points: CarbonDataPoint[];
  statistics: CarbonStatistics;
  metadata: CarbonMetadata;
  total_points: number;
}
