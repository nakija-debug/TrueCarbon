const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Load mock data
const mockLands = require('./data/mockLands.json');
const mockKpis = require('./data/mockKpis.json');
const mockTimeSeries = require('./data/mockTimeSeries.json');

// ============================================
// BACKEND ROUTES
// ============================================

// GET /api/kpis - Returns KPI dashboard metrics
// BACKEND INTEGRATION POINT:
// This will be replaced with real database query from PostgreSQL
// Satellite data aggregation from Google Earth Engine will be processed here
app.get('/api/kpis', (req, res) => {
  const { dateRange, location } = req.query;
  
  // In production: Query database with filters
  // const kpis = await db.query(`
  //   SELECT 
  //     SUM(area_ha) as totalLandArea,
  //     SUM(total_carbon_credits) as totalCarbonCredits,
  //     COUNT(*) as activeProjects,
  //     AVG(verified_percent) as verifiedPercent,
  //     AVG(ndvi_trend) as avgNDVIChange
  //   FROM projects
  //   WHERE start_date >= $1 AND location = $2
  // `, [dateRange, location]);
  
  // For now, return mock data with filter simulation
  let response = { ...mockKpis };
  
  if (dateRange === '3months') {
    response.carbonGenerated = 12500;
    response.avgNDVIChange = 0.045;
  }
  
  res.json(response);
});

// GET /api/lands - Returns GeoJSON land boundaries
// BACKEND INTEGRATION POINT:
// Fetch land parcel boundaries from PostGIS (PostgreSQL with GIS extensions)
// Real satellite imagery will overlay these boundaries
app.get('/api/lands', (req, res) => {
  const { dateRange, verifiedOnly } = req.query;
  
  // In production: Query PostGIS for land geometries
  // const lands = await db.query(`
  //   SELECT 
  //     ST_AsGeoJSON(geometry) as geojson,
  //     project_id, name, area_ha, location,
  //     verification_status, ndvi_trend
  //   FROM land_parcels
  //   WHERE last_updated >= $1
  // `, [dateRange]);
  
  let filteredLands = mockLands.features;
  
  if (verifiedOnly === 'true') {
    filteredLands = filteredLands.filter(land => 
      land.properties.verificationStatus === 'Verified'
    );
  }
  
  if (dateRange === '3months') {
    // Simulate recent data
    filteredLands = filteredLands.map(land => ({
      ...land,
      properties: {
        ...land.properties,
        ndviTrend: land.properties.ndviTrend * 1.2 // Simulate improvement
      }
    }));
  }
  
  res.json({
    type: "FeatureCollection",
    features: filteredLands
  });
});

// GET /api/ndvi/:landId - Returns NDVI time-series for specific land
// BACKEND INTEGRATION POINT:
// Fetch time-series NDVI data from Google Earth Engine API
// Process Sentinel-2/Landsat imagery for vegetation index history
app.get('/api/ndvi/:landId', (req, res) => {
  const { landId } = req.params;
  const { startDate, endDate } = req.query;
  
  // In production: Query time-series database
  // const ndviData = await db.query(`
  //   SELECT date, ndvi_value, confidence
  //   FROM ndvi_measurements
  //   WHERE land_id = $1 
  //     AND date BETWEEN $2 AND $3
  //   ORDER BY date
  // `, [landId, startDate, endDate]);
  
  // Return mock time-series data
  res.json({
    landId,
    ndvi: mockTimeSeries.ndvi,
    landUse: mockTimeSeries.landUse,
    timeframe: { startDate, endDate }
  });
});

// GET /api/carbon/:landId - Returns carbon accumulation data
// BACKEND INTEGRATION POINT:
// Calculate carbon using IPCC Tier 2 methodology
// Biomass = NDVI × allometric equations × conversion factors
app.get('/api/carbon/:landId', (req, res) => {
  const { landId } = req.params;
  
  // In production: Calculate from biomass measurements
  // const carbonData = await db.query(`
  //   SELECT 
  //     measurement_date,
  //     baseline_carbon,
  //     additional_carbon,
  //     calculation_method,
  //     confidence_interval
  //   FROM carbon_measurements
  //   WHERE land_id = $1
  //   ORDER BY measurement_date
  // `, [landId]);
  
  res.json({
    landId,
    carbon: mockTimeSeries.carbon,
    methodology: "IPCC Tier 2",
    confidence: 0.92
  });
});

// GET /api/environment/:landId - Returns environmental data
// BACKEND INTEGRATION POINT:
// Fetch climate data from NASA POWER API or CHIRPS rainfall
// Soil moisture from SMAP satellite data
app.get('/api/environment/:landId', (req, res) => {
  const { landId } = req.params;
  
  res.json({
    landId,
    rainfall: mockTimeSeries.environment.rainfall,
    temperature: mockTimeSeries.environment.temperature,
    soilMoisture: mockTimeSeries.environment.soilMoisture,
    dataSources: ["CHIRPS Rainfall", "NASA POWER", "SMAP Soil Moisture"]
  });
});

// POST /api/reports/export - Triggers report generation
// BACKEND INTEGRATION POINT:
// Generate PDF reports with charts using pdfkit/chart.js-node
// Export CSV/GeoJSON for auditors
app.post('/api/reports/export', (req, res) => {
  const { landId, reportType, format } = req.body;
  
  // In production: Generate report files
  // await reportService.generate({
  //   landId,
  //   type: reportType,
  //   format,
  //   includeCharts: true,
  //   verificationData: true
  // });
  
  res.json({
    success: true,
    message: `Report generation initiated for ${landId}`,
    downloadUrl: `/api/reports/download/${Date.now()}`,
    estimatedTime: "30 seconds"
  });
});

// GET /api/alerts - Returns system alerts and risks
// BACKEND INTEGRATION POINT:
// Monitor NDVI drops, data gaps, verification deadlines
// Integrate with alerting system (email/Slack)
app.get('/api/alerts', (req, res) => {
  res.json({
    highPriority: [
      {
        id: "alert-001",
        type: "NDVI_DROP",
        landId: "land-004",
        severity: "HIGH",
        message: "NDVI dropped 15% in Colorado Forest",
        date: "2024-01-15",
        actionRequired: true
      },
      {
        id: "alert-002",
        type: "VERIFICATION_PENDING",
        landId: "land-002",
        severity: "MEDIUM",
        message: "Verification overdue by 14 days",
        date: "2024-01-10",
        actionRequired: true
      }
    ],
    mediumPriority: [
      {
        id: "alert-003",
        type: "DATA_GAP",
        landId: "land-001",
        severity: "MEDIUM",
        message: "7-day satellite data gap detected",
        date: "2024-01-12",
        actionRequired: false
      }
    ]
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🌍 Carbon MRV Backend running on port ${PORT}`);
  console.log(`📊 API available at http://localhost:${PORT}/api/kpis`);
  console.log(`🗺️  Map data at http://localhost:${PORT}/api/lands`);
});