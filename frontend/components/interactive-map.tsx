'use client';

/**
 * Interactive Map Component - Displays farms on Leaflet map with OpenStreetMap
 */

import React, { useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON, ZoomControl, ScaleControl } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useFarmsGeoJSON } from '@/hooks/use-farms';
import { useDashboardContext } from '@/lib/contexts/dashboard-context';
import { ErrorMessage } from '@/components/ui/error-message';
import { MapSkeleton } from '@/components/ui/skeleton';

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

export function InteractiveMap() {
  const { data: farmsGeoJSON, isLoading, error, refetch } = useFarmsGeoJSON();
  const { setSelectedLand } = useDashboardContext();

  useEffect(() => {
    fixLeafletIcons();
  }, []);

  const getFeatureStyle = () => ({
    fillColor: '#088',
    fillOpacity: 0.8,
    color: '#066',
    weight: 2,
  });

  const onEachFeature = (feature: any, layer: L.Layer) => {
    layer.on({
      click: () => {
        setSelectedLand({
          id: feature.id as number,
          name: feature.properties?.name || 'Unknown',
          area_ha: feature.properties?.area_ha || 0,
          location: feature.properties?.location || 'Unknown',
          status: 'active',
        });
      },
      mouseover: (e: any) => {
        const l = e.target;
        l.setStyle({ weight: 4 });
      },
      mouseout: (e: any) => {
        const l = e.target;
        l.setStyle(getFeatureStyle());
      }
    });
  };

  if (isLoading) return <MapSkeleton />;
  if (error) return <ErrorMessage message="Failed to load map data" onRetry={() => refetch()} />;

  return (
    <div className="h-96 w-full rounded-lg border border-gray-200 overflow-hidden">
      <MapContainer
        center={[0, 0]}
        zoom={2}
        style={{ height: '100%', width: '100%' }}
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ZoomControl position="top-right" />
        <ScaleControl position="bottomleft" />
        {farmsGeoJSON && (
          <GeoJSON
            data={farmsGeoJSON as any}
            style={getFeatureStyle}
            onEachFeature={onEachFeature}
          />
        )}
      </MapContainer>
    </div>
  );
}
