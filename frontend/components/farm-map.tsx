'use client';

import React, { useState, useEffect, useRef } from 'react';

interface Farm {
  id: number;
  name: string;
  geometry: {
    type: string;
    coordinates: number[][][];
  };
  area_ha: number;
  created_at: string;
}

interface FarmMapProps {
  mockFarms?: Farm[];
}

export function FarmMap({ mockFarms }: FarmMapProps) {
  const [farms, setFarms] = useState<Farm[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const mapRef = useRef<any>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const L = useRef<any>(null);
  const markersRef = useRef<any[]>([]);

  // Initialize map and fetch farms
  useEffect(() => {
    if (!mapContainerRef.current) return;

    const initMap = async () => {
      try {
        // Dynamically import Leaflet
        const leaflet = await import('leaflet');
        L.current = leaflet.default;

        // Load CSS
        if (!document.getElementById('leaflet-css-farm')) {
          const link = document.createElement('link');
          link.id = 'leaflet-css-farm';
          link.rel = 'stylesheet';
          link.href = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css';
          document.head.appendChild(link);
        }

        // Create map centered on Africa (default view)
        if (!mapContainerRef.current) {
          throw new Error('Map container not found');
        }

        const map = L.current.map(mapContainerRef.current).setView([0, 20], 4);

        // Add OpenStreetMap tiles
        L.current.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '© OpenStreetMap contributors',
          maxZoom: 19,
        }).addTo(map);

        mapRef.current = map;

        // Fetch farms from backend
        fetchFarms(map);
      } catch (err) {
        console.error('Failed to initialize map:', err);
        // Use mock data as fallback
        if (mockFarms && mockFarms.length > 0) {
          setFarms(mockFarms);
          setLoading(false);
        } else {
          setError('Failed to load map');
          setLoading(false);
        }
      }
    };

    initMap();

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [mockFarms]);

  // Fetch farms from backend
  const fetchFarms = async (map: any) => {
    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        // Use mock data if not authenticated
        if (mockFarms && mockFarms.length > 0) {
          setFarms(mockFarms);
          if (map && L.current) {
            plotFarmsOnMap(map, mockFarms);
          }
          setLoading(false);
          return;
        }
        // No token and no mock data - just load empty
        setLoading(false);
        return;
      }

      const response = await fetch('/api/v1/farms', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch farms');
      }

      const farmsData = await response.json();
      setFarms(farmsData);

      // Plot farms on map
      if (map && L.current) {
        plotFarmsOnMap(map, farmsData);
      }
    } catch (err) {
      console.error('Error fetching farms:', err);
      // Fallback to mock data on error
      if (mockFarms && mockFarms.length > 0) {
        setFarms(mockFarms);
        if (mapRef.current && L.current) {
          plotFarmsOnMap(mapRef.current, mockFarms);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  // Plot farms on map
  const plotFarmsOnMap = (map: any, farmsData: Farm[]) => {
    // Clear existing markers
    markersRef.current.forEach((marker) => map.removeLayer(marker));
    markersRef.current = [];

    if (farmsData.length === 0) {
      setError('No farms found');
      return;
    }

    // Add farms to map
    farmsData.forEach((farm) => {
      try {
        if (farm.geometry && farm.geometry.type === 'Polygon') {
          const coordinates = farm.geometry.coordinates[0];
          const latLngs = coordinates.map((coord) => [coord[1], coord[0]]);

          // Draw polygon
          const polygon = L.current.polygon(latLngs, {
            color: '#1890ff',
            weight: 2,
            opacity: 0.8,
            fillColor: '#1890ff',
            fillOpacity: 0.2,
          }).addTo(map);

          markersRef.current.push(polygon);

          // Calculate center and add popup
          const bounds = L.current.latLngBounds(latLngs);
          const center = bounds.getCenter();

          const popup = L.current.circleMarker(center, {
            radius: 8,
            fillColor: '#1890ff',
            color: '#0050b3',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8,
          })
            .bindPopup(
              `<div style="font-family: Arial; font-size: 12px;">
                <strong>${farm.name}</strong><br/>
                Area: ${farm.area_ha.toFixed(2)} ha<br/>
                Created: ${new Date(farm.created_at).toLocaleDateString()}
              </div>`
            )
            .addTo(map);

          markersRef.current.push(popup);

          // Fit map to farms on first load
          if (farmsData.length > 0) {
            map.fitBounds(bounds.pad(0.1));
          }
        }
      } catch (err) {
        console.error(`Error plotting farm ${farm.name}:`, err);
      }
    });

    setError('');
  };

  return (
    <div style={{ width: '100%' }}>
      <div style={{ backgroundColor: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <h3 style={{ margin: 0, marginBottom: '15px', color: '#333', fontSize: '18px' }}>
          🗺️ Farm Location Map
        </h3>

        {error && (
          <div
            style={{
              background: '#fee2e2',
              color: '#991b1b',
              padding: '12px',
              borderRadius: '4px',
              marginBottom: '15px',
              fontSize: '14px',
            }}
          >
            {error}
          </div>
        )}

        {loading && (
          <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
            ⏳ Loading farms...
          </div>
        )}

        <div
          ref={mapContainerRef}
          style={{
            width: '100%',
            height: '500px',
            borderRadius: '4px',
            border: '1px solid #e0e0e0',
            background: '#f5f5f5',
          }}
        />

        {!loading && farms.length > 0 && (
          <div style={{ marginTop: '15px', fontSize: '14px', color: '#666' }}>
            <strong>Farms on map:</strong> {farms.length}
            <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
              {farms.map((farm) => (
                <li key={farm.id}>
                  {farm.name} ({farm.area_ha.toFixed(2)} ha)
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
