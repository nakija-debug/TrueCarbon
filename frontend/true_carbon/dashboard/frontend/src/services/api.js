import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// BACKEND INTEGRATION POINT:
// All API calls will be replaced with real backend integration
// Error handling and retry logic will be added for production

export const api = {
  // Fetch KPI data with filters
  getKPIs: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.dateRange) params.append('dateRange', filters.dateRange);
    if (filters.location) params.append('location', filters.location);
    
    const response = await axios.get(`${API_BASE_URL}/kpis?${params}`);
    return response.data;
  },

  // Fetch land parcel GeoJSON data
  getLands: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.dateRange) params.append('dateRange', filters.dateRange);
    if (filters.verifiedOnly) params.append('verifiedOnly', filters.verifiedOnly);
    
    const response = await axios.get(`${API_BASE_URL}/lands?${params}`);
    return response.data;
  },

  // Fetch NDVI time-series for specific land
  getNDVITimeSeries: async (landId, timeframe = {}) => {
    const params = new URLSearchParams();
    if (timeframe.startDate) params.append('startDate', timeframe.startDate);
    if (timeframe.endDate) params.append('endDate', timeframe.endDate);
    
    const response = await axios.get(
      `${API_BASE_URL}/ndvi/${landId}?${params}`
    );
    return response.data;
  },

  // Fetch carbon data
  getCarbonData: async (landId) => {
    const response = await axios.get(`${API_BASE_URL}/carbon/${landId}`);
    return response.data;
  },

  // Fetch environmental data
  getEnvironmentalData: async (landId) => {
    const response = await axios.get(`${API_BASE_URL}/environment/${landId}`);
    return response.data;
  },

  // Export reports
  exportReport: async (landId, reportType = 'verification', format = 'pdf') => {
    const response = await axios.post(`${API_BASE_URL}/reports/export`, {
      landId,
      reportType,
      format
    });
    return response.data;
  },

  // Fetch alerts
  getAlerts: async () => {
    const response = await axios.get(`${API_BASE_URL}/alerts`);
    return response.data;
  }
};