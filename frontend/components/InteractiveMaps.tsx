'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Map, Source, Layer, NavigationControl, ScaleControl } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

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

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || 'your_mapbox_token_here';

const InteractiveMaps: React.FC<InteractiveMapsProps> = ({
  selectedLocation,
  dateRange,
}) => {
  const mapRef = useRef<any>(null);
  const [viewState, setViewState] = useState({
    latitude: 0,
    longitude: 0,
    zoom: 1.5,
  });
  const [activeLayer, setActiveLayer] = useState<'ndvi' | 'parcels' | 'carbon'>(
    'ndvi'
  );
  const [hoveredLand, setHoveredLand] = useState<LandProperty | null>(null);
  const [landsData, setLandsData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  const layers = {
    parcels: {
      id: 'land-parcels',
      type: 'fill' as const,
      paint: {
        'fill-color': [
          'case',
          ['==', ['get', 'verificationStatus'], 'Verified'],
          '#10b981',
          ['==', ['get', 'verificationStatus'], 'Pending'],
          '#f59e0b',
          ['==', ['get', 'verificationStatus'], 'At Risk'],
          '#ef4444',
          '#6b7280',
        ],
        'fill-opacity': 0.7,
        'fill-outline-color': '#1f2937',
      },
    },
    ndvi: {
      id: 'ndvi-heatmap',
      type: 'fill' as const,
      paint: {
        'fill-color': [
          'interpolate',
          ['linear'],
          ['get', 'ndviCurrent'],
          0,
          '#ef4444',
          0.3,
          '#f59e0b',
          0.6,
          '#84cc16',
          0.8,
          '#10b981',
          1,
          '#065f46',
        ],
        'fill-opacity': 0.8,
      },
    },
    carbon: {
      id: 'carbon-points',
      type: 'circle' as const,
      paint: {
        'circle-radius': [
          'interpolate',
          ['linear'],
          ['get', 'carbonCreditsGenerated'],
          0,
          5,
          5000,
          10,
          20000,
          20,
        ],
        'circle-color': [
          'case',
          ['==', ['get', 'verificationStatus'], 'Verified'],
          '#10b981',
          ['==', ['get', 'verificationStatus'], 'Pending'],
          '#f59e0b',
          '#ef4444',
        ],
        'circle-opacity': 0.8,
        'circle-stroke-width': 2,
        'circle-stroke-color': '#ffffff',
      },
    },
  };

  const handleClick = (event: any) => {
    if (!mapRef.current) return;
    const features = mapRef.current.queryRenderedFeatures(event.point);
    if (features && features.length > 0) {
      const landFeature = features.find((f: any) => f.source === 'lands');
      if (landFeature) {
        console.log('Land selected:', landFeature.properties);
      }
    }
  };

  const handleHover = (event: any) => {
    if (!mapRef.current) return;
    const features = mapRef.current.queryRenderedFeatures(event.point);
    if (features && features.length > 0) {
      const landFeature = features.find((f: any) => f.source === 'lands');
      setHoveredLand(landFeature?.properties || null);
    } else {
      setHoveredLand(null);
    }
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

        const response = await fetch(`/api/farms?${params.toString()}`);
        if (response.ok) {
          const data = await response.json();
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
            className={`rounded-lg px-4 py-2 font-medium ${
              activeLayer === 'ndvi'
                ? 'border border-emerald-300 bg-emerald-100 text-emerald-700'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            NDVI Heatmap
          </button>
          <button
            onClick={() => setActiveLayer('parcels')}
            className={`rounded-lg px-4 py-2 font-medium ${
              activeLayer === 'parcels'
                ? 'border border-blue-300 bg-blue-100 text-blue-700'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Land Parcels
          </button>
          <button
            onClick={() => setActiveLayer('carbon')}
            className={`rounded-lg px-4 py-2 font-medium ${
              activeLayer === 'carbon'
                ? 'border border-purple-300 bg-purple-100 text-purple-700'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Carbon Credits
          </button>
        </div>
      </div>

      {hoveredLand && (
        <div className="absolute left-20 top-120 z-50 rounded-lg border border-gray-200 bg-white p-4 shadow-lg">
          <h4 className="font-bold text-gray-900">{hoveredLand.name}</h4>
          <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="text-gray-500">Area:</span>
              <span className="ml-2 font-medium">{hoveredLand.areaHa} ha</span>
            </div>
            <div>
              <span className="text-gray-500">NDVI:</span>
              <span className="ml-2 font-medium">
                {hoveredLand.ndviCurrent}
              </span>
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
                className={`ml-2 inline-block rounded-full px-2 py-1 text-xs font-medium ${
                  hoveredLand.verificationStatus === 'Verified'
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
          <p className="mt-2 text-xs text-gray-500">
            Click for detailed time-series analysis
          </p>
        </div>
      )}

      <div className="relative overflow-hidden rounded-lg border border-gray-200">
        <div style={{ height: '500px' }}>
          <Map
            ref={mapRef}
            {...viewState}
            onMove={(evt) => setViewState(evt.viewState)}
            onClick={handleClick}
            onMouseMove={handleHover}
            mapStyle="mapbox://styles/mapbox/light-v11"
            mapboxAccessToken={MAPBOX_TOKEN}
            interactiveLayerIds={[layers[activeLayer].id]}
          >
            <NavigationControl position="top-right" />
            <ScaleControl />

            {landsData && landsData.features && landsData.features.length > 0 && (
              <Source id="lands" type="geojson" data={landsData} promoteId="id">
                <Layer {...(layers[activeLayer] as any)} />
              </Source>
            )}

            <div className="absolute bottom-4 left-4 rounded-lg border border-gray-200 bg-white p-4 shadow">
              <h4 className="mb-2 text-sm font-bold">
                {activeLayer === 'ndvi'
                  ? 'NDVI Scale'
                  : activeLayer === 'parcels'
                    ? 'Verification Status'
                    : 'Carbon Credits Size'}
              </h4>
              {activeLayer === 'ndvi' && (
                <div className="flex space-x-2">
                  <div className="flex flex-col">
                    <div className="h-4 w-6 bg-red-500"></div>
                    <span className="text-xs">0</span>
                  </div>
                  <div className="flex flex-col">
                    <div className="h-4 w-6 bg-yellow-500"></div>
                    <span className="text-xs">0.3</span>
                  </div>
                  <div className="flex flex-col">
                    <div className="h-4 w-6 bg-lime-500"></div>
                    <span className="text-xs">0.6</span>
                  </div>
                  <div className="flex flex-col">
                    <div className="h-4 w-6 bg-emerald-500"></div>
                    <span className="text-xs">0.8</span>
                  </div>
                  <div className="flex flex-col">
                    <div className="h-4 w-6 bg-green-900"></div>
                    <span className="text-xs">1.0</span>
                  </div>
                </div>
              )}
              {activeLayer === 'parcels' && (
                <div className="space-y-2">
                  <div className="flex items-center">
                    <div className="mr-2 h-3 w-3 rounded bg-emerald-500"></div>
                    <span className="text-xs">Verified</span>
                  </div>
                  <div className="flex items-center">
                    <div className="mr-2 h-3 w-3 rounded bg-yellow-500"></div>
                    <span className="text-xs">Pending</span>
                  </div>
                  <div className="flex items-center">
                    <div className="mr-2 h-3 w-3 rounded bg-red-500"></div>
                    <span className="text-xs">At Risk</span>
                  </div>
                </div>
              )}
            </div>

            <div className="absolute right-4 top-4 rounded-lg bg-white bg-opacity-90 p-3 text-sm">
              <p className="font-medium text-gray-600">Data Sources:</p>
              <ul className="mt-1 text-xs text-gray-500">
                <li>• Land Boundaries: PostGIS</li>
                <li>• NDVI: Sentinel-2 (10m resolution)</li>
                <li>• Last Updated: Today</li>
              </ul>
            </div>
          </Map>
        </div>
      </div>

      <div className="mt-4 text-sm text-gray-500">
        <p>
          <span className="font-medium">Time Range:</span>{' '}
          {dateRange ? `${formatDate(dateRange.start)} - ${formatDate(dateRange.end)}` : 'All time'}{' '}
          •{' '}
          <span className="ml-4 font-medium">Lands Displayed:</span>{' '}
          {landsData?.features?.length || 0} • 
          <span className="ml-4 font-medium">Satellite:</span> Sentinel-2
        </p>
      </div>
    </div>
  );
};

export default InteractiveMaps;
