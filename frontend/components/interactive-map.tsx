/**
 * Interactive Map Component - Displays farms on Mapbox GL JS map
 */

'use client';

import React, { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { useFarmsGeoJSON } from '@/hooks/use-farms';
import { useDashboardContext } from '@/lib/contexts/dashboard-context';
import { ErrorMessage } from '@/components/ui/error-message';
import { EmptyState } from '@/components/ui/empty-state';
import { MapSkeleton } from '@/components/ui/skeleton';
import { MAPBOX_TOKEN } from '@/lib/mapbox-config';

export function InteractiveMap() {
  const { data: farmsGeoJSON, isLoading, error, refetch } = useFarmsGeoJSON();
  const { setSelectedLand } = useDashboardContext();
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || !MAPBOX_TOKEN) return;

    mapboxgl.accessToken = MAPBOX_TOKEN;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/light-v10',
      center: [0, 0],
      zoom: 2,
    });

    return () => {
      map.current?.remove();
    };
  }, []);

  // Add data sources and layers
  useEffect(() => {
    if (!map.current || !farmsGeoJSON || farmsGeoJSON.length === 0) return;

    // Create FeatureCollection from farmsGeoJSON
    const featureCollection: GeoJSON.FeatureCollection = {
      type: 'FeatureCollection',
      features: farmsGeoJSON.map((farm) => ({
        type: 'Feature' as const,
        id: farm.id,
        geometry: farm.geometry,
        properties: farm.properties,
      })),
    };

    // Add source
    if (!map.current.getSource('farms')) {
      map.current.addSource('farms', {
        type: 'geojson',
        data: featureCollection,
      });
    } else {
      (map.current.getSource('farms') as mapboxgl.GeoJSONSource).setData(featureCollection);
    }

    // Add layer
    if (!map.current.getLayer('farms-layer')) {
      map.current.addLayer({
        id: 'farms-layer',
        type: 'fill',
        source: 'farms',
        paint: {
          'fill-color': '#088',
          'fill-opacity': 0.8,
        },
      });

      map.current.addLayer({
        id: 'farms-outline',
        type: 'line',
        source: 'farms',
        paint: {
          'line-color': '#088',
          'line-width': 2,
        },
      });
    }

    // Add click handler
    map.current.on('click', 'farms-layer', (e) => {
      if (e.features && e.features.length > 0) {
        const feature = e.features[0];
        setSelectedLand({
          id: feature.id as number,
          name: feature.properties?.name || 'Unknown',
          area_ha: feature.properties?.area_ha || 0,
          location: feature.properties?.location || 'Unknown',
          status: 'active',
        });
      }
    });

    // Fit bounds to data
    const bbox = getBounds(featureCollection);
    if (bbox) {
      map.current.fitBounds(bbox, { padding: 50 });
    }
  }, [farmsGeoJSON, setSelectedLand]);

  if (isLoading) {
    return <MapSkeleton />;
  }

  if (error) {
    return <ErrorMessage message="Failed to load map data" onRetry={() => refetch()} />;
  }

  if (!farmsGeoJSON || farmsGeoJSON.length === 0) {
    return <EmptyState title="No farms available" description="Add your first farm to see it on the map" />;
  }

  return <div ref={mapContainer} className="h-96 w-full rounded-lg border border-gray-200" />;
}

/**
 * Calculate bounding box from GeoJSON FeatureCollection
 */
function getBounds(fc: GeoJSON.FeatureCollection): [[number, number], [number, number]] | null {
  let minLng = Infinity,
    minLat = Infinity,
    maxLng = -Infinity,
    maxLat = -Infinity;

  fc.features.forEach((feature) => {
    if (feature.geometry.type === 'Polygon') {
      const coords = feature.geometry.coordinates[0];
      coords.forEach(([lng, lat]) => {
        minLng = Math.min(minLng, lng);
        minLat = Math.min(minLat, lat);
        maxLng = Math.max(maxLng, lng);
        maxLat = Math.max(maxLat, lat);
      });
    }
  });

  return isFinite(minLng) ? [[minLng, minLat], [maxLng, maxLat]] : null;
}
