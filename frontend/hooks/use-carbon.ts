/**
 * React Query hooks for Carbon operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { estimateCarbon, getCarbonEstimates, getCarbonReport } from '@/lib/api/carbon';
import type { CarbonEstimateRequest, CarbonEstimate, CarbonReport } from '@/lib/api/carbon';

const CARBON_QUERY_KEY = ['carbon'];

/**
 * Hook to fetch carbon estimates for a farm
 */
export function useCarbonEstimates(farmId: number | null) {
  return useQuery<{
    items: CarbonEstimate[];
    total: number;
    skip: number;
    limit: number;
  } | null, Error>({
    queryKey: [...CARBON_QUERY_KEY, 'estimates', farmId],
    queryFn: () => farmId ? getCarbonEstimates(farmId) : null,
    enabled: !!farmId,
  });
}

/**
 * Hook to fetch detailed carbon report
 */
export function useCarbonReport(estimateId: number | null) {
  return useQuery<CarbonReport, Error>({
    queryKey: [...CARBON_QUERY_KEY, 'report', estimateId],
    queryFn: () => estimateId ? getCarbonReport(estimateId) : Promise.reject(),
    enabled: !!estimateId,
  });
}

/**
 * Hook to calculate carbon for a farm
 */
export function useEstimateCarbon() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CarbonEstimateRequest) => estimateCarbon(request),
    onSuccess: (data: any) => {
      queryClient.invalidateQueries({ queryKey: [...CARBON_QUERY_KEY, 'estimates', data.farm_id] });
    },
  });
}
