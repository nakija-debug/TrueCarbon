# Phase 5: Satellite Health Monitoring Implementation Guide

## Overview

Phase 5 implements comprehensive satellite health monitoring and data source availability tracking for the TrueCarbon platform. This phase monitors three primary satellite data sources:

- **Sentinel-2**: Multispectral satellite imagery (10-60m resolution)
- **Landsat-8**: Multispectral satellite imagery (30m resolution)  
- **ERA5-Land**: Reanalysis weather dataset (0.1° resolution)

## Architecture

### Components

#### 1. Database Model: `SatelliteStatus`

Location: `backend/app/models/satellite_status.py`

**Fields:**
- `satellite_name`: Unique identifier (sentinel-2, landsat-8, era5-land)
- `status`: Operational status (operational, degraded, offline, unknown)
- `coverage_percent`: Data availability percentage (0-100)
- `accuracy_percent`: Quality accuracy metric (0-100)
- `data_quality`: Quality level (high, medium, low, unknown)
- `uptime_percent`: Historical uptime percentage (0-100)
- `last_update`: Timestamp of last health check
- `metadata`: JSON field for additional metrics (cloud cover %, latency ms, error messages, etc.)

**Key Properties:**
- `is_operational`: Boolean check if satellite is operational
- `is_degraded`: Boolean check if satellite is degraded
- `is_offline`: Boolean check if satellite is offline

#### 2. Pydantic Schemas: Satellite Health Responses

Location: `backend/app/schemas/satellite.py`

**Enums:**
- `SatelliteStatusEnum`: operational, degraded, offline, unknown
- `DataQualityEnum`: high, medium, low, unknown

**Response Schemas:**
- `SatelliteHealthResponse`: Individual satellite metrics
- `SatelliteHealthListResponse`: List of all satellites with aggregates

#### 3. Service Layer: `SatelliteHealthService`

Location: `backend/app/services/satellite_health_service.py`

**Key Methods:**

```python
# Check individual satellite health
async def check_sentinel2_health() -> Dict[str, any]
async def check_landsat8_health() -> Dict[str, any]
async def check_era5_health() -> Dict[str, any]

# Batch update all satellites
async def update_all_satellite_status(db: AsyncSession) -> None

# Retrieve health summary
async def get_satellite_health_summary(db: AsyncSession) -> Dict[str, any]

# Historical data retrieval
async def get_health_history(
    db: AsyncSession,
    satellite_name: Optional[str] = None,
    days: int = 7
) -> List[Dict[str, Any]]
```

**Health Check Logic:**

The service evaluates satellite health by:

1. **Sentinel-2**: Queries last 30 days of images, filters by cloud cover
   - Low cloud images (< 20%): High-quality indicators
   - Coverage % = (low_cloud_count / total_count) × 100
   - Status: operational if coverage ≥ 90%, degraded if ≥ 50%

2. **Landsat-8**: Queries last 30 days with quality flags
   - Good quality = cloud cover < 25%
   - Coverage % = (good_count / total_count) × 100
   - Same thresholds as Sentinel-2

3. **ERA5-Land**: Monitors temporal continuity
   - Expected: 720 hourly records in 30 days
   - Status: operational if availability ≥ 95%
   - Higher accuracy (99%) due to reanalysis consistency

#### 4. API Endpoints: `satellites.py`

Location: `backend/app/api/v1/satellites.py`

**Endpoints:**

1. **GET /satellites/health**
   - Returns: All satellite health metrics with aggregates
   - Query Parameter: `refresh=true` to trigger live health check
   - Response: `SatelliteHealthListResponse`
   - Status Codes: 200, 401, 429, 500

2. **GET /satellites/health/{satellite_name}**
   - Returns: Health metrics for specific satellite
   - Path Parameter: satellite_name (sentinel-2, landsat-8, era5-land)
   - Response: `SatelliteHealthResponse`
   - Status Codes: 200, 401, 404, 500

3. **POST /satellites/health/refresh**
   - Triggers: Manual refresh of all satellite health checks
   - Status Code: 202 Accepted
   - Returns: Status with task timestamp
   - Raises: 401, 403, 429, 500

### Integration with Earth Engine

The `SatelliteHealthService` integrates with Earth Engine API via `EarthEngineManager`:

```python
# Manager initialization
self.ee_manager = EarthEngineManager.get_instance()
self.ee_manager.initialize()

# Collections queried
"COPERNICUS/S2_SR" - Sentinel-2 Surface Reflectance
"LANDSAT/LC08/C02/T1_L2" - Landsat-8 Level-2 Collection 2
"ECMWF/ERA5_LAND/HOURLY" - ERA5-Land Hourly Reanalysis
```

**Error Handling:**

- **EarthEngineQuotaError**: Raised when API quota exceeded (429 HTTP status)
- **SatelliteHealthCheckError**: Raised on health check failures
- **EarthEngineError**: Parent exception for general API errors

## Database Migration

**Migration File:** `backend/alembic/versions/a1b2c3d4e5f6_add_satellite_status_model.py`

**Creates:**
- `satellite_status` table with:
  - Primary key: `id`
  - Unique constraint: `satellite_name`
  - Indexes: satellite_name, status, created_at, id
  - JSON metadata support
  - Timezone-aware timestamps

**Up Migration:** Creates table and indexes
**Down Migration:** Drops table and indexes for rollback

## API Response Examples

### Get All Satellite Health

**Request:**
```
GET /api/v1/satellites/health
```

