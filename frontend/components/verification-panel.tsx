/**
 * Verification Panel Component - Shows carbon verification and confidence metrics
 */

'use client';

import React from 'react';
import { useDashboardContext } from '@/lib/contexts/dashboard-context';
import { EmptyState } from '@/components/ui/empty-state';

export function VerificationPanel() {
  const { selectedLand } = useDashboardContext();

  if (!selectedLand) {
    return (
      <EmptyState
        title="No farm selected"
        description="Click on a farm to view verification details"
      />
    );
  }

  return (
    <div className="space-y-4 rounded-lg border border-gray-200 bg-white p-6">
      <h3 className="text-lg font-semibold text-gray-900">Verification Status</h3>
      <VerificationDetails />
    </div>
  );
}

function VerificationDetails() {
  return null;
}
