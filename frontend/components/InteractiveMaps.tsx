'use client';

import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, ZoomControl, ScaleControl } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in Leaflet with Next.js
const fixLeafletIcons = () => {
  // @ts-ignore
  delete L.Icon.Default.prototype._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  });
};

interface InteractiveMapsProps {
  selectedLocation?: string | null;
  dateRange?: {
    start: Date;
    end: Date;
  };
}

interface LandProperty {
  id: string;
  name: string;
  areaHa: number;
  ndviCurrent: number;
  carbonCreditsGenerated: number;
  verificationStatus: 'Verified' | 'Pending' | 'At Risk';
}

const InteractiveMaps: React.FC<InteractiveMapsProps> = ({
  selectedLocation,
  dateRange,
}) => {
  const [activeLayer, setActiveLayer] = useState<'ndvi' | 'parcels' | 'carbon'>('ndvi');
  const [hoveredLand, setHoveredLand] = useState<LandProperty | null>(null);
  const [landsData, setLandsData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fixLeafletIcons();
  }, []);

  // Helper for NDVI coloring
  const getNDVIColor = (ndvi: number) => {
    if (ndvi >= 1.0) return '#065f46';
    if (ndvi >= 0.8) return '#10b981';
    if (ndvi >= 0.6) return '#84cc16';
    if (ndvi >= 0.3) return '#f59e0b';
    return '#ef4444';
  };

  // Helper for Status coloring
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Verified': return '#10b981';
      case 'Pending': return '#f59e0b';
      case 'At Risk': return '#ef4444';
      default: return '#6b7280';
    }
  };

  // Style function for GeoJSON
  const getFeatureStyle = (feature: any) => {
    const props = feature.properties;

    if (activeLayer === 'ndvi') {
      return {
        fillColor: getNDVIColor(props.ndviCurrent || 0),
        fillOpacity: 0.8,
        color: '#1f2937',
        weight: 1,
      };
    } else if (activeLayer === 'parcels') {
      return {
        fillColor: getStatusColor(props.verificationStatus || ''),
        fillOpacity: 0.7,
        color: '#1f2937',
        weight: 2,
      };
    } else { // carbon
      return {
        fillColor: getStatusColor(props.verificationStatus || ''),
        fillOpacity: 0.8,
        color: '#ffffff',
        weight: 2,
      };
    }
  };

  const onEachFeature = (feature: any, layer: L.Layer) => {
    layer.on({
      mouseover: (e) => {
        const l = e.target;
        l.setStyle({
          weight: 3,
          fillOpacity: 0.9,
        });
        setHoveredLand(feature.properties);
      },
      mouseout: (e) => {
        const l = e.target;
        l.setStyle(getFeatureStyle(feature));
        setHoveredLand(null);
      },
      click: (e) => {
        console.log('Land selected:', feature.properties);
      }
    });
  };

  useEffect(() => {
    const loadLands = async () => {
      try {
        setIsLoading(true);
        const params = new URLSearchParams();
        if (selectedLocation) {
          params.append('location', selectedLocation);
        }
        if (dateRange) {
          params.append('start_date', dateRange.start.toISOString());
          params.append('end_date', dateRange.end.toISOString());
        }

        const response = await fetch(`/api/v1/farms?${params.toString()}`);
        if (response.ok) {
          const data = await response.json();
          // Note: Backend returns data differently sometimes, adjust if needed
          setLandsData(data.geojson || {
            type: 'FeatureCollection',
            features: [],
          });
        }
      } catch (error) {
        console.error('Failed to load lands data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadLands();
  }, [selectedLocation, dateRange]);

  if (isLoading || !landsData) {
    return (
      <div className="flex h-[600px] items-center justify-center rounded-xl bg-white p-8 shadow-lg">
        <div className="text-center">
          <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-b-2 border-emerald-500"></div>
          <p className="text-gray-600">Loading satellite data...</p>
          <p className="mt-2 text-sm text-gray-500">
            Source: Sentinel-2 • Processing NDVI layers
          </p>
        </div>
      </div>
    );
  }

  const formatDate = (date?: Date) => {
    return date ? date.toLocaleDateString() : 'Unknown';
  };

  return (
    <div className="mb-8 rounded-xl bg-white p-6 shadow-lg">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">
            Interactive Monitoring Map
          </h2>
          <p className="text-gray-600">
            Click land parcels for detailed analysis • Hover for quick summary
          </p>
        </div>

        <div className="flex space-x-2">
          <button
            onClick={() => setActiveLayer('ndvi')}
            className={`rounded-lg px-4 py-2 font-medium ${activeLayer === 'ndvi'
                ? 'border border-emerald-300 bg-emerald-100 text-emerald-700'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
          >
            NDVI Heatmap
          </button>
          <button
            onClick={() => setActiveLayer('parcels')}
            className={`rounded-lg px-4 py-2 font-medium ${activeLayer === 'parcels'
                ? 'border border-blue-300 bg-blue-100 text-blue-700'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
          >
            Land Parcels
          </button>
          <button
            onClick={() => setActiveLayer('carbon')}
            className={`rounded-lg px-4 py-2 font-medium ${activeLayer === 'carbon'
                ? 'border border-purple-300 bg-purple-100 text-purple-700'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
          >
            Carbon Credits
          </button>
        </div>
      </div>

      <div className="relative overflow-hidden rounded-lg border border-gray-200">
        {hoveredLand && (
          <div className="absolute left-6 top-6 z-[1000] rounded-lg border border-gray-200 bg-white p-4 shadow-lg pointer-events-none">
            <h4 className="font-bold text-gray-900">{hoveredLand.name}</h4>
            <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-gray-500">Area:</span>
                <span className="ml-2 font-medium">{hoveredLand.areaHa} ha</span>
              </div>
              <div>
                <span className="text-gray-500">NDVI:</span>
                <span className="ml-2 font-medium">{hoveredLand.ndviCurrent}</span>
              </div>
              <div>
                <span className="text-gray-500">Credits:</span>
                <span className="ml-2 font-medium">
                  {hoveredLand.carbonCreditsGenerated.toLocaleString()} tCO₂e
                </span>
              </div>
              <div>
                <span className="text-gray-500">Status:</span>
                <span
                  className={`ml-2 inline-block rounded-full px-2 py-1 text-xs font-medium ${hoveredLand.verificationStatus === 'Verified'
                      ? 'bg-emerald-100 text-emerald-800'
                      : hoveredLand.verificationStatus === 'Pending'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                >
                  {hoveredLand.verificationStatus}
                </span>
              </div>
            </div>
          </div>
        )}

        <div style={{ height: '500px' }}>
          <MapContainer
            center={[0, 0]}
            zoom={2}
            scrollWheelZoom={true}
            style={{ height: '100%', width: '100%' }}
            zoomControl={false}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <ZoomControl position="top-right" />
            <ScaleControl position="bottomleft" />

            {landsData && landsData.features && (
              <GeoJSON
                key={`${activeLayer}-${landsData.features.length}`}
                data={landsData}
                style={getFeatureStyle}
                onEachFeature={onEachFeature}
              />
            )}

            <div className="absolute bottom-4 left-4 z-[1000] rounded-lg border border-gray-200 bg-white p-4 shadow">
              <h4 className="mb-2 text-sm font-bold">
                {activeLayer === 'ndvi'
                  ? 'NDVI Scale'
                  : activeLayer === 'parcels'
                    ? 'Verification Status'
                    : 'Carbon Status'}
              </h4>
              {activeLayer === 'ndvi' && (
                <div className="flex space-x-2">
                  <div className="flex flex-col items-center">
                    <div className="h-4 w-6 bg-[#ef4444]"></div>
                    <span className="text-[10px]">0</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <div className="h-4 w-6 bg-[#f59e0b]"></div>
                    <span className="text-[10px]">0.3</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <div className="h-4 w-6 bg-[#84cc16]"></div>
                    <span className="text-[10px]">0.6</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <div className="h-4 w-6 bg-[#10b981]"></div>
                    <span className="text-[10px]">0.8</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <div className="h-4 w-6 bg-[#065f46]"></div>
                    <span className="text-[10px]">1.0</span>
                  </div>
                </div>
              )}
              {activeLayer === 'parcels' && (
                <div className="space-y-2">
                  <div className="flex items-center">
                    <div className="mr-2 h-3 w-3 rounded bg-[#10b981]"></div>
                    <span className="text-xs">Verified</span>
                  </div>
                  <div className="flex items-center">
                    <div className="mr-2 h-3 w-3 rounded bg-[#f59e0b]"></div>
                    <span className="text-xs">Pending</span>
                  </div>
                  <div className="flex items-center">
                    <div className="mr-2 h-3 w-3 rounded bg-[#ef4444]"></div>
                    <span className="text-xs">At Risk</span>
                  </div>
                </div>
              )}
            </div>

            <div className="absolute right-4 top-16 z-[1000] rounded-lg bg-white bg-opacity-90 p-3 text-sm border border-gray-200 shadow-sm">
              <p className="font-medium text-gray-600">Data Sources:</p>
              <ul className="mt-1 text-xs text-gray-500">
                <li>• Boundaries: OpenStreetMap</li>
                <li>• NDVI: Sentinel-2</li>
                <li>• Status: Verified Daily</li>
              </ul>
            </div>
          </MapContainer>
        </div>
      </div>

      <div className="mt-4 text-sm text-gray-500">
        <p>
          <span className="font-medium">Time Range:</span>{' '}
          {dateRange ? `${formatDate(dateRange.start)} - ${formatDate(dateRange.end)}` : 'All time'}{' '}
          •{' '}
          <span className="ml-4 font-medium">Lands Displayed:</span>{' '}
          {landsData?.features?.length || 0} •
          <span className="ml-4 font-medium">Map Engine:</span> Leaflet + OSM
        </p>
      </div>
    </div>
  );
};

export default InteractiveMaps;
