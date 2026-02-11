/**
 * NDVI API service functions
 */

import axiosInstance from '@/lib/api-client';
import type { NDVIRequest, NDVIResponse } from '@/types/ndvi';

const NDVI_ENDPOINT = '/api/v1/ndvi';

export const ndviApi = {
  /**
   * Calculate NDVI for a farm
   */
  calculateNDVI: async (request: NDVIRequest): Promise<NDVIResponse> => {
    const response = await axiosInstance.post<NDVIResponse>(`${NDVI_ENDPOINT}/calculate`, request);
    return response.data;
  },

  /**
   * Get NDVI time series for a farm
   */
  getNDVITimeSeries: async (farmId: number): Promise<NDVIResponse> => {
    const response = await axiosInstance.get<NDVIResponse>(`${NDVI_ENDPOINT}/${farmId}`);
    return response.data;
  },
};
