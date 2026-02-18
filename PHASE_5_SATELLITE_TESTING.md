# Satellite Health Monitoring - Testing Guide

## Pre-Test Setup

### 1. Database Migration

Before running tests, ensure the migration is applied:

```bash
cd backend
alembic upgrade head
```

**Verify Migration:**
```bash
# Check if satellite_status table exists
psql -U postgres -d truecarbon -c "\dt satellite_status"
```

### 2. Earth Engine Authentication

Ensure Earth Engine credentials are configured:

```bash
# Set environment variables
export EARTHENGINE_ACCOUNT=<your-service-account>
export EARTHENGINE_KEY_PATH=/path/to/service-account-key.json

# Test authentication
python -c "import ee; ee.Initialize(); print('Earth Engine authenticated')"
```

### 3. Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API documentation will be available at: http://localhost:8000/docs

## Manual API Testing

### Using cURL

#### 1. Get All Satellite Health (No Refresh)

```bash
curl -X GET "http://localhost:8000/api/v1/satellites/health" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "satellites": [],
  "total_satellites": 0,
  "operational_count": 0,
  "degraded_count": 0,
  "offline_count": 0,
  "average_uptime": 0.0,
  "last_check": "2024-01-15T10:30:00Z"
}
```

Note: First request returns empty if no health checks have been run yet.

#### 2. Trigger Manual Health Check (With Refresh)

```bash
curl -X GET "http://localhost:8000/api/v1/satellites/health?refresh=true" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
```

**Expected Response (200 OK after ~30 seconds):**
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
      "metadata": {...}
    },
    ...
  ],
  "total_satellites": 3,
  "operational_count": 3,
  "degraded_count": 0,
  "offline_count": 0,
  "average_uptime": 98.5,
  "last_check": "2024-01-15T10:30:00Z"
}
```

**Potential Errors:**
- **429 Quota Exceeded**: Earth Engine API quota limit reached
- **500 Health Check Failed**: Network issues or service unavailable

#### 3. Get Specific Satellite Health

```bash
# Sentinel-2
curl -X GET "http://localhost:8000/api/v1/satellites/health/sentinel-2" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"

# Landsat-8
curl -X GET "http://localhost:8000/api/v1/satellites/health/landsat-8" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"

# ERA5-Land
curl -X GET "http://localhost:8000/api/v1/satellites/health/era5-land" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
```

**Expected Response:**
```json
{
  "satellite_name": "sentinel-2",
  "status": "operational",
  "coverage_percent": 95.5,
  "accuracy_percent": 92.3,
  "data_quality": "high",
  "last_update": "2024-01-15T10:30:00Z",
  "uptime_percent": 98.7,
  "metadata": {...}
}
```

#### 4. Manual Refresh Request

```bash
curl -X POST "http://localhost:8000/api/v1/satellites/health/refresh" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
```

**Expected Response (202 Accepted):**
```json
{
  "status": "accepted",
  "message": "Satellite health check in progress",
  "timestamp": "2024-01-15T10:35:00Z"
}
```

#### 5. Test 404 Error (Invalid Satellite)

```bash
curl -X GET "http://localhost:8000/api/v1/satellites/health/invalid-satellite" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
```

**Expected Response (404 Not Found):**
```json
{
  "detail": "Satellite 'invalid-satellite' not found. Valid options: sentinel-2, landsat-8, era5-land"
}
```

### Using Python Requests

```python
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
AUTH_TOKEN = "YOUR_AUTH_TOKEN"
headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}

# 1. Get all satellite health (no refresh)
response = requests.get(
    f"{BASE_URL}/satellites/health",
    headers=headers
)
print("Status:", response.status_code)
print("Response:", json.dumps(response.json(), indent=2))

# 2. Trigger refresh
response = requests.get(
    f"{BASE_URL}/satellites/health?refresh=true",
    headers=headers,
    timeout=60  # Health checks can take 30+ seconds
)
print("Status:", response.status_code)
print("Response:", json.dumps(response.json(), indent=2))

