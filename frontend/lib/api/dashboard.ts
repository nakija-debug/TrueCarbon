/**
 * Dashboard-specific API service functions
 */

import axiosInstance from '@/lib/api-client';
import type { KPIData, AlertData } from '@/types/dashboard';
import type { DateRangeFilter } from '@/types/api';

export const dashboardApi = {
  /**
   * Get KPI data with optional filters
   */
  getKPIs: async (filters?: DateRangeFilter): Promise<KPIData> => {
    const response = await axiosInstance.get<KPIData>('/api/v1/kpis', {
      params: filters,
    });
    return response.data;
  },

  /**
   * Get alerts
   */
  getAlerts: async (): Promise<AlertData[]> => {
    const response = await axiosInstance.get<AlertData[]>('/api/v1/alerts');
    return response.data;
  },
};
