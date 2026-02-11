/**
 * React Query hooks for Farm operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { farmsApi } from '@/lib/api/farms';
import type { FarmResponse, FarmCreate, FarmUpdate, FarmGeoJSON } from '@/types/farm';
import type { PaginationParams } from '@/types/api';

const FARMS_QUERY_KEY = ['farms'];

/**
 * Hook to fetch all farms with pagination
 */
export function useFarms(params?: PaginationParams) {
  return useQuery<FarmResponse[], Error>({
    queryKey: [...FARMS_QUERY_KEY, params],
    queryFn: () => farmsApi.getFarms(params),
  });
}

/**
 * Hook to fetch farms as GeoJSON
 */
export function useFarmsGeoJSON() {
  return useQuery<FarmGeoJSON[], Error>({
    queryKey: [...FARMS_QUERY_KEY, 'geojson'],
    queryFn: () => farmsApi.getFarmsGeoJSON(),
  });
}

/**
 * Hook to fetch a single farm
 */
export function useFarm(farmId: number | null) {
  return useQuery<FarmResponse, Error>({
    queryKey: [...FARMS_QUERY_KEY, farmId],
    queryFn: () => farmsApi.getFarm(farmId!),
    enabled: !!farmId,
  });
}

/**
 * Hook to create a new farm
 */
export function useCreateFarm() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: FarmCreate) => farmsApi.createFarm(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FARMS_QUERY_KEY });
    },
  });
}

/**
 * Hook to update a farm
 */
export function useUpdateFarm() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ farmId, data }: { farmId: number; data: FarmUpdate }) =>
      farmsApi.updateFarm(farmId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FARMS_QUERY_KEY });
    },
  });
}

/**
 * Hook to delete a farm
 */
export function useDeleteFarm() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (farmId: number) => farmsApi.deleteFarm(farmId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FARMS_QUERY_KEY });
    },
  });
}
