/**
 * Farm-related TypeScript types
 * Based on backend/app/schemas/farm.py
 */

export interface FarmBase {
  name: string;
  description?: string;
  area_ha: number;
  geometry: any;
}

export interface FarmCreate extends FarmBase {}

export interface FarmUpdate {
  name?: string;
  description?: string;
  area_ha?: number;
  geometry?: GeoJSON.Geometry;
}

export interface FarmResponse extends FarmBase {
  id: number;
  company_id: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface FarmGeoJSON {
  type: 'Feature';
  id: number;
  geometry: GeoJSON.Geometry;
  properties: {
    name: string;
    description?: string;
    area_ha: number;
    company_id: number;
    is_active: boolean;
    created_at: string;
    updated_at: string;
  };
}
