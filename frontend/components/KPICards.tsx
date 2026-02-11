'use client';

import React from 'react';
import { useKPIs } from '@/hooks/use-kpis';
import {
  GlobeAltIcon,
  CloudIcon,
  CheckCircleIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';

interface KPICardsProps {
  dateRange?: {
    start: Date;
    end: Date;
  };
  locationFilter?: string | null;
}

interface KPICard {
  title: string;
  value: string | number;
  subValue?: string;
  icon: any;
  color: string;
  description: string;
  trend?: 'positive' | 'negative';
}

const KPICards: React.FC<KPICardsProps> = ({ locationFilter }) => {
  const { data: kpiData, isLoading } = useKPIs({
    location: locationFilter || undefined,
  });

  if (isLoading || !kpiData) {
    return (
      <div className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-5">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="animate-pulse rounded-xl bg-white p-6 shadow">
            <div className="mb-4 h-4 w-1/2 rounded bg-gray-200"></div>
            <div className="h-8 w-3/4 rounded bg-gray-200"></div>
          </div>
        ))}
      </div>
    );
  }

  const cards: KPICard[] = [
    {
      title: 'Total Land Area',
      value: `${(kpiData.totalLandArea || 0).toLocaleString()} ha`,
      icon: GlobeAltIcon,
      color: 'bg-blue-500',
      description: '📍 Where is the land?',
    },
    {
      title: 'Carbon Credits',
      value: `${(kpiData.carbonGenerated || 0).toLocaleString()} tCO₂e`,
      subValue: `of ${(kpiData.totalCarbonCredits || 0).toLocaleString()} total`,
      icon: CloudIcon,
      color: 'bg-emerald-500',
      description: '🌿 How much carbon is being generated?',
    },
    {
      title: 'Active Projects',
      value: kpiData.activeProjects || 0,
      icon: ChartBarIcon,
      color: 'bg-purple-500',
      description: '📊 Project portfolio overview',
    },
    {
      title: 'Verified %',
      value: `${kpiData.verifiedPercent || 0}%`,
      icon: CheckCircleIcon,
      color:
        (kpiData.verifiedPercent || 0) >= 80 ? 'bg-green-500' : 'bg-yellow-500',
      description: '✅ Is the data verifiable?',
    },
    {
      title: 'Avg NDVI Δ',
      value:
        (kpiData.avgNDVIChange || 0) >= 0
          ? `+${kpiData.avgNDVIChange}`
          : kpiData.avgNDVIChange,
      icon: ChartBarIcon,
      color:
        (kpiData.avgNDVIChange || 0) >= 0 ? 'bg-emerald-500' : 'bg-red-500',
      description: '📈 Is vegetation improving or degrading?',
      trend: (kpiData.avgNDVIChange || 0) >= 0 ? 'positive' : 'negative',
    },
  ];

  return (
    <div className="mb-8">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">
          Carbon Credit Dashboard
        </h2>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-5">
        {cards.map((card, index) => (
          <div
            key={index}
            className="rounded-xl border border-gray-100 bg-white p-6 shadow-lg transition-shadow duration-300 hover:shadow-xl"
          >
            <div className="mb-4 flex items-center justify-between">
              <div
                className={`rounded-lg ${card.color} bg-opacity-10 p-3`}
              >
                <card.icon
                  className={`h-6 w-6 ${card.color.replace('bg-', 'text-')}`}
                />
              </div>
              <span className="rounded-full bg-gray-100 px-3 py-1 text-sm font-medium text-gray-500">
                {card.description}
              </span>
            </div>

            <h3 className="mb-1 text-sm font-medium text-gray-500">
              {card.title}
            </h3>
            <div className="flex items-end">
              <p className="text-3xl font-bold text-gray-900">{card.value}</p>
              {card.subValue && (
                <p className="mb-1 ml-2 text-sm text-gray-500">
                  / {card.subValue}
                </p>
              )}
            </div>

            {card.trend && (
              <div className="mt-4 flex items-center">
                <span
                  className={`text-sm font-medium ${
                    card.trend === 'positive' ? 'text-emerald-600' : 'text-red-600'
                  }`}
                >
                  {card.trend === 'positive' ? '▲ Improving' : '▼ Declining'}
                </span>
                <span className="ml-2 text-xs text-gray-500">
                  Since last quarter
                </span>
              </div>
            )}

            <div className="mt-4 border-t border-gray-100 pt-4">
              <p className="text-xs text-gray-500">
                Updated: Just now • Source: Sentinel-2
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default KPICards;
