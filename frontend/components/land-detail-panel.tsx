/**
 * Land Detail Panel Component - Shows detailed data for selected farm
 */

'use client';

import React from 'react';
import { useDashboardContext } from '@/lib/contexts/dashboard-context';
import { EmptyState } from '@/components/ui/empty-state';

export function LandDetailPanel() {
  const { selectedLand } = useDashboardContext();

  if (!selectedLand) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-8">
        <EmptyState
          title="No farm selected"
          description="Click on a farm on the map to view details"
        />
      </div>
    );
  }

  return (
    <div className="space-y-6 rounded-lg border border-gray-200 bg-white p-6">
      {/* Farm Info */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900">{selectedLand.name}</h3>
        <div className="mt-2 grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Area</p>
            <p className="text-lg font-semibold text-gray-900">{selectedLand.area_ha} ha</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Location</p>
            <p className="text-lg font-semibold text-gray-900">{selectedLand.location}</p>
          </div>
        </div>
      </div>

      {/* Carbon Chart - placeholder */}
    </div>
  );
}
