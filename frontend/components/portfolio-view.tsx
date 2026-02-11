/**
 * Portfolio View Component - Shows overview of all farms
 */

'use client';

import React from 'react';
import { useFarms } from '@/hooks/use-farms';
import { ErrorMessage } from '@/components/ui/error-message';
import { EmptyState } from '@/components/ui/empty-state';
import { TableSkeleton } from '@/components/ui/skeleton';
import { useDashboardContext } from '@/lib/contexts/dashboard-context';

export function PortfolioView() {
  const { data: farms, isLoading, error, refetch } = useFarms();
  const { setSelectedLand } = useDashboardContext();

  if (isLoading) {
    return <TableSkeleton rows={5} columns={4} />;
  }

  if (error) {
    return <ErrorMessage message="Failed to load farms" onRetry={() => refetch()} />;
  }

  if (!farms || farms.length === 0) {
    return (
      <EmptyState
        title="No farms in portfolio"
        description="Start by adding your first farm to the system"
        actionLabel="Add Farm"
      />
    );
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Name
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Area (ha)
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Action
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {farms.map((farm) => (
            <tr
              key={farm.id}
              className="hover:bg-gray-50 cursor-pointer"
              onClick={() =>
                setSelectedLand({
                  id: farm.id,
                  name: farm.name,
                  area_ha: farm.area_ha,
                  location: farm.description || 'Unknown',
                  status: farm.is_active ? 'active' : 'inactive',
                })
              }
            >
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {farm.name}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {farm.area_ha.toLocaleString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium ${
                    farm.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {farm.is_active ? 'Active' : 'Inactive'}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                <button className="text-blue-600 hover:text-blue-900">View Details</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
