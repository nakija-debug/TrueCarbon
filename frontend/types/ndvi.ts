/**
 * NDVI (Normalized Difference Vegetation Index) TypeScript types
 * Based on backend/app/schemas/ndvi.py
 */

export interface NDVIDataPoint {
  date: string; // YYYY-MM-DD
  ndvi: number;
  std_dev?: number;
}

export interface NDVIRequest {
  farm_id: number;
  start_date: string; // YYYY-MM-DD
  end_date: string; // YYYY-MM-DD
}

export interface NDVIMetadata {
  data_source: string;
  collection: string;
  collection_version: string;
  scale: number;
  units: string;
  processing_timestamp: string;
  satellite_images_used: number;
  cloud_cover_mean: number;
}

export interface NDVIResponse {
  farm_id: number;
  farm_name: string;
  ndvi_data: NDVIDataPoint[];
  min_ndvi: number;
  max_ndvi: number;
  mean_ndvi: number;
  metadata: NDVIMetadata;
}
