/**
 * React Query hooks for NDVI operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ndviApi } from '@/lib/api/ndvi';
import type { NDVIRequest, NDVIResponse } from '@/types/ndvi';

const NDVI_QUERY_KEY = ['ndvi'];

/**
 * Hook to fetch NDVI time series for a farm
 */
export function useNDVITimeSeries(farmId: number | null) {
  return useQuery<NDVIResponse, Error>({
    queryKey: [...NDVI_QUERY_KEY, 'timeseries', farmId],
    queryFn: () => ndviApi.getNDVITimeSeries(farmId!),
    enabled: !!farmId,
  });
}

/**
 * Hook to calculate NDVI for a farm
 */
export function useCalculateNDVI() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: NDVIRequest) => ndviApi.calculateNDVI(request),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: [...NDVI_QUERY_KEY, 'timeseries', data.farm_id] });
    },
  });
}
