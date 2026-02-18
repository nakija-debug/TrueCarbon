'use client';

import React, { useState, useEffect, useRef } from 'react';

// Types
interface FarmFormProps {
  companyName?: string;
  onSuccess?: (farmData?: any) => void;
}

interface DrawnPolygon {
  type: string;
  coordinates: number[][][];
}

export function FarmForm({ companyName = '', onSuccess }: FarmFormProps) {
  const [farmName, setFarmName] = useState('');
  const [promisedCredits, setPromisedCredits] = useState('');
  const [areaHa, setAreaHa] = useState('');
  const [isDrawing, setIsDrawing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [drawnPolygon, setDrawnPolygon] = useState<DrawnPolygon | null>(null);
  const [pendingPolygon, setPendingPolygon] = useState<DrawnPolygon | null>(null);
  const [pendingArea, setPendingArea] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [mapReady, setMapReady] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const [mapLayer, setMapLayer] = useState<'osm' | 'satellite'>('osm');

  const mapRef = useRef<any>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const drawnLayerRef = useRef<any>(null);
  const L = useRef<any>(null);

  // Set mounted flag
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Initialize map with dynamic imports
  useEffect(() => {
    if (!isMounted || !mapContainerRef.current || mapReady) return;

    const initMap = async () => {
      try {
        // Load CSS first
        if (!document.getElementById('leaflet-css')) {
          const link = document.createElement('link');
          link.id = 'leaflet-css';
          link.rel = 'stylesheet';
          link.href = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css';
          link.onload = () => {
            console.log('Leaflet CSS loaded');
          };
          document.head.appendChild(link);
        }

        // Give CSS time to load
        await new Promise(resolve => setTimeout(resolve, 500));

        // Dynamically import Leaflet only on client side
        const leaflet = await import('leaflet');
        L.current = leaflet.default;

        // Ensure container is visible and has dimensions
        if (!mapContainerRef.current || mapContainerRef.current.offsetWidth === 0) {
          throw new Error('Map container not properly sized');
        }

        // Create map centered on Kenya
        const map = L.current.map(mapContainerRef.current, {
          preferCanvas: true,
        }).setView([0, 34.8], 5);

        // Create layer groups
        const osmLayer = L.current.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '© OpenStreetMap contributors',
          maxZoom: 22,
        });

        const satelliteLayer = L.current.tileLayer(
          'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
          {
            attribution: 'Tiles &copy; Esri',
            maxZoom: 22,
          }
        );

        // Add OSM by default
        osmLayer.addTo(map);
        (map as any)._tileLayer = osmLayer;
        (map as any)._satelliteLayer = satelliteLayer;

        // Invalidate size to ensure map renders correctly
        setTimeout(() => {
          map.invalidateSize();
        }, 100);

        // Create feature group for drawn items
        const drawnLayer = new L.current.FeatureGroup();
        map.addLayer(drawnLayer);
        drawnLayerRef.current = drawnLayer;

        mapRef.current = map;
        setMapReady(true);
        setError('');

        console.log('Map initialized successfully');
      } catch (err) {
        console.error('Failed to initialize map:', err);
        setError('Failed to load map. Please refresh the page.');
        setMapReady(false);
      }
    };

    initMap();

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
        setMapReady(false);
      }
    };
  }, [isMounted]);

  // Calculate area from polygon
  const calculateArea = (polygon: DrawnPolygon): number => {
    if (!polygon || polygon.coordinates.length === 0) return 0;

    const coords = polygon.coordinates[0];
    if (coords.length < 3) return 0;

    let area = 0;
    for (let i = 0; i < coords.length - 1; i++) {
      const [x1, y1] = coords[i];
      const [x2, y2] = coords[i + 1];
      area += x1 * y2 - x2 * y1;
    }

    area = Math.abs(area) / 2;
    const kmSq = area * 111 * 111;
    const hectares = kmSq * 100;

    return hectares;
  };

  const drawingStateRef = useRef({
    isDrawingActive: false,
    coordinates: [] as number[][],
  });

  // Draw polygon on map
  const handleStartDrawing = async () => {
    console.log('handleStartDrawing called');
    console.log('mapRef.current:', !!mapRef.current);
    console.log('drawnLayerRef.current:', !!drawnLayerRef.current);
    console.log('L.current:', !!L.current);
    
    if (!mapRef.current || !drawnLayerRef.current || !L.current) {
      console.error('Map not ready for drawing');
      return;
    }

    console.log('Starting drawing mode');
    setIsDrawing(true);
    setError('');

    const map = mapRef.current;
    const drawnLayer = drawnLayerRef.current;
    const Leaflet = L.current;

    // Reset drawing state
    drawnLayer.clearLayers();
    setDrawnPolygon(null);
    drawingStateRef.current.coordinates = [];
    drawingStateRef.current.isDrawingActive = true;

    // Change cursor to crosshair
    if (mapContainerRef.current) {
      mapContainerRef.current.style.cursor = 'crosshair';
    }

    const onMapClick = (e: any) => {
      if (!drawingStateRef.current.isDrawingActive) return;

      const { lat, lng } = e.latlng;
      const coordinates = drawingStateRef.current.coordinates;
      coordinates.push([lng, lat]);

      console.log('Point added:', { lat, lng }, 'Total points:', coordinates.length);

      // Draw point marker
      Leaflet.circleMarker([lat, lng], {
        radius: 5,
        fill: true,
        color: '#3b82f6',
        fillColor: '#3b82f6',
        fillOpacity: 0.8,
        weight: 2,
      }).addTo(drawnLayer);

      // Draw line to previous point
      if (coordinates.length > 1) {
        const prevCoord = coordinates[coordinates.length - 2];
        Leaflet.polyline(
          [
            [prevCoord[1], prevCoord[0]],
            [lat, lng],
          ],
          {
            color: '#3b82f6',
            weight: 2,
            dashArray: '5, 5',
          }
        ).addTo(drawnLayer);
      }
    };

    const onDoubleClick = (e: any) => {
      e.originalEvent.preventDefault();
      e.originalEvent.stopPropagation();

      const coordinates = drawingStateRef.current.coordinates;

      if (coordinates.length >= 3) {
        console.log('Polygon completed with', coordinates.length, 'points');

        const closedCoords = [...coordinates, coordinates[0]];

        drawnLayer.clearLayers();

        // Draw completed polygon
        Leaflet.polygon(closedCoords.map((c) => [c[1], c[0]]), {
          color: '#22c55e',
          weight: 3,
          fill: true,
          fillColor: '#16a34a',
          fillOpacity: 0.3,
        }).addTo(drawnLayer);

        const polygon: DrawnPolygon = {
          type: 'Polygon',
          coordinates: [closedCoords],
        };

        // Set as pending - user must confirm
        setPendingPolygon(polygon);
        const calculatedArea = calculateArea(polygon);
        setPendingArea(calculatedArea.toFixed(2));

        // Clean up event listeners but keep drawing active for now
        drawingStateRef.current.isDrawingActive = false;
        map.off('click', onMapClick);
        map.off('dblclick', onDoubleClick);
        setIsDrawing(false);

        // Reset cursor
        if (mapContainerRef.current) {
          mapContainerRef.current.style.cursor = '';
        }
      } else {
        alert('Please add at least 3 points to create a polygon');
      }
    };

    // Attach event listeners
    map.on('click', onMapClick);
    map.on('dblclick', onDoubleClick);

    // Store for cleanup
    (map as any)._farmDrawing = { onMapClick, onDoubleClick };
  };

  // Toggle between OSM and Satellite layers
  const toggleMapLayer = (layer: 'osm' | 'satellite') => {
    if (!mapRef.current) return;

    const map = mapRef.current;
    const osmLayer = (map as any)._tileLayer;
    const satelliteLayer = (map as any)._satelliteLayer;

    if (layer === 'satellite') {
      if (osmLayer) map.removeLayer(osmLayer);
      if (satelliteLayer) map.addLayer(satelliteLayer);
      setMapLayer('satellite');
    } else {
      if (satelliteLayer) map.removeLayer(satelliteLayer);
      if (osmLayer) map.addLayer(osmLayer);
      setMapLayer('osm');
    }
  };

  // Confirm pending boundary
  const confirmBoundary = () => {
    console.log('🎯 Confirm Boundary clicked');
    console.log('pendingPolygon:', pendingPolygon);
    console.log('pendingArea:', pendingArea);
    if (pendingPolygon) {
      setDrawnPolygon(pendingPolygon);
      setAreaHa(pendingArea);
      setPendingPolygon(null);
      setPendingArea('');
      console.log('✅ Boundary confirmed and saved');
    }
  };

  // Clear drawing
  const handleClearDrawing = () => {
    console.log('Clearing drawing');
    
    if (mapRef.current) {
      const map = mapRef.current;
      // Remove any active drawing event listeners
      if ((map as any)._farmDrawing) {
        map.off('click', (map as any)._farmDrawing.onMapClick);
        map.off('dblclick', (map as any)._farmDrawing.onDoubleClick);
        delete (map as any)._farmDrawing;
      }
    }

    if (drawnLayerRef.current) {
      drawnLayerRef.current.clearLayers();
    }

    drawingStateRef.current.coordinates = [];
    drawingStateRef.current.isDrawingActive = false;
    setDrawnPolygon(null);
    setAreaHa('');
    setPendingPolygon(null);
    setPendingArea('');
    setIsDrawing(false);

    // Reset cursor
    if (mapContainerRef.current) {
      mapContainerRef.current.style.cursor = '';
    }
  };

  // Submit form
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate inputs
    if (!farmName.trim()) {
      setError('Farm name is required');
      return;
    }
    if (!drawnPolygon) {
      setError('Please draw a polygon on the map to define farm boundary');
      return;
    }
    if (!areaHa) {
      setError('Farm area could not be calculated');
      return;
    }
    if (!promisedCredits || parseFloat(promisedCredits) <= 0) {
      setError('Promised carbon credits must be greater than 0');
      return;
    }

    setIsSubmitting(true);

    try {
      const token = localStorage.getItem('authToken');

      const payload = {
        name: farmName.trim(),
        description: `Farm with promised ${promisedCredits} carbon credits`,
        geometry: drawnPolygon,
        area_ha: parseFloat(areaHa),
        promised_credits: parseFloat(promisedCredits),
      };

      console.log('Farm payload:', payload);

      // Try backend request if token available
      if (token) {
        try {
          const response = await fetch('/api/v1/farms', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(payload),
          });

          if (response.ok) {
            const farm = await response.json();
            console.log('Farm created successfully:', farm);

            setSuccessMsg(
              `Farm "${farmName}" created successfully! Satellite data will be fetched soon.`
            );

            // Reset form
            setTimeout(() => {
              const farmDataToPass = {
                name: farmName,
                geometry: drawnPolygon,
                area_ha: parseFloat(areaHa),
                promised_credits: parseFloat(promisedCredits),
                description: `Farm with promised ${promisedCredits} carbon credits`,
                created_at: new Date().toISOString(),
              };
              
              console.log('🚀 About to call onSuccess with:', farmDataToPass);
              
              setFarmName('');
              setPromisedCredits('');
              setAreaHa('');
              handleClearDrawing();
              setSuccessMsg('');

              // Call callback with farm data
              if (onSuccess) {
                console.log('✅ Calling onSuccess callback');
                onSuccess(farmDataToPass);
              } else {
                console.log('❌ onSuccess callback not provided!');
              }
            }, 2000);
            return;
          }
        } catch (apiErr) {
          console.warn('Backend unavailable, using demo mode:', apiErr);
        }
      }

      // Demo mode - backend not available, proceed anyway
      console.log('Using demo mode for farm creation');
      console.log('📋 Form Values at submission:', { farmName, areaHa, promisedCredits, drawnPolygon });
      setSuccessMsg(
        `Farm "${farmName}" created successfully! (Demo Mode) Satellite data will be fetched soon.`
      );

      // Reset form
      setTimeout(() => {
        const farmDataToPass = {
          name: farmName,
          geometry: drawnPolygon,
          area_ha: parseFloat(areaHa),
          promised_credits: parseFloat(promisedCredits),
          description: `Farm with promised ${promisedCredits} carbon credits`,
          created_at: new Date().toISOString(),
        };
        
        console.log('🚀 About to call onSuccess with:', farmDataToPass);
        
        setFarmName('');
        setPromisedCredits('');
        setAreaHa('');
        handleClearDrawing();
        setSuccessMsg('');

        // Call callback with farm data
        if (onSuccess) {
          console.log('✅ Calling onSuccess callback');
          onSuccess(farmDataToPass);
        } else {
          console.log('❌ onSuccess callback not provided!');
        }
      }, 2000);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create farm');
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '20px' }}>
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
      <div
        style={{
          background: '#f8f9fa',
          padding: '30px',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}
      >
        <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '10px' }}>
          {companyName ? `${companyName} - Add Farm Location & Details` : 'Add Farm Location & Details'}
        </h2>
        <p
          style={{
            color: '#666',
            marginBottom: '30px',
            fontSize: '14px',
          }}
        >
          Draw your farm boundary on the map, provide promised carbon credits, and we'll
          fetch satellite data to track your carbon sequestration.
        </p>

        {error && (
          <div
            style={{
              background: '#fee2e2',
              color: '#991b1b',
              padding: '12px',
              borderRadius: '4px',
              marginBottom: '20px',
              fontSize: '14px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <span>⚠️ {error}</span>
            <button
              type="button"
              onClick={() => {
                setError('');
                setMapReady(false);
              }}
              style={{
                background: '#991b1b',
                color: 'white',
                border: 'none',
                padding: '4px 12px',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px',
              }}
            >
              Retry
            </button>
          </div>
        )}

        {successMsg && (
          <div
            style={{
              background: '#dcfce7',
              color: '#166534',
              padding: '12px',
              borderRadius: '4px',
              marginBottom: '20px',
              fontSize: '14px',
            }}
          >
            ✅ {successMsg}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label
              style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '500',
                fontSize: '14px',
              }}
            >
              Farm Name *
            </label>
            <input
              type="text"
              value={farmName}
              onChange={(e) => setFarmName(e.target.value)}
              placeholder="e.g., Northern Plantation A"
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '14px',
                boxSizing: 'border-box',
              }}
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label
              style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '500',
                fontSize: '14px',
              }}
            >
              Farm Boundary on Map *
            </label>
            <p style={{ fontSize: '12px', color: '#666', marginBottom: '10px' }}>
              {isDrawing
                ? '📍 Click on map to add points, double-click to complete polygon'
                : 'Click on the map to add points, double-click to complete polygon.'}
            </p>
            <div
              style={{
                position: 'relative',
                width: '100%',
                height: '400px',
                marginBottom: '10px',
              }}
            >
              {/* Layer Switcher Controls */}
              <div
                style={{
                  position: 'absolute',
                  top: '10px',
                  right: '10px',
                  display: 'flex',
                  gap: '5px',
                  zIndex: 999,
                  background: 'white',
                  padding: '8px',
                  borderRadius: '4px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
                }}
              >
                <button
                  type="button"
                  onClick={() => toggleMapLayer('osm')}
                  style={{
                    padding: '6px 12px',
                    background: mapLayer === 'osm' ? '#3b82f6' : '#e5e7eb',
                    color: mapLayer === 'osm' ? 'white' : '#333',
                    border: 'none',
                    borderRadius: '3px',
                    cursor: 'pointer',
                    fontSize: '12px',
                    fontWeight: '500',
                  }}
                >
                  🗺️ Map
                </button>
                <button
                  type="button"
                  onClick={() => toggleMapLayer('satellite')}
                  style={{
                    padding: '6px 12px',
                    background: mapLayer === 'satellite' ? '#3b82f6' : '#e5e7eb',
                    color: mapLayer === 'satellite' ? 'white' : '#333',
                    border: 'none',
                    borderRadius: '3px',
                    cursor: 'pointer',
                    fontSize: '12px',
                    fontWeight: '500',
                  }}
                >
                  🛰️ Satellite
                </button>
              </div>

              <div
                ref={mapContainerRef}
                style={{
                  width: '100%',
                  height: '100%',
                  border: '2px solid #3b82f6',
                  borderRadius: '4px',
                  background: '#f0f0f0',
                  display: 'block',
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                {!mapReady && !error && (
                  <div
                    style={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: 'translate(-50%, -50%)',
                      textAlign: 'center',
                      zIndex: 1,
                    }}
                  >
                    <div
                      style={{
                        display: 'inline-block',
                        width: '40px',
                        height: '40px',
                        border: '4px solid #3b82f6',
                        borderTop: '4px solid #f0f0f0',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite',
                        marginBottom: '10px',
                      }}
                    />
                    <p style={{ margin: '0', color: '#666', fontSize: '12px' }}>Loading Map...</p>
                  </div>
                )}
              </div>

              {pendingPolygon && !drawnPolygon && (
                <div
                  style={{
                    position: 'absolute',
                    left: '10px',
                    right: '10px',
                    bottom: '10px',
                    background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.98) 0%, rgba(22, 163, 74, 0.98) 100%)',
                    color: 'white',
                    padding: '16px',
                    borderRadius: '6px',
                    fontSize: '13px',
                    fontWeight: '500',
                    zIndex: 100,
                    boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
                    border: '2px solid #16a34a',
                  }}
                >
                  <div style={{ marginBottom: '12px', fontSize: '14px', fontWeight: '600' }}>
                    📍 Land Boundary Ready: <strong>{pendingArea} hectares</strong>
                  </div>
                  <p style={{ margin: '0 0 12px 0', fontSize: '12px', opacity: 0.95 }}>
                    Review the highlighted area below the form will be auto-filled
                  </p>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      type="button"
                      onClick={confirmBoundary}
                      style={{
                        background: 'white',
                        color: '#16a34a',
                        border: 'none',
                        padding: '8px 16px',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '13px',
                        fontWeight: '700',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
                        flex: 1,
                      }}
                    >
                      ✅ SAVE LAND AREA
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setPendingPolygon(null);
                        setPendingArea('');
                        if (drawnLayerRef.current) {
                          drawnLayerRef.current.clearLayers();
                        }
                      }}
                      style={{
                        background: 'rgba(255,255,255,0.2)',
                        color: 'white',
                        border: '1.5px solid rgba(255,255,255,0.5)',
                        padding: '8px 14px',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '12px',
                        fontWeight: '600',
                        transition: 'all 0.2s',
                      }}
                    >
                      ✏️ REDRAW
                    </button>
                  </div>
                </div>
              )}

              {drawnPolygon && (
                <div
                  style={{
                    position: 'absolute',
                    left: '10px',
                    right: '10px',
                    bottom: '10px',
                    background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.95) 0%, rgba(37, 99, 235, 0.95) 100%)',
                    color: 'white',
                    padding: '12px 16px',
                    borderRadius: '6px',
                    fontSize: '13px',
                    fontWeight: '600',
                    zIndex: 100,
                    boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
                    border: '2px solid #2563eb',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                  }}
                >
                  <span style={{ fontSize: '16px' }}>✨</span>
                  Land area <strong>{areaHa}</strong> hectares saved! Form below is auto-filled.
                </div>
              )}

              {isDrawing && (
                <div
                  style={{
                    position: 'absolute',
                    top: '10px',
                    left: '10px',
                    right: '10px',
                    background: 'rgba(59, 130, 246, 0.95)',
                    color: 'white',
                    padding: '12px 16px',
                    borderRadius: '4px',
                    fontSize: '13px',
                    fontWeight: '500',
                    zIndex: 100,
                    boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>📍 Drawing Mode - Points: {drawingStateRef.current.coordinates.length}</span>
                    <button
                      type="button"
                      onClick={handleClearDrawing}
                      style={{
                        background: 'rgba(255,255,255,0.3)',
                        color: 'white',
                        border: '1px solid white',
                        padding: '4px 12px',
                        borderRadius: '3px',
                        cursor: 'pointer',
                        fontSize: '12px',
                      }}
                    >
                      Cancel Drawing
                    </button>
                  </div>
                  <div style={{ marginTop: '8px', fontSize: '12px', opacity: 0.9 }}>
                    ✓ {drawingStateRef.current.coordinates.length === 0 ? 'Click on map to start' : drawingStateRef.current.coordinates.length === 1 ? 'Add at least 2 more points' : drawingStateRef.current.coordinates.length === 2 ? 'Add 1 more point then double-click' : 'Double-click to finish polygon'}
                  </div>
                </div>
              )}
            </div>
            <div style={{ display: 'flex', gap: '10px', marginTop: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
              <button
                type="button"
                onClick={handleStartDrawing}
                disabled={isDrawing || isSubmitting || !mapReady}
                style={{
                  padding: '10px 18px',
                  background: isDrawing ? '#1d4ed8' : '#3b82f6',
                  color: 'white',
                  border: isDrawing ? '2px solid #1d4ed8' : 'none',
                  borderRadius: '4px',
                  cursor: !mapReady || isDrawing ? 'not-allowed' : 'pointer',
                  opacity: !mapReady || isDrawing ? 0.7 : 1,
                  fontSize: '14px',
                  fontWeight: '600',
                  boxShadow: isDrawing ? '0 0 12px rgba(59, 130, 246, 0.5)' : 'none',
                  transition: 'all 0.2s',
                }}
              >
                {!mapReady
                  ? '⏳ Loading Map...'
                  : isDrawing
                    ? '🖱️ Drawing...'
                    : '✏️ Draw Polygon'}
              </button>

              {pendingPolygon && !drawnPolygon && (
                <>
                  <button
                    type="button"
                    onClick={confirmBoundary}
                    style={{
                      padding: '10px 18px',
                      background: 'linear-gradient(135deg, #16a34a 0%, #15803d 100%)',
                      color: 'white',
                      border: '2px solid #22c55e',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '14px',
                      fontWeight: '700',
                      boxShadow: '0 0 12px rgba(34, 197, 94, 0.5)',
                      transition: 'all 0.2s',
                    }}
                  >
                    ✅ SAVE LAND AREA ({pendingArea} ha)
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      console.log('Redraw clicked');
                      setPendingPolygon(null);
                      setPendingArea('');
                      if (drawnLayerRef.current) {
                        drawnLayerRef.current.clearLayers();
                      }
                    }}
                    style={{
                      padding: '10px 18px',
                      background: '#f59e0b',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '14px',
                      fontWeight: '600',
                    }}
                  >
                    ✏️ REDRAW
                  </button>
                </>
              )}

              <button
                type="button"
                onClick={handleClearDrawing}
                disabled={!drawnPolygon && !isDrawing || isSubmitting}
                style={{
                  padding: '10px 18px',
                  background: '#ef4444',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: drawnPolygon || isDrawing ? 'pointer' : 'not-allowed',
                  opacity: drawnPolygon || isDrawing ? 1 : 0.5,
                  fontSize: '14px',
                  fontWeight: '600',
                }}
              >
                🗑️ Clear
              </button>
            </div>
            {drawnPolygon && (
              <p
                style={{
                  fontSize: '12px',
                  color: '#16a34a',
                  marginTop: '8px',
                  fontWeight: '500',
                }}
              >
                ✓ Polygon drawn ({(parseFloat(areaHa) || 0).toFixed(2)} hectares)
              </p>
            )}
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '20px',
              marginBottom: '20px',
            }}
          >
            <div>
              <label
                style={{
                  display: 'block',
                  marginBottom: '8px',
                  fontWeight: '500',
                  fontSize: '14px',
                }}
              >
                Farm Area (Hectares) *
              </label>
              <input
                type="number"
                value={areaHa}
                onChange={(e) => setAreaHa(e.target.value)}
                placeholder="Calculated from polygon"
                step="0.01"
                min="0"
                style={{
                  width: '100%',
                  padding: '10px',
                  border: `1px solid ${areaHa ? '#16a34a' : '#ddd'}`,
                  borderRadius: '4px',
                  fontSize: '14px',
                  boxSizing: 'border-box',
                  background: areaHa ? '#f0fdf4' : 'white',
                }}
                readOnly
              />
              <p style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                Auto-calculated from drawn polygon
              </p>
            </div>

            <div>
              <label
                style={{
                  display: 'block',
                  marginBottom: '8px',
                  fontWeight: '500',
                  fontSize: '14px',
                }}
              >
                Promised Carbon Credits (tCO2e/year) *
              </label>
              <input
                type="number"
                value={promisedCredits}
                onChange={(e) => setPromisedCredits(e.target.value)}
                placeholder="Enter promised credits from supplier"
                step="0.1"
                min="0"
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '14px',
                  boxSizing: 'border-box',
                }}
              />
              <p style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                Claim from your carbon supplier
              </p>
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting || !farmName || !drawnPolygon || !promisedCredits}
            style={{
              width: '100%',
              padding: '12px',
              background: isSubmitting ? '#888' : '#22c55e',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              fontSize: '16px',
              fontWeight: '600',
              cursor:
                isSubmitting || !farmName || !drawnPolygon || !promisedCredits
                  ? 'not-allowed'
                  : 'pointer',
              opacity:
                isSubmitting || !farmName || !drawnPolygon || !promisedCredits ? 0.6 : 1,
            }}
          >
            {isSubmitting ? '📡 Creating Farm...' : '✅ Create Farm & Fetch Satellite Data'}
          </button>
        </form>
      </div>
    </div>
  );
}
