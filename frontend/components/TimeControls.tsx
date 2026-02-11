'use client';

import React, { useState } from 'react';
import { CalendarDaysIcon } from '@heroicons/react/24/outline';

interface TimeControlsProps {
  onRangeChange?: (range: { start: Date; end: Date }) => void;
}

interface TimeRange {
  id: string;
  label: string;
}

const TimeControls: React.FC<TimeControlsProps> = ({
  onRangeChange,
}) => {
  const [rangeType, setRangeType] = useState('3months');
  const [customStart, setCustomStart] = useState('2023-01-01');
  const [customEnd, setCustomEnd] = useState('2024-01-01');

  const timeRanges: TimeRange[] = [
    { id: '3months', label: 'Last 3 Months' },
    { id: '6months', label: 'Last 6 Months' },
    { id: '1year', label: 'Last 1 Year' },
    { id: 'all', label: 'All Time' },
    { id: 'custom', label: 'Custom Range' },
  ];

  const getDateRange = (rangeId: string) => {
    const now = new Date();
    switch (rangeId) {
      case '3months':
        return {
          start: new Date(now.setMonth(now.getMonth() - 3)),
          end: new Date(),
        };
      case '6months':
        return {
          start: new Date(now.setMonth(now.getMonth() - 6)),
          end: new Date(),
        };
      case '1year':
        return {
          start: new Date(now.setFullYear(now.getFullYear() - 1)),
          end: new Date(),
        };
      case 'all':
        return {
          start: new Date('2020-01-01'),
          end: new Date(),
        };
      case 'custom':
        return {
          start: new Date(customStart),
          end: new Date(customEnd),
        };
      default:
        return {
          start: new Date(now.setMonth(now.getMonth() - 3)),
          end: new Date(),
        };
    }
  };

  const handleDateRangeChange = (range: string) => {
    setRangeType(range);
    const dateRange = getDateRange(range);
    if (onRangeChange) {
      onRangeChange(dateRange);
    }
  };

  const handleApplyCustomRange = () => {
    handleDateRangeChange('custom');
  };

  const currentLabel = timeRanges.find((t) => t.id === rangeType)?.label;

  return (
    <div className="mb-8 rounded-xl bg-white p-6 shadow-lg">
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center">
          <CalendarDaysIcon className="mr-3 h-6 w-6 text-gray-700" />
          <div>
            <h2 className="text-xl font-bold text-gray-900">
              Time Range Analysis
            </h2>
            <p className="text-gray-600">
              Select timeframe to update KPIs, maps, and charts
            </p>
          </div>
        </div>

        <div className="rounded-lg bg-gray-100 px-3 py-2 text-sm text-gray-500">
          <span className="font-medium">Current Range:</span> {currentLabel}
        </div>
      </div>

      <div className="grid grid-cols-5 gap-3">
        {timeRanges.map((range) => (
          <button
            key={range.id}
            onClick={() => handleDateRangeChange(range.id)}
            className={`rounded-lg px-4 py-4 text-center transition-all duration-200 ${
              rangeType === range.id
                ? 'border-2 border-emerald-500 bg-emerald-50 font-semibold text-emerald-700'
                : 'border border-gray-200 bg-gray-50 text-gray-700 hover:border-gray-300 hover:bg-gray-100'
            }`}
          >
            {range.label}
          </button>
        ))}
      </div>

      {rangeType === 'custom' && (
        <div className="mt-6 rounded-lg border border-gray-200 bg-gray-50 p-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">
                Start Date
              </label>
              <input
                type="date"
                value={customStart}
                onChange={(e) => setCustomStart(e.target.value)}
                className="w-full rounded-lg border border-gray-300 p-3 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">
                End Date
              </label>
              <input
                type="date"
                value={customEnd}
                onChange={(e) => setCustomEnd(e.target.value)}
                className="w-full rounded-lg border border-gray-300 p-3 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>
          <div className="mt-4 flex justify-end">
            <button
              onClick={handleApplyCustomRange}
              className="rounded-lg bg-emerald-600 px-6 py-3 font-medium text-white transition-colors hover:bg-emerald-700"
            >
              Apply Custom Range
            </button>
          </div>
        </div>
      )}

      <div className="mt-6 border-t border-gray-200 pt-6">
        <div className="flex items-center text-sm text-gray-500">
          <div className="mr-2 h-2 w-2 rounded-full bg-emerald-500"></div>
          <p>
            Changing time range updates: KPIs • Map Colors • Time-series Charts •
            Risk Assessments
          </p>
        </div>
        <p className="ml-4 mt-2 text-xs text-gray-400">
          All time-series data synchronized to selected range for consistent audit
          trail
        </p>
      </div>
    </div>
  );
};

export default TimeControls;
