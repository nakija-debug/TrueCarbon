/**
 * Dashboard-specific TypeScript types
 */

export interface KPIData {
  totalLandArea: number;
  carbonGenerated: number;
  activeProjects: number;
  verifiedPercent: number;
  avgNDVIChange: number;
}

export interface LandProperties {
  id: number;
  name: string;
  area_ha: number;
  location: string;
  status: 'active' | 'inactive' | 'pending';
  lastMeasurement?: string;
  carbonCredit?: number;
  ndvi?: number;
}

export type AlertSeverity = 'low' | 'medium' | 'high' | 'critical';
export type AlertType = 'warning' | 'info' | 'success' | 'error';

export interface AlertData {
  id: string;
  type: AlertType;
  severity: AlertSeverity;
  message: string;
  date: string;
  actionRequired: boolean;
  actionUrl?: string;
}

export interface TimeSeriesData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    borderColor?: string;
    backgroundColor?: string;
    fill?: boolean;
    tension?: number;
    borderWidth?: number;
  }>;
}

export type MapLayerType = 'ndvi' | 'parcels' | 'carbon';

export interface DashboardContextType {
  selectedLand: LandProperties | null;
  setSelectedLand: (land: LandProperties | null) => void;
  dateRange: {
    startDate: string;
    endDate: string;
  };
  setDateRange: (range: { startDate: string; endDate: string }) => void;
  locationFilter: string;
  setLocationFilter: (location: string) => void;
  activeLayer: MapLayerType;
  setActiveLayer: (layer: MapLayerType) => void;
}
