/**
 * Chart.js data transformation utilities
 */

import type { NDVIDataPoint } from '@/types/ndvi';
import type { CarbonDataPoint } from '@/types/carbon';
import type { TimeSeriesData } from '@/types/dashboard';

/**
 * Transform NDVI data to Chart.js format
 */
export function formatNDVIChartData(data: NDVIDataPoint[]): TimeSeriesData {
  return {
    labels: data.map((point) => point.date),
    datasets: [
      {
        label: 'NDVI',
        data: data.map((point) => point.ndvi),
        borderColor: '#627BC1',
        backgroundColor: 'rgba(98, 123, 193, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 2,
      },
    ],
  };
}

/**
 * Transform carbon data to Chart.js format
 */
export function formatCarbonChartData(data: CarbonDataPoint[]): TimeSeriesData {
  return {
    labels: data.map((point) => point.date),
    datasets: [
      {
        label: 'CO2 (tonnes)',
        data: data.map((point) => point.co2_total_tonnes),
        borderColor: '#31a354',
        backgroundColor: 'rgba(49, 163, 84, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 2,
      },
    ],
  };
}

/**
 * Transform carbon data with confidence intervals
 */
export function formatCarbonWithConfidenceData(data: CarbonDataPoint[]): TimeSeriesData {
  const hasConfidenceData = data.some((d) => d.confidence_interval_lower && d.confidence_interval_upper);

  const datasets = [
    {
      label: 'CO2 Estimate',
      data: data.map((point) => point.co2_total_tonnes),
      borderColor: '#31a354',
      backgroundColor: 'rgba(49, 163, 84, 0.1)',
      fill: false,
      tension: 0.4,
      borderWidth: 2,
    },
  ];

  if (hasConfidenceData) {
    datasets.push({
      label: 'Upper Bound (95% CI)',
      data: data.map((point) => point.confidence_interval_upper || point.co2_total_tonnes),
      borderColor: 'rgba(49, 163, 84, 0.3)',
      fill: false,
      tension: 0.4,
      pointRadius: 0,
      borderWidth: 1,
      borderDash: [5, 5],
    } as any);

    datasets.push({
      label: 'Lower Bound (95% CI)',
      data: data.map((point) => point.confidence_interval_lower || point.co2_total_tonnes),
      borderColor: 'rgba(49, 163, 84, 0.3)',
      fill: false,
      tension: 0.4,
      pointRadius: 0,
      borderWidth: 1,
      borderDash: [5, 5],
    } as any);
  }

  return {
    labels: data.map((point) => point.date),
    datasets,
  };
}

/**
 * Transform environmental data to Chart.js format (multiple metrics)
 */
export function formatEnvironmentalChartData(ndviData: NDVIDataPoint[]): TimeSeriesData {
  return {
    labels: ndviData.map((point) => point.date),
    datasets: [
      {
        label: 'NDVI',
        data: ndviData.map((point) => point.ndvi * 100), // Scale to 0-100
        borderColor: '#627BC1',
        backgroundColor: 'rgba(98, 123, 193, 0.1)',
        fill: false,
        tension: 0.4,
        borderWidth: 2,
      },
    ],
  };
}
