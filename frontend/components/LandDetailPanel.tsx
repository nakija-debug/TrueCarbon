'use client';

import React from 'react';

interface LandDetailPanelProps {
  landId?: string | null;
  onClose?: () => void;
}

interface LandDetail {
  id: string;
  name: string;
  areaHa: number;
  location: string;
  ndviValues: number[];
  carbonEstimate: number;
  verificationStatus: string;
  lastUpdated: string;
}

const LandDetailPanel: React.FC<LandDetailPanelProps> = ({ landId, onClose }) => {
  const [landDetail] = React.useState<LandDetail | null>(
    landId
      ? {
          id: landId,
          name: 'Sample Land Property',
          areaHa: 250,
          location: 'North Region',
          ndviValues: [0.42, 0.45, 0.48, 0.50, 0.52],
          carbonEstimate: 1200,
          verificationStatus: 'Verified',
          lastUpdated: new Date().toISOString(),
        }
      : null
  );

  if (!landDetail) {
    return null;
  }

  return (
    <div className="rounded-xl bg-white p-6 shadow-lg">
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">{landDetail.name}</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        )}
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <p className="text-sm text-gray-600">Location</p>
          <p className="text-lg font-semibold text-gray-900">
            {landDetail.location}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Area</p>
          <p className="text-lg font-semibold text-gray-900">
            {landDetail.areaHa} hectares
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Carbon Estimate</p>
          <p className="text-lg font-semibold text-emerald-600">
            {landDetail.carbonEstimate.toLocaleString()} tCO₂e
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Verification Status</p>
          <p
            className={`text-lg font-semibold ${
              landDetail.verificationStatus === 'Verified'
                ? 'text-emerald-600'
                : 'text-yellow-600'
            }`}
          >
            {landDetail.verificationStatus}
          </p>
        </div>
      </div>

      <div className="mt-6 border-t border-gray-200 pt-6">
        <h3 className="mb-4 text-lg font-semibold text-gray-900">
          NDVI Time Series
        </h3>
        <div className="flex items-end gap-2">
          {landDetail.ndviValues.map((value, index) => (
            <div key={index} className="flex-1">
              <div
                className="relative mb-2 rounded-t bg-emerald-500 transition-all hover:bg-emerald-600"
                style={{ height: `${value * 100}px` }}
              ></div>
              <p className="text-center text-xs text-gray-600">T{index + 1}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6 text-xs text-gray-500">
        Last updated: {new Date(landDetail.lastUpdated).toLocaleDateString()}
      </div>
    </div>
  );
};

export default LandDetailPanel;
