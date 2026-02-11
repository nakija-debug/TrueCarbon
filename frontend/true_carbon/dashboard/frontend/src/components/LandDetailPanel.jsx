import React, { useState, useEffect } from 'react';
import { useDashboard } from '../context/DashboardContext';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { api } from '../services/api';
import {
  MapPinIcon,
  CalendarIcon,
  DocumentTextIcon,
  ArrowTrendingUpIcon,
  CloudIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const LandDetailPanel = () => {
  const { selectedLand } = useDashboard();
  const [ndviData, setNdviData] = useState(null);
  const [carbonData, setCarbonData] = useState(null);
  const [envData, setEnvData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (selectedLand) {
      loadLandData();
    }
  }, [selectedLand]);

  const loadLandData = async () => {
    setLoading(true);
    try {
      // BACKEND INTEGRATION POINT:
      // Fetch all time-series data for selected land
      // Parallel API calls for efficiency
      const [ndvi, carbon, environment] = await Promise.all([
        api.getNDVITimeSeries(selectedLand.id),
        api.getCarbonData(selectedLand.id),
        api.getEnvironmentalData(selectedLand.id)
      ]);
      
      setNdviData(ndvi);
      setCarbonData(carbon);
      setEnvData(environment);
    } catch (error) {
      console.error('Failed to load land data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!selectedLand) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8 h-[800px] flex flex-col items-center justify-center">
        <DocumentTextIcon className="h-16 w-16 text-gray-300 mb-4" />
        <h3 className="text-xl font-semibold text-gray-700 mb-2">No Land Selected</h3>
        <p className="text-gray-500 text-center max-w-md">
          Click on any land parcel in the map to view detailed time-series data,
          carbon accumulation metrics, and environmental factors.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8 h-[800px] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading detailed analysis...</p>
          <p className="text-sm text-gray-500 mt-2">
            Processing NDVI, carbon, and environmental data
          </p>
        </div>
      </div>
    );
  }

  const ndviChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'NDVI Time Series - Vegetation Health',
        font: {
          size: 16
        }
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            return `NDVI: ${context.parsed.y.toFixed(3)}`;
          }
        }
      }
    },
    scales: {
      y: {
        min: 0,
        max: 1,
        title: {
          display: true,
          text: 'NDVI Value'
        }
      }
    }
  };

  const carbonChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Carbon Accumulation (tCO₂e)',
        font: {
          size: 16
        }
      }
    },
    scales: {
      x: {
        stacked: true,
      },
      y: {
        stacked: true,
        title: {
          display: true,
          text: 'Carbon (tCO₂e)'
        }
      }
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 h-[800px] overflow-y-auto">
      {/* Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{selectedLand.name}</h2>
          <div className="flex items-center mt-2 space-x-4">
            <span className="flex items-center text-gray-600">
              <MapPinIcon className="h-4 w-4 mr-1" />
              {selectedLand.location}
            </span>
            <span className="flex items-center text-gray-600">
              <CalendarIcon className="h-4 w-4 mr-1" />
              Started: {selectedLand.startDate}
            </span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              selectedLand.verificationStatus === 'Verified' ? 'bg-emerald-100 text-emerald-800' :
              selectedLand.verificationStatus === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>
              {selectedLand.verificationStatus}
            </span>
          </div>
        </div>
        <div className="text-right">
          <p className="text-3xl font-bold text-emerald-700">
            {selectedLand.carbonCreditsGenerated.toLocaleString()} tCO₂e
          </p>
          <p className="text-gray-600">Carbon Credits Generated</p>
        </div>
      </div>

      {/* Metadata Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-sm text-gray-500">Project ID</p>
          <p className="font-mono font-bold">{selectedLand.projectId}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-sm text-gray-500">Area</p>
          <p className="font-bold text-lg">{selectedLand.area_ha} ha</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-sm text-gray-500">Project Type</p>
          <p className="font-bold">{selectedLand.projectType}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-sm text-gray-500">NDVI Trend</p>
          <div className="flex items-center">
            <ArrowTrendingUpIcon className={`h-5 w-5 mr-2 ${
              selectedLand.ndviTrend >= 0 ? 'text-emerald-500' : 'text-red-500'
            }`} />
            <span className={`font-bold ${
              selectedLand.ndviTrend >= 0 ? 'text-emerald-700' : 'text-red-700'
            }`}>
              {selectedLand.ndviTrend >= 0 ? '+' : ''}{selectedLand.ndviTrend}
            </span>
          </div>
        </div>
      </div>

      {/* BACKEND INTEGRATION POINT:
      Section A: Time-Series Charts (CRITICAL for audit trail) */}
      <div className="mb-8">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
          <DocumentTextIcon className="h-5 w-5 mr-2" />
          Time-Series Analysis & Audit Trail
        </h3>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* NDVI Chart */}
          <div className="bg-white border border-gray-200 rounded-xl p-4">
            <Line 
              data={ndviData?.ndvi || { labels: [], datasets: [] }} 
              options={ndviChartOptions} 
              height={250}
            />
            <div className="mt-4 text-sm text-gray-500">
              <p>
                <span className="font-medium">Data Source:</span> Sentinel-2 (10m resolution)
              </p>
              <p>
                <span className="font-medium">Audit Trail:</span> Continuous monitoring, 
                {selectedLand.ndviTrend >= 0 ? ' positive ' : ' negative '}
                trend detected
              </p>
            </div>
          </div>

          {/* Carbon Chart */}
          <div className="bg-white border border-gray-200 rounded-xl p-4">
            <Bar 
              data={carbonData?.carbon || { labels: [], datasets: [] }} 
              options={carbonChartOptions} 
              height={250}
            />
            <div className="mt-4 text-sm text-gray-500">
              <p>
                <span className="font-medium">Methodology:</span> {carbonData?.methodology || 'IPCC Tier 2'}
              </p>
              <p>
                <span className="font-medium">Confidence:</span> {carbonData?.confidence || 0.92}
              </p>
              {/* BACKEND INTEGRATION POINT:
              Show calculation methodology details */}
            </div>
          </div>
        </div>
      </div>

      {/* BACKEND INTEGRATION POINT:
      Section C: Supporting Environmental Charts */}
      <div className="mb-8">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
          <CloudIcon className="h-5 w-5 mr-2" />
          Environmental Factors
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium text-gray-700 mb-2">Rainfall (mm)</h4>
            <div className="h-40 flex items-end space-x-1">
              {envData?.rainfall?.map((value, index) => (
                <div 
                  key={index}
                  className="flex-1 bg-blue-500 rounded-t"
                  style={{ height: `${(value / 150) * 100}%` }}
                  title={`Month ${index + 1}: ${value}mm`}
                ></div>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-2">Monthly rainfall correlation with NDVI</p>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium text-gray-700 mb-2">Temperature (°C)</h4>
            <div className="h-40 flex items-end space-x-1">
              {envData?.temperature?.map((value, index) => (
                <div 
                  key={index}
                  className="flex-1 bg-red-500 rounded-t"
                  style={{ height: `${((value - 20) / 15) * 100}%` }}
                  title={`Month ${index + 1}: ${value}°C`}
                ></div>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-2">Temperature trend affecting growth</p>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium text-gray-700 mb-2">Soil Moisture</h4>
            <div className="h-40 flex items-end space-x-1">
              {envData?.soilMoisture?.map((value, index) => (
                <div 
                  key={index}
                  className="flex-1 bg-amber-500 rounded-t"
                  style={{ height: `${value * 100}%` }}
                  title={`Month ${index + 1}: ${value.toFixed(2)}`}
                ></div>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-2">Soil moisture index from SMAP</p>
          </div>
        </div>

        <div className="mt-4 text-sm text-gray-500">
          <p>
            <span className="font-medium">Data Sources:</span>{' '}
            {envData?.dataSources?.join(', ') || 'CHIRPS, NASA POWER, SMAP'}
          </p>
        </div>
      </div>

      {/* Export & Verification Section */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
          <ShieldCheckIcon className="h-5 w-5 mr-2" />
          Reporting & Verification
        </h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button
            onClick={() => api.exportReport(selectedLand.id, 'verification', 'pdf')}
            className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg hover:bg-emerald-100 transition-colors"
          >
            <p className="font-medium text-emerald-700">PDF Report</p>
            <p className="text-sm text-emerald-600">Auditor-ready</p>
          </button>
          
          <button
            onClick={() => api.exportReport(selectedLand.id, 'data', 'csv')}
            className="p-4 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
          >
            <p className="font-medium text-blue-700">CSV Export</p>
            <p className="text-sm text-blue-600">Time-series data</p>
          </button>
          
          <button
            onClick={() => api.exportReport(selectedLand.id, 'boundaries', 'geojson')}
            className="p-4 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 transition-colors"
          >
            <p className="font-medium text-purple-700">GeoJSON</p>
            <p className="text-sm text-purple-600">Land boundaries</p>
          </button>
          
          <button
            onClick={() => api.exportReport(selectedLand.id, 'summary', 'pdf')}
            className="p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <p className="font-medium text-gray-700">Verification Summary</p>
            <p className="text-sm text-gray-600">Methodology & confidence</p>
          </button>
        </div>

        {/* BACKEND INTEGRATION POINT:
        Verification status and audit trail */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex justify-between items-center">
            <div>
              <p className="font-medium">Verification Status</p>
              <p className="text-sm text-gray-600">
                Last verified: 2024-01-10 • Next due: 2024-07-10
              </p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-emerald-700">
                {selectedLand.confidenceScore}%
              </p>
              <p className="text-sm text-gray-600">Confidence Score</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandDetailPanel;