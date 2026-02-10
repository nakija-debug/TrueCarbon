import React from 'react';
import { DashboardProvider } from './context/DashboardContext';
import KPICards from './components/KPICards';
import InteractiveMap from './components/InteractiveMap';
import TimeControls from './components/TimeControls';
import LandDetailPanel from './components/LandDetailPanel';
import PortfolioView from './components/PortfolioView';
import VerificationPanel from './components/VerificationPanel';

function App() {
  return (
    <DashboardProvider>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  🌍 Carbon Credit MRV Dashboard
                </h1>
                <p className="text-gray-600">
                  Audit-grade Monitoring, Reporting & Verification • Real-time Satellite Data
                </p>
              </div>
              <div className="flex items-center space-x-4">
                <span className="px-3 py-1 bg-emerald-100 text-emerald-800 text-sm font-medium rounded-full">
                  Satellite: Sentinel-2
                </span>
                <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
                  IPCC Tier 2 Methodology
                </span>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* KPI Cards Row */}
          <KPICards />
          
          {/* Time Controls */}
          <TimeControls />
          
          {/* Map & Detail Panel Row */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
            <div className="lg:col-span-2">
              <InteractiveMap />
            </div>
            <div>
              <LandDetailPanel />
            </div>
          </div>
          
          {/* Portfolio & Verification Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <PortfolioView />
            <VerificationPanel />
          </div>
          
          {/* Audit Trail Footer */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <div className="text-sm text-gray-500">
              <p className="font-medium mb-2">Audit Trail & Data Sources:</p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="font-semibold">Satellite Sources</p>
                  <ul className="list-disc pl-5 mt-1">
                    <li>Sentinel-2 (10m NDVI)</li>
                    <li>Landsat 8/9 (30m backup)</li>
                    <li>Planet Scope (3m high-res)</li>
                  </ul>
                </div>
                <div>
                  <p className="font-semibold">Climate Data</p>
                  <ul className="list-disc pl-5 mt-1">
                    <li>CHIRPS Rainfall</li>
                    <li>NASA POWER Temperature</li>
                    <li>SMAP Soil Moisture</li>
                  </ul>
                </div>
                <div>
                  <p className="font-semibold">Verification Standards</p>
                  <ul className="list-disc pl-5 mt-1">
                    <li>IPCC 2006 Guidelines</li>
                    <li>Verified Carbon Standard</li>
                    <li>Gold Standard</li>
                  </ul>
                </div>
              </div>
              <p className="mt-4 text-xs">
                Last full system audit: 2024-01-15 • Data updated hourly • 
                Confidence scores calculated using Monte Carlo simulation
              </p>
            </div>
          </div>
        </main>
      </div>
    </DashboardProvider>
  );
}

export default App;