**Response:**
```json
{
  "satellites": [
    {
      "satellite_name": "sentinel-2",
      "status": "operational",
      "coverage_percent": 95.5,
      "accuracy_percent": 92.3,
      "data_quality": "high",
      "last_update": "2024-01-15T10:30:00Z",
      "uptime_percent": 98.7,
      "metadata": {
        "total_images": 150,
        "low_cloud_images": 143,
        "average_cloud_cover": 4.5,
        "check_date": "2024-01-15T10:30:00Z",
        "date_range_days": 30
      }
    },
    {
      "satellite_name": "landsat-8",
      "status": "operational",
      "coverage_percent": 92.1,
      "accuracy_percent": 88.9,
      "data_quality": "high",
      "last_update": "2024-01-15T10:30:00Z",
      "uptime_percent": 97.2,
      "metadata": {
        "total_images": 89,
        "good_quality_images": 82,
        "average_cloud_cover": 7.9,
        "check_date": "2024-01-15T10:30:00Z",
        "date_range_days": 30
      }
    },
    {
      "satellite_name": "era5-land",
      "status": "operational",
      "coverage_percent": 99.7,
      "accuracy_percent": 99.0,
      "data_quality": "high",
      "last_update": "2024-01-15T10:30:00Z",
      "uptime_percent": 99.5,
      "metadata": {
        "total_records": 717,
        "expected_records": 720,
        "availability_percent": 99.58,
        "check_date": "2024-01-15T10:30:00Z",
        "record_frequency": "hourly"
      }
    }
  ],
  "total_satellites": 3,
  "operational_count": 3,
  "degraded_count": 0,
  "offline_count": 0,
  "average_uptime": 98.47,
  "last_check": "2024-01-15T10:30:00Z"
}
```

### Get Specific Satellite

**Request:**
```
GET /api/v1/satellites/health/sentinel-2
```

**Response:**
```json
{
  "satellite_name": "sentinel-2",
  "status": "operational",
  "coverage_percent": 95.5,
  "accuracy_percent": 92.3,
  "data_quality": "high",
  "last_update": "2024-01-15T10:30:00Z",
  "uptime_percent": 98.7,
  "metadata": {
    "total_images": 150,
    "low_cloud_images": 143,
    "average_cloud_cover": 4.5,
    "check_date": "2024-01-15T10:30:00Z",
    "date_range_days": 30
  }
}
```

### Trigger Manual Refresh

**Request:**
```
POST /api/v1/satellites/health/refresh
```

**Response (202 Accepted):**
```json
{
  "status": "accepted",
  "message": "Satellite health check in progress",
  "timestamp": "2024-01-15T10:35:00Z"
}
```

## Error Responses

### 429 - Quota Exceeded

```json
{
  "detail": "Earth Engine quota exceeded, try again later"
}
```

### 500 - Health Check Failed

```json
{
  "detail": "Health check failed: Connection timeout to Earth Engine"
}
```

### 404 - Satellite Not Found

```json
{
  "detail": "Satellite 'unknown-sat' not found. Valid options: sentinel-2, landsat-8, era5-land"
}
```

## Health Check Frequencies

**Recommended Schedule:**
- Manual checks (user-triggered via `refresh=true`): On-demand
- Automatic checks: Every 60 minutes
- Database retention: 30 days minimum history

**Data Updates:**
- Each check updates `last_update` timestamp
- Historical data preserved through timestamps
- Metadata includes Earth Engine API query details

## Implementation Steps

1. **Database Setup**
   ```bash
   cd backend
   alembic upgrade head
   ```

2. **Dependencies**
   - FastAPI (already installed)
   - SQLAlchemy (already installed)
   - Earth Engine API library: `ee` (if not already installed)

3. **Environment Configuration**
   - Earth Engine credentials configured in `EARTHENGINE_*` env vars
   - Database connection string configured

4. **Testing**
   ```bash
   pytest backend/tests/test_satellites.py -v
   ```

5. **API Documentation**
   - Auto-generated at `http://localhost:8000/docs`
   - Interactive Swagger UI for testing endpoints

## Monitoring and Alerts

The satellite health monitoring system enables:

1. **Real-time Status Monitoring**: Check current operational status anytime
2. **Data Quality Assessment**: Identify degraded data sources before using in analysis
3. **Availability Tracking**: Monitor satellite constellation reliability
4. **Historical Analysis**: Track satellite performance over time
5. **Quota Management**: Detect Earth Engine API quota issues

## Future Enhancements

1. **Automated Alerting**
   - Email notifications when satellites go offline/degraded
   - Slack integration for DevOps team
   - SMS alerts for critical issues

2. **Predictive Health**
   - Machine learning models to predict satellite failures
   - Preventive maintenance alerts

3. **Multi-region Monitoring**
   - Region-specific health checks
   - Geographic coverage analysis

4. **Advanced Metrics**
   - Latency tracking for API responses
   - Data consistency metrics
   - Multi-spectral band health assessment

5. **Frontend Integration**
   - Dashboard visualization of satellite status
   - Historical trend charts
   - Coverage maps by region

## Troubleshooting

### Issue: "Earth Engine quota exceeded"
- **Cause**: Too many API calls to Earth Engine
- **Solution**: 
  - Increase check interval (reduce frequency)
  - Contact Google Cloud to increase quota
  - Check for other services using Earth Engine quota

### Issue: "Satellite not found in database"
- **Cause**: Migration not applied or first health check not run
- **Solution**:
  - Run: `alembic upgrade head`
  - Trigger manual refresh: `POST /satellites/health/refresh`

### Issue: Connection timeout to Earth Engine
- **Cause**: Network connectivity or Earth Engine service down
- **Solution**:
  - Check internet connectivity
  - Verify Earth Engine is accessible: https://earthengine.google.com/
  - Check Earth Engine credentials are valid

## References

- [Google Earth Engine API Docs](https://developers.google.com/earth-engine)
- [Sentinel-2 Collection](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED)
- [Landsat-8 Collection](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2)
- [ERA5-Land Dataset](https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_MONTHLY)
