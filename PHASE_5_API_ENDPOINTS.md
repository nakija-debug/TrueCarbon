# Phase 5 API Endpoints: Satellite Health Monitoring

## Base URL
```
/api/v1/satellites
```

## Endpoints

### 1. Get All Satellite Health Metrics

**Endpoint:** `GET /satellites/health`

**Description:** Retrieve current operational status, coverage, and data quality for all monitored satellites.

**Authentication:** Required (Bearer Token)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `refresh` | boolean | false | If true, trigger live health check from Earth Engine |

**Response Model:** `SatelliteHealthListResponse`

**Status Codes:**
| Code | Description |
|------|-------------|
| 200 | Successfully retrieved health metrics |
| 401 | Unauthorized - invalid authentication |
| 429 | Too Many Requests - Earth Engine quota exceeded |
| 500 | Internal Server Error - health check failed |

**Example Request:**
```bash
# Get cached health status
GET /api/v1/satellites/health

# Trigger live health check
GET /api/v1/satellites/health?refresh=true
```

**Example Response (200 OK):**
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

**Error Responses:**

429 Response:
```json
{
  "detail": "Earth Engine quota exceeded, try again later"
}
```

500 Response:
```json
{
  "detail": "Failed to retrieve satellite health: Connection timeout to Earth Engine"
}
```

---

### 2. Get Specific Satellite Health

**Endpoint:** `GET /satellites/health/{satellite_name}`

**Description:** Retrieve health metrics for a specific satellite by name.

**Authentication:** Required (Bearer Token)

**Path Parameters:**
| Parameter | Type | Valid Values | Description |
|-----------|------|--------------|-------------|
| `satellite_name` | string | sentinel-2, landsat-8, era5-land | Name of the satellite |

**Response Model:** `SatelliteHealthResponse`

**Status Codes:**
| Code | Description |
|------|-------------|
| 200 | Successfully retrieved satellite health |
| 401 | Unauthorized - invalid authentication |
| 404 | Satellite not found |
| 500 | Internal Server Error |

**Example Requests:**
```bash
# Get Sentinel-2 health
GET /api/v1/satellites/health/sentinel-2

# Get Landsat-8 health
GET /api/v1/satellites/health/landsat-8

# Get ERA5-Land health
GET /api/v1/satellites/health/era5-land
```

**Example Response (200 OK):**
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

**Error Responses:**

404 Response:
```json
{
  "detail": "Satellite 'unknown-sat' not found. Valid options: sentinel-2, landsat-8, era5-land"
}
```

---

### 3. Trigger Manual Health Check Refresh

**Endpoint:** `POST /satellites/health/refresh`

**Description:** Manually trigger a comprehensive health check for all satellites using Earth Engine API.

**Authentication:** Required (Bearer Token)

**Request Body:** None

**Response Status:** `202 Accepted`

**Response Format:** JSON with task status

**Status Codes:**
| Code | Description |
|------|-------------|
| 202 | Health check accepted and in progress |
| 401 | Unauthorized - invalid authentication |
| 403 | Forbidden - insufficient permissions |
| 429 | Too Many Requests - Earth Engine quota exceeded |
| 500 | Internal Server Error |

**Example Request:**
```bash
POST /api/v1/satellites/health/refresh
Content-Type: application/json
Authorization: Bearer YOUR_AUTH_TOKEN
```

**Example Response (202 Accepted):**
```json
{
  "status": "accepted",
  "message": "Satellite health check in progress",
  "timestamp": "2024-01-15T10:35:00Z"
}
```

**Error Responses:**

429 Response:
```json
{
  "detail": "Earth Engine quota exceeded, try again later"
}
```

500 Response:
```json
{
  "detail": "Failed to refresh satellite health: Service temporarily unavailable"
}
```

---

## Data Models

### SatelliteStatusEnum
Valid status values:
- `operational` - Satellite is fully operational
- `degraded` - Satellite is partially operational or has quality issues
- `offline` - Satellite is not available
- `unknown` - Status cannot be determined

### DataQualityEnum
Valid quality levels:
- `high` - Excellent coverage and accuracy
- `medium` - Moderate coverage and accuracy
- `low` - Poor coverage or accuracy
- `unknown` - Cannot assess quality

### SatelliteHealthResponse

```json
{
  "satellite_name": "string (sentinel-2|landsat-8|era5-land)",
  "status": "string (operational|degraded|offline|unknown)",
  "coverage_percent": "number (0-100)",
  "accuracy_percent": "number (0-100)",
  "data_quality": "string (high|medium|low|unknown)",
  "last_update": "string (ISO 8601 timestamp)",
  "uptime_percent": "number (0-100)",
  "metadata": {
    "additionalProperties": true
  }
}
```

### SatelliteHealthListResponse

```json
{
  "satellites": "array of SatelliteHealthResponse",
  "total_satellites": "integer",
  "operational_count": "integer",
  "degraded_count": "integer",
  "offline_count": "integer",
  "average_uptime": "number (0-100)",
  "last_check": "string (ISO 8601 timestamp)"
}
```

---

## Health Check Details

### Sentinel-2
- **Collection:** COPERNICUS/S2_SR (Sentinel-2 Surface Reflectance)
- **Resolution:** 10-60 meters
- **Temporal Frequency:** 5-day revisit
- **Check Period:** Last 30 days
- **Quality Metric:** Cloud cover percentage
- **Operational Threshold:** ≥90% coverage
- **Degraded Threshold:** ≥50% coverage

