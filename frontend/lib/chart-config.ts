/**
 * Chart.js configuration and utilities
 */

import { Chart as ChartJS, registerables } from 'chart.js';
import type { ChartOptions } from 'chart.js';

// Register Chart.js components
ChartJS.register(...registerables);

// NDVI Chart Options
export const NDVI_CHART_OPTIONS: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: {
      display: true,
      position: 'top' as const,
    },
    title: {
      display: true,
      text: 'NDVI Time Series',
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 1,
      ticks: {
        stepSize: 0.2,
      },
    },
  },
};

// Carbon Chart Options
export const CARBON_CHART_OPTIONS: ChartOptions<'bar'> = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: {
      display: true,
      position: 'top' as const,
    },
    title: {
      display: true,
      text: 'Carbon Accumulation',
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: function (value: any) {
          return value + ' tonnes';
        },
      },
    },
  },
};

// Environmental Chart Options
export const ENV_CHART_OPTIONS: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: {
      display: true,
      position: 'top' as const,
    },
    title: {
      display: true,
      text: 'Environmental Metrics',
    },
  },
  scales: {
    y: {
      beginAtZero: true,
    },
  },
};