# 3. Get specific satellite
response = requests.get(
    f"{BASE_URL}/satellites/health/sentinel-2",
    headers=headers
)
print("Status:", response.status_code)
print("Response:", json.dumps(response.json(), indent=2))

# 4. Manual refresh
response = requests.post(
    f"{BASE_URL}/satellites/health/refresh",
    headers=headers
)
print("Status:", response.status_code)
print("Response:", json.dumps(response.json(), indent=2))
```

### Using FastAPI Swagger UI

1. Navigate to: http://localhost:8000/docs
2. Authorize with your authentication token (click "Authorize" button)
3. Expand satellite endpoints:
   - GET /satellites/health
   - GET /satellites/health/{satellite_name}
   - POST /satellites/health/refresh
4. Click "Try it out" to send test requests
5. Add `refresh=true` query parameter to trigger live checks

## Automated Testing

### Unit Tests

**Location:** `backend/tests/test_satellites.py`

**Run Tests:**
```bash
cd backend
pytest tests/test_satellites.py -v

# Run with coverage
pytest tests/test_satellites.py --cov=app.services.satellite_health_service -v

# Run specific test
pytest tests/test_satellites.py::test_check_sentinel2_health -v
```

**Test Areas:**

1. **Service Tests**
   - `test_check_sentinel2_health()`: Sentinel-2 health check
   - `test_check_landsat8_health()`: Landsat-8 health check
   - `test_check_era5_health()`: ERA5-Land health check
   - `test_update_all_satellite_status()`: Batch update
   - `test_get_satellite_health_summary()`: Summary retrieval

2. **Endpoint Tests**
   - `test_get_satellite_health_no_refresh()`: Basic health endpoint
   - `test_get_satellite_health_with_refresh()`: With live check
   - `test_get_satellite_by_name()`: Individual satellite query
   - `test_get_satellite_not_found()`: 404 error handling
   - `test_refresh_endpoint()`: Manual refresh trigger

3. **Error Handling Tests**
   - `test_quota_exceeded_error()`: 429 handling
   - `test_health_check_failure()`: 500 error handling
   - `test_database_error()`: Database connection issues

### Integration Tests

**Test Database**:
```bash
# Use test database (if configured)
TEST_DATABASE_URL=sqlite:///./test.db pytest tests/
```

**Test with Real Data:**
```bash
# Test with actual Earth Engine data (requires valid credentials)
pytest tests/test_satellites.py -m "earth_engine" -v
```

## Load Testing

### Using Apache Bench

```bash
# Single endpoint test (1000 requests, 10 concurrent)
ab -n 1000 -c 10 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/satellites/health

# Results interpretation:
# - Requests per second: Throughput
# - Time per request: Latency
# - Failed requests: Stability issues
```

### Using wrk

```bash
# High-performance load test
wrk -t4 -c100 -d30s \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/satellites/health
```

### Using Locust

```python
# locustfile.py
from locust import HttpUser, task, between

class SatelliteHealthUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def get_health(self):
        self.client.get(
            "/api/v1/satellites/health",
            headers={"Authorization": "Bearer YOUR_TOKEN"}
        )
    
    @task
    def get_specific_satellite(self):
        self.client.get(
            "/api/v1/satellites/health/sentinel-2",
            headers={"Authorization": "Bearer YOUR_TOKEN"}
        )
```

Run: `locust -f locustfile.py --host=http://localhost:8000`

## Performance Benchmarks

**Expected Performance:**

| Endpoint | Method | Avg Response | Max Response | Notes |
|----------|--------|--------------|--------------|-------|
| `/satellites/health` | GET (no refresh) | 50ms | 100ms | Database query only |
| `/satellites/health?refresh=true` | GET | 30-60s | 120s | Earth Engine calls |
| `/satellites/health/{name}` | GET | 30ms | 60ms | Single record query |
| `/satellites/health/refresh` | POST | 30-60s | 120s | Async health checks |

