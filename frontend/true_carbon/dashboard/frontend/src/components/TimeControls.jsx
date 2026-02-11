import React from 'react';
import { useDashboard } from '../context/DashboardContext';
import { CalendarDaysIcon } from '@heroicons/react/24/outline';

const TimeControls = () => {
  const { dateRange, setDateRange } = useDashboard();

  const timeRanges = [
    { id: '3months', label: 'Last 3 Months' },
    { id: '6months', label: 'Last 6 Months' },
    { id: '1year', label: 'Last 1 Year' },
    { id: 'all', label: 'All Time' },
    { id: 'custom', label: 'Custom Range' }
  ];

  const handleDateRangeChange = (range) => {
    setDateRange(range);
    
    // BACKEND INTEGRATION POINT:
    // In production: Debounce API calls and update all components
    // await Promise.all([
    //   api.getKPIs({ dateRange: range }),
    //   api.getLands({ dateRange: range }),
    //   api.getAlerts()
    // ]);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <CalendarDaysIcon className="h-6 w-6 text-gray-700 mr-3" />
          <div>
            <h2 className="text-xl font-bold text-gray-900">Time Range Analysis</h2>
            <p className="text-gray-600">
              Select timeframe to update KPIs, maps, and charts
            </p>
          </div>
        </div>
        
        <div className="text-sm text-gray-500 bg-gray-100 px-3 py-2 rounded-lg">
          <span className="font-medium">Current Range:</span>{' '}
          {timeRanges.find(t => t.id === dateRange)?.label}
        </div>
      </div>

      <div className="grid grid-cols-5 gap-3">
        {timeRanges.map((range) => (
          <button
            key={range.id}
            onClick={() => handleDateRangeChange(range.id)}
            className={`py-4 px-4 rounded-lg text-center transition-all duration-200 ${
              dateRange === range.id
                ? 'bg-emerald-50 border-2 border-emerald-500 text-emerald-700 font-semibold'
                : 'bg-gray-50 border border-gray-200 text-gray-700 hover:bg-gray-100 hover:border-gray-300'
            }`}
          >
            {range.label}
          </button>
        ))}
      </div>

      {dateRange === 'custom' && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Start Date
              </label>
              <input
                type="date"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                defaultValue="2023-01-01"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                End Date
              </label>
              <input
                type="date"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                defaultValue="2024-01-01"
              />
            </div>
          </div>
          <div className="mt-4 flex justify-end">
            <button className="px-6 py-3 bg-emerald-600 text-white font-medium rounded-lg hover:bg-emerald-700 transition-colors">
              Apply Custom Range
            </button>
          </div>
        </div>
      )}

      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="flex items-center text-sm text-gray-500">
          <div className="h-2 w-2 bg-emerald-500 rounded-full mr-2"></div>
          <p>
            {/* BACKEND INTEGRATION POINT:
            Show actual API call status and data freshness */}
            Changing time range updates: KPIs • Map Colors • Time-series Charts • Risk Assessments
          </p>
        </div>
        <p className="text-xs text-gray-400 mt-2 ml-4">
          All time-series data synchronized to selected range for consistent audit trail
        </p>
      </div>
    </div>
  );
};

export default TimeControls;