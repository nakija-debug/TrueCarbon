'use client';

import React from 'react';

interface PortfolioViewProps {
  dateRange?: {
    start: Date;
    end: Date;
  };
  onSelectLocation?: (location: string | null) => void;
}

interface Land {
  id: string;
  name: string;
  areaHa: number;
  carbonCredits: number;
  verificationStatus: 'Verified' | 'Pending' | 'At Risk';
  ndviTrend: number;
}

const PortfolioView: React.FC<PortfolioViewProps> = ({
  onSelectLocation,
}) => {
  const [lands] = React.useState<Land[]>([
    {
      id: '1',
      name: 'North Property',
      areaHa: 250,
      carbonCredits: 1200,
      verificationStatus: 'Verified',
      ndviTrend: 0.12,
    },
    {
      id: '2',
      name: 'South Farm',
      areaHa: 180,
      carbonCredits: 950,
      verificationStatus: 'Pending',
      ndviTrend: -0.05,
    },
    {
      id: '3',
      name: 'East Agricultural',
      areaHa: 320,
      carbonCredits: 1650,
      verificationStatus: 'Verified',
      ndviTrend: 0.18,
    },
  ]);

  return (
    <div className="mb-8 rounded-xl bg-white p-6 shadow-lg">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900">Portfolio Overview</h2>
        <p className="text-gray-600">
          Manage your land parcels and track carbon credit generation
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                Land Name
              </th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                Area (ha)
              </th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                Carbon Credits
              </th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                NDVI Trend
              </th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                Status
              </th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                Action
              </th>
            </tr>
          </thead>
          <tbody>
            {lands.map((land) => (
              <tr
                key={land.id}
                className="border-b border-gray-100 transition-colors hover:bg-gray-50"
              >
                <td className="px-4 py-3">
                  <div className="font-medium text-gray-900">{land.name}</div>
                </td>
                <td className="px-4 py-3 text-gray-600">{land.areaHa.toLocaleString()}</td>
                <td className="px-4 py-3 text-gray-600">
                  {land.carbonCredits.toLocaleString()} tCO₂e
                </td>
                <td className="px-4 py-3">
                  <div
                    className={`flex items-center text-sm font-medium ${
                      land.ndviTrend >= 0 ? 'text-emerald-600' : 'text-red-600'
                    }`}
                  >
                    {land.ndviTrend >= 0 ? '▲' : '▼'}
                    <span className="ml-1">{land.ndviTrend.toFixed(2)}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-block rounded-full px-3 py-1 text-xs font-medium ${
                      land.verificationStatus === 'Verified'
                        ? 'bg-emerald-100 text-emerald-800'
                        : land.verificationStatus === 'Pending'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {land.verificationStatus}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() =>
                      onSelectLocation && onSelectLocation(land.id)
                    }
                    className="text-sm font-medium text-emerald-600 hover:text-emerald-700"
                  >
                    View Details
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-6 border-t border-gray-200 pt-4">
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="rounded-lg bg-blue-50 p-4">
            <p className="text-gray-600">Total Portfolio</p>
            <p className="text-2xl font-bold text-blue-600">
              {lands.reduce((sum, land) => sum + land.areaHa, 0).toLocaleString()} ha
            </p>
          </div>
          <div className="rounded-lg bg-emerald-50 p-4">
            <p className="text-gray-600">Total Carbon Credits</p>
            <p className="text-2xl font-bold text-emerald-600">
              {lands
                .reduce((sum, land) => sum + land.carbonCredits, 0)
                .toLocaleString()}{' '}
              tCO₂e
            </p>
          </div>
          <div className="rounded-lg bg-purple-50 p-4">
            <p className="text-gray-600">Verified Projects</p>
            <p className="text-2xl font-bold text-purple-600">
              {lands.filter((l) => l.verificationStatus === 'Verified').length}/
              {lands.length}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PortfolioView;
