/**
 * KPI and Alerts API Module
 * Handles KPI data and alert requests to FastAPI backend
 */

import axiosInstance from '../api-client';

export interface KPIData {
  totalLandArea: number;
  carbonGenerated: number;
  totalCarbonCredits: number;
  activeProjects: number;
  verifiedPercent: number;
  avgNDVIChange: number;
  timestamp: string;
}

export interface Alert {
  id: string;
  level: 'high' | 'medium' | 'low';
  message: string;
  farmId?: number;
  farmName?: string;
  type: 'verification' | 'performance' | 'data_quality' | 'anomaly';
  timestamp: string;
}

export interface KPIFilters {
  dateRange?: string; // '1month' | '3months' | '6months' | '1year'
  location?: string;
}

/**
 * Get KPI data with optional filters
 */
export async function getKPIs(filters?: KPIFilters): Promise<KPIData> {
  const response = await axiosInstance.get<KPIData>('/api/v1/kpis', { params: filters });
  return response.data;
}

/**
 * Get alerts with optional filtering
 */
export async function getAlerts(params?: {
  level?: string;
  type?: string;
  limit?: number;
}): Promise<{ highPriority: Alert[]; all: Alert[] }> {
  const response = await axiosInstance.get<{
    highPriority: Alert[];
    all: Alert[];
  }>('/api/v1/alerts', { params });
  return response.data;
}

/**
 * Get specific alert details
 */
export async function getAlert(alertId: string): Promise<Alert> {
  const response = await axiosInstance.get<Alert>(`/api/v1/alerts/${alertId}`);
  return response.data;
}

/**
 * Mark alert as read
 */
export async function markAlertAsRead(alertId: string): Promise<void> {
  await axiosInstance.put(`/api/v1/alerts/${alertId}/read`, {});
}

/**
 * Dismiss alert
 */
export async function dismissAlert(alertId: string): Promise<void> {
  await axiosInstance.delete(`/api/v1/alerts/${alertId}`);
}
