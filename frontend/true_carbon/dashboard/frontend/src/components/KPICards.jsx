import React from 'react';
import { useDashboard } from '../context/DashboardContext';
import { 
  GlobeAltIcon, 
  CloudIcon, 
  CheckCircleIcon, 
  ChartBarIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline';

const KPICards = () => {
  const { kpiData, loading, alerts } = useDashboard();

  if (loading || !kpiData) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="bg-white rounded-xl shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    );
  }

  const cards = [
    {
      title: "Total Land Area",
      value: `${kpiData.totalLandArea.toLocaleString()} ha`,
      icon: GlobeAltIcon,
      color: "bg-blue-500",
      description: "📍 Where is the land?",
      // BACKEND INTEGRATION POINT:
      // Data fetched from /api/kpis?dateRange=&location=
      // In production: Real-time aggregation from PostGIS
    },
    {
      title: "Carbon Credits",
      value: `${kpiData.carbonGenerated.toLocaleString()} tCO₂e`,
      subValue: `of ${kpiData.totalCarbonCredits.toLocaleString()} total`,
      icon: CloudIcon,
      color: "bg-emerald-500",
      description: "🌿 How much carbon is being generated?",
      // BACKEND INTEGRATION POINT:
      // Carbon calculated using IPCC Tier 2 methodology
      // Biomass = NDVI × allometric equations
    },
    {
      title: "Active Projects",
      value: kpiData.activeProjects,
      icon: ChartBarIcon,
      color: "bg-purple-500",
      description: "📊 Project portfolio overview",
    },
    {
      title: "Verified %",
      value: `${kpiData.verifiedPercent}%`,
      icon: CheckCircleIcon,
      color: kpiData.verifiedPercent >= 80 ? "bg-green-500" : "bg-yellow-500",
      description: "✅ Is the data verifiable?",
      // BACKEND INTEGRATION POINT:
      // Verification status from auditor submissions
      // Blockchain verification integration point
    },
    {
      title: "Avg NDVI Δ",
      value: kpiData.avgNDVIChange >= 0 ? `+${kpiData.avgNDVIChange}` : kpiData.avgNDVIChange,
      icon: ChartBarIcon,
      color: kpiData.avgNDVIChange >= 0 ? "bg-emerald-500" : "bg-red-500",
      description: "📈 Is vegetation improving or degrading?",
      trend: kpiData.avgNDVIChange >= 0 ? "positive" : "negative",
      // BACKEND INTEGRATION POINT:
      // NDVI trend calculated from Sentinel-2 time-series
      // Real-time Google Earth Engine processing
    }
  ];

  return (
    <div className="mb-8">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-gray-900">
          Carbon Credit Dashboard
        </h2>
        {alerts.length > 0 && (
          <div className="flex items-center text-red-600">
            <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
            <span className="font-semibold">{alerts.length} High Priority Alerts</span>
          </div>
        )}
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {cards.map((card, index) => (
          <div 
            key={index} 
            className="bg-white rounded-xl shadow-lg p-6 border border-gray-100 hover:shadow-xl transition-shadow duration-300"
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 rounded-lg ${card.color} bg-opacity-10`}>
                <card.icon className={`h-6 w-6 ${card.color.replace('bg-', 'text-')}`} />
              </div>
              <span className="text-sm font-medium text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                {card.description}
              </span>
            </div>
            
            <h3 className="text-sm font-medium text-gray-500 mb-1">{card.title}</h3>
            <div className="flex items-end">
              <p className="text-3xl font-bold text-gray-900">{card.value}</p>
              {card.subValue && (
                <p className="text-sm text-gray-500 ml-2 mb-1">/ {card.subValue}</p>
              )}
            </div>
            
            {card.trend && (
              <div className="mt-4 flex items-center">
                <span className={`text-sm font-medium ${
                  card.trend === 'positive' ? 'text-emerald-600' : 'text-red-600'
                }`}>
                  {card.trend === 'positive' ? '▲ Improving' : '▼ Declining'}
                </span>
                <span className="text-xs text-gray-500 ml-2">
                  Since last quarter
                </span>
              </div>
            )}
            
            <div className="mt-4 pt-4 border-t border-gray-100">
              <p className="text-xs text-gray-500">
                {/* BACKEND INTEGRATION POINT:
                Tooltip showing data source and last update
                Real implementation: show actual update timestamp */}
                Updated: Just now • Source: Sentinel-2
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default KPICards;