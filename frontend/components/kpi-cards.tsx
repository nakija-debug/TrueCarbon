/**
 * KPI Cards Component - Displays key performance indicators
 */

'use client';

import React from 'react';
import { useKPIs } from '@/hooks/use-dashboard';
import { ErrorMessage } from '@/components/ui/error-message';
import { CardSkeleton } from '@/components/ui/skeleton';
import { useDashboardContext } from '@/lib/contexts/dashboard-context';

export function KPICards() {
  const { dateRange } = useDashboardContext();
  const { data: kpis, isLoading, error, refetch } = useKPIs({
    startDate: dateRange.startDate,
    endDate: dateRange.endDate,
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <CardSkeleton count={5} />
      </div>
    );
  }

  if (error) {
    return <ErrorMessage message="Failed to load KPI data" onRetry={() => refetch()} />;
  }

  if (!kpis) {
    return null;
  }

  const metrics = [
    {
      label: 'Total Land Area',
      value: `${kpis.totalLandArea.toLocaleString()}`,
      unit: 'hectares',
      color: 'bg-blue-50 border-blue-200',
    },
    {
      label: 'Carbon Generated',
      value: `${kpis.carbonGenerated.toLocaleString()}`,
      unit: 'tonnes CO2',
      color: 'bg-green-50 border-green-200',
    },
    {
      label: 'Active Projects',
      value: `${kpis.activeProjects}`,
      unit: 'projects',
      color: 'bg-yellow-50 border-yellow-200',
    },
    {
      label: 'Verified',
      value: `${kpis.verifiedPercent.toFixed(1)}%`,
      unit: 'verified',
      color: 'bg-purple-50 border-purple-200',
    },
    {
      label: 'Avg NDVI Change',
      value: `${(kpis.avgNDVIChange * 100).toFixed(1)}%`,
      unit: 'change',
      color: 'bg-orange-50 border-orange-200',
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
      {metrics.map((metric) => (
        <div
          key={metric.label}
          className={`rounded-lg border-2 ${metric.color} p-6 shadow-sm`}
        >
          <p className="text-sm font-medium text-gray-600">{metric.label}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{metric.value}</p>
          <p className="mt-1 text-xs text-gray-500">{metric.unit}</p>
        </div>
      ))}
    </div>
  );
}
