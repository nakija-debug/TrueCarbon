/**
 * React Query hooks for KPI and Alert operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getKPIs, getAlerts, markAlertAsRead, dismissAlert } from '@/lib/api/kpis';
import type { KPIData, Alert, KPIFilters } from '@/lib/api/kpis';

const KPI_QUERY_KEY = ['kpis'];
const ALERTS_QUERY_KEY = ['alerts'];

/**
 * Hook to fetch KPI data with optional filters
 */
export function useKPIs(filters?: KPIFilters) {
  return useQuery<KPIData, Error>({
    queryKey: [...KPI_QUERY_KEY, filters],
    queryFn: () => getKPIs(filters),
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchInterval: 1000 * 60 * 5, // Refetch every 5 minutes
  });
}

/**
 * Hook to fetch alerts
 */
export function useAlerts(params?: { level?: string; type?: string; limit?: number }) {
  return useQuery<{ highPriority: Alert[]; all: Alert[] }, Error>({
    queryKey: [...ALERTS_QUERY_KEY, params],
    queryFn: () => getAlerts(params),
    staleTime: 1000 * 60, // 1 minute
    refetchInterval: 1000 * 60, // Refetch every minute
  });
}

/**
 * Hook to mark alert as read
 */
export function useMarkAlertAsRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (alertId: string) => markAlertAsRead(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ALERTS_QUERY_KEY });
    },
  });
}

/**
 * Hook to dismiss alert
 */
export function useDismissAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (alertId: string) => dismissAlert(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ALERTS_QUERY_KEY });
    },
  });
}
