/**
 * Type guards and validators
 */

import type { FarmResponse } from '@/types/farm';
import type { DateRangeFilter } from '@/types/api';

/**
 * Check if value is a valid GeoJSON geometry
 */
export function isValidGeoJSONGeometry(value: unknown): value is any {
  if (!value || typeof value !== 'object') {
    return false;
  }

  const obj = value as Record<string, unknown>;
  const validTypes = ['Point', 'LineString', 'Polygon', 'MultiPoint', 'MultiLineString', 'MultiPolygon', 'GeometryCollection'];

  return 'type' in obj && validTypes.includes(String(obj.type)) && 'coordinates' in obj;
}

/**
 * Check if value is a date range filter
 */
export function isValidDateRange(value: unknown): value is DateRangeFilter {
  if (!value || typeof value !== 'object') {
    return false;
  }

  const obj = value as Record<string, unknown>;
  if (!('startDate' in obj) || !('endDate' in obj)) {
    return false;
  }

  const startDate = new Date(String(obj.startDate));
  const endDate = new Date(String(obj.endDate));

  return !isNaN(startDate.getTime()) && !isNaN(endDate.getTime()) && startDate <= endDate;
}

/**
 * Check if value is a FarmResponse
 */
export function isFarmResponse(value: unknown): value is FarmResponse {
  if (!value || typeof value !== 'object') {
    return false;
  }

  const obj = value as Record<string, unknown>;
  return (
    'id' in obj &&
    'name' in obj &&
    'area_ha' in obj &&
    'geometry' in obj &&
    'company_id' in obj &&
    isValidGeoJSONGeometry(obj.geometry)
  );
}

/**
 * Validate date format YYYY-MM-DD
 */
export function isValidDateFormat(date: string): boolean {
  const regex = /^\d{4}-\d{2}-\d{2}$/;
  if (!regex.test(date)) {
    return false;
  }

  const parsedDate = new Date(date);
  return !isNaN(parsedDate.getTime());
}
