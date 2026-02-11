/**
 * Dashboard-specific API service functions
 */

import axiosInstance from '@/lib/api-client';
import type { KPIData, AlertData } from '@/types/dashboard';
import type { DateRangeFilter } from '@/types/api';

const DASHBOARD_ENDPOINT = '/api/dashboard';

export const dashboardApi = {
  /**
   * Get KPI data with optional filters
   */
  getKPIs: async (filters?: DateRangeFilter): Promise<KPIData> => {
    const response = await axiosInstance.get<KPIData>(`${DASHBOARD_ENDPOINT}/kpis`, {
      params: filters,
    });
    return response.data;
  },

  /**
   * Get alerts
   */
  getAlerts: async (): Promise<AlertData[]> => {
    const response = await axiosInstance.get<AlertData[]>(`${DASHBOARD_ENDPOINT}/alerts`);
    return response.data;
  },
};
