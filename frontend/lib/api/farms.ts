/**
 * Farm API service functions
 */

import axiosInstance from '@/lib/api-client';
import type { FarmResponse, FarmCreate, FarmUpdate, FarmGeoJSON } from '@/types/farm';
import type { PaginationParams } from '@/types/api';

const FARMS_ENDPOINT = '/api/v1/farms';

export const farmsApi = {
  /**
   * Get all farms with pagination
   */
  getFarms: async (params?: PaginationParams): Promise<FarmResponse[]> => {
    const response = await axiosInstance.get<FarmResponse[]>(FARMS_ENDPOINT, { params });
    return response.data;
  },

  /**
   * Get farms as GeoJSON features
   */
  getFarmsGeoJSON: async (): Promise<FarmGeoJSON[]> => {
    const response = await axiosInstance.get<FarmGeoJSON[]>(`${FARMS_ENDPOINT}/geojson`);
    return response.data;
  },

  /**
   * Get single farm by ID
   */
  getFarm: async (farmId: number): Promise<FarmResponse> => {
    const response = await axiosInstance.get<FarmResponse>(`${FARMS_ENDPOINT}/${farmId}`);
    return response.data;
  },

  /**
   * Create new farm
   */
  createFarm: async (data: FarmCreate): Promise<FarmResponse> => {
    const response = await axiosInstance.post<FarmResponse>(FARMS_ENDPOINT, data);
    return response.data;
  },

  /**
   * Update existing farm
   */
  updateFarm: async (farmId: number, data: FarmUpdate): Promise<FarmResponse> => {
    const response = await axiosInstance.put<FarmResponse>(`${FARMS_ENDPOINT}/${farmId}`, data);
    return response.data;
  },

  /**
   * Delete farm
   */
  deleteFarm: async (farmId: number): Promise<void> => {
    await axiosInstance.delete(`${FARMS_ENDPOINT}/${farmId}`);
  },
};
