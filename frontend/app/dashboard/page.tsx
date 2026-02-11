'use client';

import { useState } from 'react';
import PortfolioView from '@/components/PortfolioView';
import KPICards from '@/components/KPICards';
import InteractiveMaps from '@/components/InteractiveMaps';
import TimeControls from '@/components/TimeControls';

export default function Dashboard() {
  const [selectedDateRange, setSelectedDateRange] = useState({
    start: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000),
    end: new Date(),
  });

  const [selectedLocation, setSelectedLocation] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b bg-white shadow-sm">
        <div className="mx-auto max-w-7xl px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Carbon Dashboard</h1>
          <p className="mt-1 text-gray-600">
            Monitor and analyze your carbon credit portfolio
          </p>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 py-8">
        {/* Time Controls */}
        <div className="mb-8">
          <TimeControls onRangeChange={setSelectedDateRange} />
        </div>

        {/* KPI Cards */}
        <div className="mb-8">
          <KPICards
            dateRange={selectedDateRange}
            locationFilter={selectedLocation}
          />
        </div>

        {/* Portfolio View */}
        <div className="mb-8">
          <PortfolioView
            dateRange={selectedDateRange}
            onSelectLocation={setSelectedLocation}
          />
        </div>

        {/* Interactive Maps */}
        <div className="mb-8">
          <InteractiveMaps
            selectedLocation={selectedLocation}
            dateRange={selectedDateRange}
          />
        </div>
      </div>
    </div>
  );
}