### Landsat-8
- **Collection:** LANDSAT/LC08/C02/T1_L2 (Collection 2 Level-2)
- **Resolution:** 30 meters
- **Temporal Frequency:** 16-day revisit
- **Check Period:** Last 30 days
- **Quality Metric:** Cloud cover + QA flags
- **Operational Threshold:** ≥90% quality coverage
- **Degraded Threshold:** ≥50% quality coverage

### ERA5-Land
- **Collection:** ECMWF/ERA5_LAND (Monthly reanalysis)
- **Resolution:** 0.1° (~11 kilometers)
- **Temporal Frequency:** Hourly reanalysis
- **Check Period:** Last 30 days (720 hourly records)
- **Quality Metric:** Temporal completeness
- **Operational Threshold:** ≥95% availability
- **Degraded Threshold:** ≥80% availability

---

## Use Cases

### 1. Pre-Analysis Health Check
Before running carbon calculations or NDVI analysis, check satellite health:

```bash
# Check health
curl -X GET "http://localhost:8000/api/v1/satellites/health" \
  -H "Authorization: Bearer TOKEN"

# If any satellite is offline/degraded, adjust analysis accordingly
```

### 2. Dashboard Status Display
Display real-time satellite status in frontend dashboard:

```javascript
// React component
const response = await fetch('/api/v1/satellites/health', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const data = await response.json();
return (
  <div>
    {data.satellites.map(sat => (
      <SatelliteStatusCard key={sat.satellite_name} data={sat} />
    ))}
  </div>
);
```

### 3. Scheduled Health Monitoring
Run periodic health checks (e.g., hourly background job):

```python
import asyncio
from app.services.satellite_health_service import SatelliteHealthService
from app.core.database import AsyncSessionLocal

async def scheduled_health_check():
    db = AsyncSessionLocal()
    try:
        service = SatelliteHealthService()
        await service.update_all_satellite_status(db)
        print("Health check completed")
    finally:
        await db.close()

# Schedule every hour
asyncio.create_task(scheduled_health_check())
```

### 4. Manual Refresh Trigger
Allow users to manually trigger a full health refresh:

```javascript
// React component
async function triggerHealthRefresh() {
  const response = await fetch('/api/v1/satellites/health/refresh', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (response.status === 202) {
    console.log('Health check triggered, checking again in 60 seconds...');
    setTimeout(() => fetchHealthStatus(), 60000);
  }
}
```

### 5. Alert System Integration
Send alerts when satellites go offline:

```python
@app.on_event("startup")
async def health_monitor():
    while True:
        db = AsyncSessionLocal()
        try:
            service = SatelliteHealthService()
            summary = await service.get_satellite_health_summary(db)
            
            if summary['offline_count'] > 0:
                send_alert(f"{summary['offline_count']} satellites offline!")
            
            await asyncio.sleep(3600)  # Check every hour
        finally:
            await db.close()
```

---

## Integration Examples

### Python (requests)
```python
import requests

class SatelliteHealthClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def get_all_health(self, refresh=False):
        params = {"refresh": refresh}
        response = requests.get(
            f"{self.base_url}/api/v1/satellites/health",
            headers=self.headers,
            params=params,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    
    def get_satellite_health(self, satellite_name):
        response = requests.get(
            f"{self.base_url}/api/v1/satellites/health/{satellite_name}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def trigger_refresh(self):
        response = requests.post(
            f"{self.base_url}/api/v1/satellites/health/refresh",
            headers=self.headers
        )
        return response.status_code == 202

# Usage
client = SatelliteHealthClient("http://localhost:8000", "YOUR_TOKEN")
health = client.get_all_health(refresh=True)
print(f"Operational satellites: {health['operational_count']}/{health['total_satellites']}")
```

### JavaScript (fetch)
```javascript
class SatelliteHealthClient {
  constructor(baseUrl, token) {
    this.baseUrl = baseUrl;
    this.token = token;
  }

  async getAllHealth(refresh = false) {
    const response = await fetch(
      `${this.baseUrl}/api/v1/satellites/health?refresh=${refresh}`,
      {
        headers: { 'Authorization': `Bearer ${this.token}` }
      }
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async getSatelliteHealth(satelliteName) {
    const response = await fetch(
      `${this.baseUrl}/api/v1/satellites/health/${satelliteName}`,
      {
        headers: { 'Authorization': `Bearer ${this.token}` }
      }
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async triggerRefresh() {
    const response = await fetch(
      `${this.baseUrl}/api/v1/satellites/health/refresh`,
      {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${this.token}` }
      }
    );
    return response.status === 202;
  }
}

// Usage
const client = new SatelliteHealthClient('http://localhost:8000', 'YOUR_TOKEN');
const health = await client.getAllHealth(true);
console.log(`Average uptime: ${health.average_uptime}%`);
```

---

## Rate Limiting & Throttling

To prevent API quota issues:

1. **Cache Results:** Cache health data for 5-10 minutes when `refresh=false`
2. **Batch Requests:** Run single refresh for all satellites (not individual requests)
3. **Schedule Checks:** Perform refreshes during off-peak hours
4. **Monitor Quota:** Track Earth Engine API usage

```python
# Recommended schedule
- Manual refreshes: On-demand (max 5 per hour per user)
- Automatic checks: Every 60 minutes (once per system)
- Dashboard display: Every 30 seconds (cached data only)
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-01-15 | Initial satellite health monitoring endpoints |

---

## Support

For issues or questions:
1. Check [Testing Guide](PHASE_5_SATELLITE_TESTING.md)
2. Review [Implementation Guide](PHASE_5_SATELLITE_MONITORING.md)
3. Check API documentation at `/docs` endpoint
4. Review error logs for detailed error messages
