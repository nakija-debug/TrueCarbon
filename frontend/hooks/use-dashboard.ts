/**
 * React Query hooks for Dashboard operations
 */

import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '@/lib/api/dashboard';
import type { KPIData, AlertData } from '@/types/dashboard';
import type { DateRangeFilter } from '@/types/api';

const DASHBOARD_QUERY_KEY = ['dashboard'];

/**
 * Hook to fetch KPI data
 */
export function useKPIs(filters?: DateRangeFilter) {
  return useQuery<KPIData, Error>({
    queryKey: [...DASHBOARD_QUERY_KEY, 'kpis', filters],
    queryFn: () => dashboardApi.getKPIs(filters),
  });
}

/**
 * Hook to fetch alerts
 */
export function useAlerts() {
  return useQuery<AlertData[], Error>({
    queryKey: [...DASHBOARD_QUERY_KEY, 'alerts'],
    queryFn: () => dashboardApi.getAlerts(),
    refetchInterval: 1000 * 60 * 5, // Refetch every 5 minutes
  });
}
