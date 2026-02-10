import React, { useEffect, useState, useRef } from 'react';
import { Map, Source, Layer, NavigationControl, ScaleControl } from 'react-map-gl';
import { useDashboard } from '../context/DashboardContext';
import 'mapbox-gl/dist/mapbox-gl.css';

// BACKEND INTEGRATION POINT:
// Mapbox token from environment variables
// In production: Use organization Mapbox account
const MAPBOX_TOKEN = process.env.REACT_APP_MAPBOX_TOKEN || 'your_mapbox_token_here';

const InteractiveMap = () => {
  const { landsData, selectLand, dateRange } = useDashboard();
  const mapRef = useRef();
  const [viewState, setViewState] = useState({
    latitude: 0,
    longitude: 0,
    zoom: 1.5
  });
  const [activeLayer, setActiveLayer] = useState('ndvi'); // 'ndvi', 'parcels', 'carbon'
  const [hoveredLand, setHoveredLand] = useState(null);

  // Layer configurations
  const layers = {
    parcels: {
      id: 'land-parcels',
      type: 'fill',
      paint: {
        'fill-color': [
          'case',
          ['==', ['get', 'verificationStatus'], 'Verified'], '#10b981',
          ['==', ['get', 'verificationStatus'], 'Pending'], '#f59e0b',
          ['==', ['get', 'verificationStatus'], 'At Risk'], '#ef4444',
          '#6b7280'
        ],
        'fill-opacity': 0.7,
        'fill-outline-color': '#1f2937'
      }
    },
    ndvi: {
      id: 'ndvi-heatmap',
      type: 'fill',
      paint: {
        'fill-color': [
          'interpolate',
          ['linear'],
          ['get', 'ndviCurrent'],
          0, '#ef4444',    // Red for low NDVI
          0.3, '#f59e0b',  // Yellow for moderate
          0.6, '#84cc16',  // Lime for good
          0.8, '#10b981',  // Green for excellent
          1, '#065f46'     // Dark green for optimal
        ],
        'fill-opacity': 0.8
      }
    },
    carbon: {
      id: 'carbon-points',
      type: 'circle',
      paint: {
        'circle-radius': [
          'interpolate',
          ['linear'],
          ['get', 'carbonCreditsGenerated'],
          0, 5,
          5000, 10,
          20000, 20
        ],
        'circle-color': [
          'case',
          ['==', ['get', 'verificationStatus'], 'Verified'], '#10b981',
          ['==', ['get', 'verificationStatus'], 'Pending'], '#f59e0b',
          '#ef4444'
        ],
        'circle-opacity': 0.8,
        'circle-stroke-width': 2,
        'circle-stroke-color': '#ffffff'
      }
    }
  };

  // Handle land click
  const handleClick = (event) => {
    const features = mapRef.current?.queryRenderedFeatures(event.point);
    if (features && features.length > 0) {
      const landFeature = features.find(f => f.source === 'lands');
      if (landFeature) {
        selectLand(landFeature.properties);
        
        // BACKEND INTEGRATION POINT:
        // In production: Log analytics for audit trail
        // await api.logInteraction({
        //   type: 'LAND_CLICK',
        //   landId: landFeature.properties.id,
        //   timestamp: new Date().toISOString(),
        //   user: 'auditor'
        // });
      }
    }
  };

  // Handle hover
  const handleHover = (event) => {
    const features = mapRef.current?.queryRenderedFeatures(event.point);
    if (features && features.length > 0) {
      const landFeature = features.find(f => f.source === 'lands');
      setHoveredLand(landFeature?.properties || null);
    } else {
      setHoveredLand(null);
    }
  };

  if (!landsData) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8 h-[600px] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading satellite data...</p>
          <p className="text-sm text-gray-500 mt-2">
            {/* BACKEND INTEGRATION POINT:
            Show actual data source when loading */}
            Source: Sentinel-2 • Processing NDVI layers
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Interactive Monitoring Map</h2>
          <p className="text-gray-600">
            Click land parcels for detailed analysis • Hover for quick summary
          </p>
        </div>
        
        <div className="flex space-x-2">
          <button
            onClick={() => setActiveLayer('ndvi')}
            className={`px-4 py-2 rounded-lg font-medium ${
              activeLayer === 'ndvi'
                ? 'bg-emerald-100 text-emerald-700 border border-emerald-300'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            NDVI Heatmap
          </button>
          <button
            onClick={() => setActiveLayer('parcels')}
            className={`px-4 py-2 rounded-lg font-medium ${
              activeLayer === 'parcels'
                ? 'bg-blue-100 text-blue-700 border border-blue-300'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Land Parcels
          </button>
          <button
            onClick={() => setActiveLayer('carbon')}
            className={`px-4 py-2 rounded-lg font-medium ${
              activeLayer === 'carbon'
                ? 'bg-purple-100 text-purple-700 border border-purple-300'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Carbon Credits
          </button>
        </div>
      </div>

      {/* Hover Tooltip */}
      {hoveredLand && (
        <div className="absolute z-50 bg-white p-4 rounded-lg shadow-lg border border-gray-200"
             style={{ left: 20, top: 120 }}>
          <h4 className="font-bold text-gray-900">{hoveredLand.name}</h4>
          <div className="grid grid-cols-2 gap-2 mt-2 text-sm">
            <div>
              <span className="text-gray-500">Area:</span>
              <span className="font-medium ml-2">{hoveredLand.area_ha} ha</span>
            </div>
            <div>
              <span className="text-gray-500">NDVI:</span>
              <span className="font-medium ml-2">{hoveredLand.ndviCurrent}</span>
            </div>
            <div>
              <span className="text-gray-500">Credits:</span>
              <span className="font-medium ml-2">{hoveredLand.carbonCreditsGenerated.toLocaleString()} tCO₂e</span>
            </div>
            <div>
              <span className="text-gray-500">Status:</span>
              <span className={`font-medium ml-2 px-2 py-1 rounded-full text-xs ${
                hoveredLand.verificationStatus === 'Verified' ? 'bg-emerald-100 text-emerald-800' :
                hoveredLand.verificationStatus === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {hoveredLand.verificationStatus}
              </span>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Click for detailed time-series analysis
          </p>
        </div>
      )}

      {/* Map Container */}
      <div className="relative h-[500px] rounded-lg overflow-hidden border border-gray-200">
        <Map
          ref={mapRef}
          {...viewState}
          onMove={evt => setViewState(evt.viewState)}
          onClick={handleClick}
          onMouseMove={handleHover}
          mapStyle="mapbox://styles/mapbox/light-v11"
          mapboxAccessToken={MAPBOX_TOKEN}
          interactiveLayerIds={[layers[activeLayer].id]}
        >
          <NavigationControl position="top-right" />
          <ScaleControl />
          
          {/* BACKEND INTEGRATION POINT:
          GeoJSON source from /api/lands endpoint
          In production: Real-time satellite overlay integration */}
          <Source 
            id="lands" 
            type="geojson" 
            data={landsData}
            promoteId="id"
          >
            <Layer {...layers[activeLayer]} />
          </Source>

          {/* Legend */}
          <div className="absolute bottom-4 left-4 bg-white p-4 rounded-lg shadow border border-gray-200">
            <h4 className="font-bold text-sm mb-2">
              {activeLayer === 'ndvi' ? 'NDVI Scale' : 
               activeLayer === 'parcels' ? 'Verification Status' : 
               'Carbon Credits Size'}
            </h4>
            {activeLayer === 'ndvi' && (
              <div className="flex items-center space-x-2">
                <div className="flex flex-col">
                  <div className="h-4 w-6 bg-red-500"></div>
                  <span className="text-xs mt-1">0</span>
                </div>
                <div className="flex flex-col">
                  <div className="h-4 w-6 bg-yellow-500"></div>
                  <span className="text-xs mt-1">0.3</span>
                </div>
                <div className="flex flex-col">
                  <div className="h-4 w-6 bg-lime-500"></div>
                  <span className="text-xs mt-1">0.6</span>
                </div>
                <div className="flex flex-col">
                  <div className="h-4 w-6 bg-emerald-500"></div>
                  <span className="text-xs mt-1">0.8</span>
                </div>
                <div className="flex flex-col">
                  <div className="h-4 w-6 bg-green-900"></div>
                  <span className="text-xs mt-1">1.0</span>
                </div>
              </div>
            )}
            {activeLayer === 'parcels' && (
              <div className="space-y-2">
                <div className="flex items-center">
                  <div className="h-3 w-3 bg-emerald-500 rounded mr-2"></div>
                  <span className="text-xs">Verified</span>
                </div>
                <div className="flex items-center">
                  <div className="h-3 w-3 bg-yellow-500 rounded mr-2"></div>
                  <span className="text-xs">Pending</span>
                </div>
                <div className="flex items-center">
                  <div className="h-3 w-3 bg-red-500 rounded mr-2"></div>
                  <span className="text-xs">At Risk</span>
                </div>
              </div>
            )}
          </div>
        </Map>

        {/* Data Source Info */}
        <div className="absolute top-4 right-4 bg-white bg-opacity-90 p-3 rounded-lg text-sm">
          <p className="text-gray-600 font-medium">Data Sources:</p>
          <ul className="text-xs text-gray-500 mt-1">
            <li>• Land Boundaries: PostGIS</li>
            <li>• NDVI: Sentinel-2 (10m resolution)</li>
            <li>• Last Updated: Today</li>
            {/* BACKEND INTEGRATION POINT:
            Show actual satellite pass timestamps */}
          </ul>
        </div>
      </div>

      <div className="mt-4 text-sm text-gray-500">
        <p>
          {/* BACKEND INTEGRATION POINT:
          Real-time update status from satellite feeds */}
          <span className="font-medium">Time Range:</span> {dateRange} • 
          <span className="font-medium ml-4">Lands Displayed:</span> {landsData.features.length} • 
          <span className="font-medium ml-4">Satellite:</span> Sentinel-2
        </p>
      </div>
    </div>
  );
};

export default InteractiveMap;