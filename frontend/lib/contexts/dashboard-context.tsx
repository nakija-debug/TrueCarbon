'use client';

/**
 * Dashboard Context - Manages dashboard-wide state
 */

import { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import type { DashboardContextType, LandProperties, MapLayerType } from '@/types/dashboard';

const DashboardContext = createContext<DashboardContextType | undefined>(undefined);

interface DashboardProviderProps {
  children: ReactNode;
}

export function DashboardProvider({ children }: DashboardProviderProps) {
  const [selectedLand, setSelectedLand] = useState<LandProperties | null>(null);
  const [dateRange, setDateRange] = useState({
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 days ago
    endDate: new Date().toISOString().split('T')[0], // Today
  });
  const [locationFilter, setLocationFilter] = useState<string>('');
  const [activeLayer, setActiveLayer] = useState<MapLayerType>('ndvi');

  const handleSetSelectedLand = useCallback((land: LandProperties | null) => {
    setSelectedLand(land);
  }, []);

  const handleSetDateRange = useCallback((range: { startDate: string; endDate: string }) => {
    setDateRange(range);
  }, []);

  const handleSetLocationFilter = useCallback((location: string) => {
    setLocationFilter(location);
  }, []);

  const handleSetActiveLayer = useCallback((layer: MapLayerType) => {
    setActiveLayer(layer);
  }, []);

  const value: DashboardContextType = {
    selectedLand,
    setSelectedLand: handleSetSelectedLand,
    dateRange,
    setDateRange: handleSetDateRange,
    locationFilter,
    setLocationFilter: handleSetLocationFilter,
    activeLayer,
    setActiveLayer: handleSetActiveLayer,
  };

  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  );
}

/**
 * Hook to use dashboard context
 */
export function useDashboardContext(): DashboardContextType {
  const context = useContext(DashboardContext);
  if (context === undefined) {
    throw new Error('useDashboardContext must be used within DashboardProvider');
  }
  return context;
}
