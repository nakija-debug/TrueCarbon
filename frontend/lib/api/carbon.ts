/**
 * Carbon API Module
 * Handles carbon estimation and reporting requests to FastAPI backend
 */

import axiosInstance from '../api-client';
import type { CarbonRequest } from '@/types/carbon';

export interface CarbonEstimateRequest extends CarbonRequest {
  farm_id: number;
  measurement_date?: string;
  land_type: 'forest' | 'grassland' | 'cropland' | 'urban';
  management_practice?: string;
  start_date: string;
  end_date: string;
  run_monte_carlo?: boolean;
  monte_carlo_iterations?: number;
}

export interface CarbonStatistics {
  mean_carbon: number;
  std_carbon: number;
  mean_ndvi: number;
  std_ndvi: number;
  mean_confidence_score: number;
  overall_std_dev: number;
  min_ndvi: number;
  max_ndvi: number;
}

export interface CarbonMetadata {
  data_source: string;
  processing_timestamp: string;
  uncertainty_method: string;
  monte_carlo_iterations: number;
  methodology?: string;
}

export interface CarbonEstimate {
  estimate_id: number;
  farm_id: number;
  carbon_value: number;
  uncertainty: number;
  confidence_score: number;
  total_points: number;
  measurement_date: string;
  methodology: string;
  statistics: CarbonStatistics;
  metadata: CarbonMetadata;
  created_at: string;
}

export interface CarbonReport extends CarbonEstimate {
  farm_name: string;
  unit: string;
  land_type: string;
  compliance?: {
    ipcc_compliant: boolean;
    iso_14064_2_compliant: boolean;
    unfccc_vcs_eligible: boolean;
  };
}

/**
 * Calculate carbon estimate for a farm
 */
export async function estimateCarbon(
  data: CarbonEstimateRequest
): Promise<CarbonEstimate> {
  const response = await axiosInstance.post<CarbonEstimate>('/api/v1/carbon/estimate', data);
  return response.data;
}

/**
 * Get carbon estimates for a farm
 */
export async function getCarbonEstimates(
  farmId: number,
  params?: { skip?: number; limit?: number; start_date?: string; end_date?: string }
) {
  const response = await axiosInstance.get<{
    items: CarbonEstimate[];
    total: number;
    skip: number;
    limit: number;
  }>(`/api/v1/carbon/estimate/${farmId}`, { params });
  return response.data;
}

/**
 * Get detailed carbon report
 */
export async function getCarbonReport(estimateId: number): Promise<CarbonReport> {
  const response = await axiosInstance.get<CarbonReport>(`/api/v1/carbon/report/${estimateId}`);
  return response.data;
}

/**
 * Get latest carbon estimate for a farm
 */
export async function getLatestCarbonEstimate(farmId: number): Promise<CarbonEstimate | null> {
  try {
    const response = await getCarbonEstimates(farmId, { limit: 1 });
    return response.items[0] || null;
  } catch {
    return null;
  }
}
