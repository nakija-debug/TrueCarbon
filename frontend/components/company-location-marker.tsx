'use client';

import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

interface CompanyLocation {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  areaHa: number;
  carbonCredits: number;
  verificationStatus: 'Verified' | 'Pending' | 'At Risk';
}

interface CompanyLocationMarkerProps {
  locations: CompanyLocation[];
  onSelectLocation?: (id: string) => void;
}

// Custom marker icon colors based on verification status
const getMarkerColor = (status: 'Verified' | 'Pending' | 'At Risk') => {
  switch (status) {
    case 'Verified':
      return '#10b981'; // green
    case 'Pending':
      return '#f59e0b'; // amber
    case 'At Risk':
      return '#ef4444'; // red
    default:
      return '#6b7280'; // gray
  }
};

// Simpler marker implementation using default Leaflet divIcon
const createDivIcon = (color: string, text: string) => {
  return L.divIcon({
    html: `
      <div style="
        background-color: ${color};
        color: white;
        border: 2px solid white;
        border-radius: 50%;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        cursor: pointer;
      ">
        ${text}
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16],
    className: 'company-marker',
  });
};

export const CompanyLocationMarker: React.FC<CompanyLocationMarkerProps> = ({
  locations,
  onSelectLocation,
}) => {
  return (
    <>
      {locations.map((location, index) => (
        <Marker
          key={location.id}
          position={[location.latitude, location.longitude]}
          icon={createDivIcon(
            getMarkerColor(location.verificationStatus),
            (index + 1).toString()
          )}
          eventHandlers={{
            click: () => {
              if (onSelectLocation) {
                onSelectLocation(location.id);
              }
            },
          }}
        >
          <Popup>
            <div className="w-48">
              <h3 className="font-bold text-gray-900">{location.name}</h3>
              <div className="mt-2 space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Area:</span>
                  <span className="font-medium">{location.areaHa} ha</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Credits:</span>
                  <span className="font-medium">
                    {location.carbonCredits.toLocaleString()} tCO₂e
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span
                    className={`rounded-full px-2 py-1 text-xs font-medium ${
                      location.verificationStatus === 'Verified'
                        ? 'bg-emerald-100 text-emerald-800'
                        : location.verificationStatus === 'Pending'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {location.verificationStatus}
                  </span>
                </div>
              </div>
              <button
                onClick={() => onSelectLocation && onSelectLocation(location.id)}
                className="mt-3 w-full rounded bg-emerald-600 px-3 py-2 text-xs font-medium text-white hover:bg-emerald-700"
              >
                View Details
              </button>
            </div>
          </Popup>
        </Marker>
      ))}
    </>
  );
};

export default CompanyLocationMarker;