**Optimization Tips:**
1. Cache results when `refresh=false` (5-10 minute TTL)
2. Run health checks async/background job (not blocking)
3. Implement database connection pooling
4. Use read replicas for health queries

## Database Verification

### Check Satellite Status Records

```sql
-- List all satellite status records
SELECT 
  satellite_name,
  status,
  coverage_percent,
  accuracy_percent,
  data_quality,
  uptime_percent,
  last_update,
  metadata
FROM satellite_status
ORDER BY satellite_name;

-- Get latest check time
SELECT MAX(last_update) as latest_check FROM satellite_status;

-- Check metadata
SELECT 
  satellite_name,
  jsonb_pretty(metadata) as metadata
FROM satellite_status;
```

### Verify Table Structure

```sql
-- Check table schema
\d satellite_status

-- List indexes
\di *satellite*

-- Check constraints
SELECT constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'satellite_status';
```

## Troubleshooting Test Issues

### Issue: "Import could not be resolved"
```bash
# Install missing dependencies
pip install -r backend/requirements-dev.txt

# Verify imports
python -c "from app.services.satellite_health_service import SatelliteHealthService"
```

### Issue: "Database connection failed"
```bash
# Check database connection
psql -h localhost -U postgres -d truecarbon -c "SELECT 1"

# Verify migrations applied
cd backend && alembic current
```

### Issue: "Earth Engine authentication failed"
```bash
# Test Earth Engine directly
python -c "
import ee
ee.Authenticate()  # Opens browser to authorize
ee.Initialize()
print('Earth Engine initialized')
"
```

### Issue: "429 Quota Exceeded"
- Wait 24 hours for quota to reset
- Check for other services using the same API key
- Contact Google Cloud to increase quota
- Use cached results instead of triggering refresh

### Issue: "Endpoints not registered"
```bash
# Verify router is imported in __init__.py
grep "satellites" backend/app/api/v1/__init__.py

# Check FastAPI app includes router
python -c "
from app.main import app
for route in app.routes:
    if 'satellites' in str(route):
        print(route)
"
```

## Continuous Monitoring

### Health Check Job Configuration

```python
# In app/main.py or background tasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup_event():
    scheduler.add_job(
        update_satellite_health,
        "interval",
        minutes=60,  # Every hour
        id="satellite_health_check"
    )
    scheduler.start()

async def update_satellite_health():
    """Background task to update satellite health"""
    db = SessionLocal()
    try:
        service = SatelliteHealthService()
        await service.update_all_satellite_status(db)
        logger.info("Background satellite health check completed")
    except Exception as e:
        logger.error(f"Background health check failed: {e}")
    finally:
        await db.close()
```

### Monitoring Queries

```sql
-- Health checks performed today
SELECT 
  DATE(last_update) as check_date,
  COUNT(*) as check_count
FROM satellite_status
WHERE last_update >= CURRENT_DATE
GROUP BY DATE(last_update);

-- Satellites with issues
SELECT 
  satellite_name,
  status,
  coverage_percent,
  last_update
FROM satellite_status
WHERE status != 'operational'
ORDER BY last_update DESC;

-- Average availability over time
SELECT 
  DATE_TRUNC('hour', last_update) as hour,
  AVG(coverage_percent) as avg_coverage,
  AVG(uptime_percent) as avg_uptime
FROM satellite_status
GROUP BY DATE_TRUNC('hour', last_update)
ORDER BY hour DESC
LIMIT 24;
```

## Success Criteria

✅ All tests pass
✅ Database migration applies successfully
✅ Endpoints respond with correct status codes
✅ Health checks complete within 60 seconds
✅ API documentation generated correctly
✅ Error responses properly formatted
✅ Performance meets benchmarks
✅ Earth Engine API integration working
✅ Database queries optimized (<50ms)
✅ No memory leaks in background tasks
