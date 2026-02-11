import React, { createContext, useState, useContext, useEffect } from 'react';
import { api } from '../services/api';

const DashboardContext = createContext();

export const useDashboard = () => {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error('useDashboard must be used within DashboardProvider');
  }
  return context;
};

export const DashboardProvider = ({ children }) => {
  const [selectedLand, setSelectedLand] = useState(null);
  const [dateRange, setDateRange] = useState('1year');
  const [locationFilter, setLocationFilter] = useState('all');
  const [kpiData, setKpiData] = useState(null);
  const [landsData, setLandsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [alerts, setAlerts] = useState([]);

  // Load initial data
  useEffect(() => {
    loadDashboardData();
    loadAlerts();
  }, [dateRange, locationFilter]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Fetch KPI data with current filters
      const kpis = await api.getKPIs({ dateRange, location: locationFilter });
      setKpiData(kpis);
      
      // Fetch land data with current filters
      const lands = await api.getLands({ dateRange });
      setLandsData(lands);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAlerts = async () => {
    try {
      const alertData = await api.getAlerts();
      setAlerts(alertData.highPriority || []);
    } catch (error) {
      console.error('Failed to load alerts:', error);
    }
  };

  const selectLand = (land) => {
    setSelectedLand(land);
  };

  const value = {
    selectedLand,
    selectLand,
    dateRange,
    setDateRange,
    locationFilter,
    setLocationFilter,
    kpiData,
    landsData,
    loading,
    alerts,
    loadDashboardData
  };

  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  );
};