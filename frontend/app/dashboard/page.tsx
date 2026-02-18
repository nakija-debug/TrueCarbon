'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import PortfolioView from '@/components/PortfolioView';
import KPICards from '@/components/KPICards';
import TimeControls from '@/components/TimeControls';

const InteractiveMaps = dynamic(() => import('@/components/InteractiveMaps'), {
  ssr: false,
  loading: () => <div className="h-[600px] w-full animate-pulse rounded-xl bg-gray-200" />,
});

export default function Dashboard() {
  const [selectedDateRange, setSelectedDateRange] = useState({
    start: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000),
    end: new Date(),
  });

  const [selectedLocation, setSelectedLocation] = useState<string | null>(null);
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load user data from localStorage
  useEffect(() => {
    const stored = localStorage.getItem('dashboardData');
    if (stored) {
      try {
        const data = JSON.parse(stored);
        setDashboardData(data);
        console.log('Loaded dashboard data:', data);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      }
    }
    setIsLoading(false);
  }, []);

  // Generate company locations from user's farms
  const getCompanyLocations = () => {
    if (!dashboardData?.farms || dashboardData.farms.length === 0) {
      return [
        {
          id: '1',
          name: 'North Property',
          latitude: -0.95,
          longitude: 36.8,
          areaHa: 250,
          carbonCredits: 1200,
          verificationStatus: 'Verified' as const,
        },
        {
          id: '2',
          name: 'South Farm',
          latitude: -0.7,
          longitude: 37.175,
          areaHa: 180,
          carbonCredits: 950,
          verificationStatus: 'Pending' as const,
        },
        {
          id: '3',
          name: 'East Agricultural',
          latitude: -0.3,
          longitude: 36.125,
          areaHa: 320,
          carbonCredits: 1650,
          verificationStatus: 'Verified' as const,
        },
      ];
    }

    return dashboardData.farms.map((farm: any, idx: number) => ({
      id: `farm-${idx}`,
      name: farm.name || `Farm ${idx + 1}`,
      latitude: farm.latitude || -0.95 + idx * 0.3,
      longitude: farm.longitude || 36.8 + idx * 0.3,
      areaHa: farm.area_ha || 250,
      carbonCredits: farm.promised_credits || 1200,
      verificationStatus: 'Pending' as const,
    }));
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-b-2 border-emerald-500"></div>
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  const companyLocations = getCompanyLocations();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b bg-white shadow-sm">
        <div className="mx-auto max-w-7xl px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Carbon Dashboard</h1>
              {dashboardData?.company && (
                <p className="mt-1 text-gray-600">
                  Company: <span className="font-semibold">{dashboardData.company.companyName}</span> • 
                  Region: <span className="font-semibold">{dashboardData.company.region}, {dashboardData.company.country}</span>
                </p>
              )}
              {dashboardData?.userName && (
                <p className="mt-1 text-sm text-gray-500">
                  Welcome, {dashboardData.userName}
                </p>
              )}
              <p className="mt-3 text-gray-600">
                Monitor and analyze your carbon credit portfolio
              </p>
            </div>
            {dashboardData?.farms && dashboardData.farms.length > 0 && (
              <div className="text-right">
                <div className="text-2xl font-bold text-emerald-600">
                  {dashboardData.farms.length}
                </div>
                <p className="text-sm text-gray-600">Farm{dashboardData.farms.length !== 1 ? 's' : ''} Created</p>
                {dashboardData.farms[0].area_ha && (
                  <p className="text-sm text-gray-600">
                    {dashboardData.farms.reduce((sum: number, f: any) => sum + (f.area_ha || 0), 0).toFixed(2)} ha Total
                  </p>
                )}
              </div>
            )}
          </div>
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
            companyLocations={companyLocations}
            onSelectLocation={setSelectedLocation}
          />
        </div>
      </div>
    </div>
  );
}
