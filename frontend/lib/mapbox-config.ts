/**
 * Mapbox GL JS configuration
 */

import type { StyleSpecification } from 'mapbox-gl';

export const MAPBOX_TOKEN = (process.env as any).NEXT_PUBLIC_MAPBOX_TOKEN;

export const DEFAULT_MAP_STYLE: StyleSpecification = {
  version: 8,
  name: 'Light',
  glyphs: 'mapbox://fonts/mapbox/{fontstack}/{range}.pbf',
  sources: {
    'mapbox-streets': {
      type: 'vector',
      url: 'mapbox://mapbox.mapbox-streets-v8',
    },
  },
  layers: [
    {
      id: 'background',
      type: 'background',
      paint: {
        'background-color': '#f0f0f0',
      },
    },
  ],
};

// Layer configurations with Mapbox types
export const NDVI_LAYER_CONFIG = {
  id: 'ndvi-layer',
  type: 'fill' as const,
  source: 'ndvi-source',
  paint: {
    'fill-color': [
      'interpolate',
      ['linear'],
      ['get', 'ndvi'],
      0,
      '#d73027',
      0.2,
      '#fee090',
      0.4,
      '#ffffbf',
      0.6,
      '#e0f3f8',
      0.8,
      '#4575b4',
    ],
    'fill-opacity': 0.7,
  },
};

export const PARCELS_LAYER_CONFIG = {
  id: 'parcels-layer',
  type: 'line' as const,
  source: 'parcels-source',
  paint: {
    'line-color': '#627BC1',
    'line-width': 2,
  },
};

export const CARBON_LAYER_CONFIG = {
  id: 'carbon-layer',
  type: 'fill' as const,
  source: 'carbon-source',
  paint: {
    'fill-color': [
      'interpolate',
      ['linear'],
      ['get', 'carbon'],
      0,
      '#ffffcc',
      100,
      '#addd8e',
      200,
      '#78c679',
      300,
      '#31a354',
      400,
      '#006837',
    ],
    'fill-opacity': 0.7,
  },
};

export type MapLayerConfig = typeof NDVI_LAYER_CONFIG | typeof PARCELS_LAYER_CONFIG | typeof CARBON_LAYER_CONFIG;
