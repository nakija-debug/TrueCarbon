# Phase 5 API Reference

## Quick Start

### 1. Calculate Carbon from NDVI
```bash
curl -X POST "http://localhost:8000/api/v1/carbon/calculate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "farm_id": "12345",
    "start_date": "2026-01-01",
    "end_date": "2026-02-01"
  }'
```

Response (202 Accepted):
```json
{
  "farm_id": "12345",
  "farm_name": "Green Farm",
  "area_ha": 50.0,
  "data_points": [
    {
      "date": "2026-01-10T00:00:00",
      "ndvi": 0.65,
      "agb_tonnes_ha": 77.8,
      "carbon_tonnes_ha": 36.55,
      "co2_tonnes_ha": 134.02,
      "agb_total_tonnes": 3890,
      "carbon_total_tonnes": 1827.59,
      "co2_total_tonnes": 6701.11
    }
  ],
  "statistics": {
    "mean_agb_tonnes_ha": 77.8,
    "total_agb_tonnes": 3890,
    "mean_carbon_tonnes_ha": 36.55,
    "total_carbon_tonnes": 1827.59,
    "total_co2_tonnes": 6701.11,
    "min_ndvi": 0.65,
    "max_ndvi": 0.72,
    "mean_ndvi": 0.68
  },
  "metadata": {
    "model_version": "v1.0",
    "model_name": "Pan-tropical Allometric Equation (Chave et al. 2014)",
    "agb_coefficient_a": 142.9,
    "agb_exponent_b": 1.60,
    "carbon_fraction": 0.47,
    "co2_conversion_factor": 3.666667,
    "assumptions": [
      "AGB = 142.9 * NDVI^1.60",
      "Carbon = AGB * 0.47 (IPCC Tier 1)",
      "CO2 equivalent = Carbon * 44/12",
      "Valid for tropical/subtropical regions"
    ]
  }
}
```

### 2. Retrieve Carbon Estimates
```bash
curl -X GET "http://localhost:8000/api/v1/carbon/12345" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response (200 OK):
```json
{
  "farm_id": "12345",
  "farm_name": "Green Farm",
  "area_ha": 50.0,
  "data_points": [...],
  "statistics": {...},
  "metadata": {...}
}
```

### 3. Calculate NDVI with Carbon (New!)
```bash
curl -X POST "http://localhost:8000/api/v1/ndvi/calculate?calculate_carbon=true" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "farm_id": "12345",
    "start_date": "2026-01-01",
    "end_date": "2026-02-01",
    "source": "Sentinel-2"
  }'
```

Response (202 Accepted):
```json
{
  "farm_id": "12345",
  "farm_name": "Green Farm",
  "ndvi_data_points": [
    {
      "date": "2026-01-10T00:00:00",
      "ndvi": 0.65,
      "std": 0.02
    }
  ],
  "statistics": {
    "mean_ndvi": 0.68,
    "min_ndvi": 0.65,
    "max_ndvi": 0.72,
    "data_points_count": 3
  }
}
```

Side effect: If `calculate_carbon=true`:
- NDVI measurements stored
- Carbon automatically calculated from NDVI
- Carbon measurements stored in database
- Retrieve via: `GET /api/v1/carbon/12345`

## API Endpoints

### POST /api/v1/carbon/calculate
**Calculate carbon sequestration from stored NDVI data**

| Property | Value |
|----------|-------|
| Method | POST |
| Status | 202 Accepted (async) |
| Auth | Required |

**Request Schema:**
```python
{
  "farm_id": str,           # UUID of farm
  "start_date": str,        # ISO 8601 date (yyyy-mm-dd)
  "end_date": str,          # ISO 8601 date (yyyy-mm-dd)
}
```

**Responses:**
- `202 Accepted`: Calculation queued
- `400 Bad Request`: Invalid request data
- `403 Forbidden`: User lacks access to farm
- `404 Not Found`: Farm not found
- `500 Server Error`: Calculation error

---

### GET /api/v1/carbon/{farm_id}
**Retrieve stored carbon estimates for farm**

| Property | Value |
|----------|-------|
| Method | GET |
| Status | 200 OK |
| Auth | Required |

**Path Parameters:**
- `farm_id`: UUID of farm

**Responses:**
- `200 OK`: Returns CarbonResponse
- `403 Forbidden`: User lacks access to farm
- `404 Not Found`: Farm not found

---

### POST /api/v1/ndvi/calculate?calculate_carbon=true
**Enhanced NDVI endpoint with optional carbon calculation**

| Property | Value |
|----------|-------|
| Method | POST |
| Status | 202 Accepted (async) |
| Auth | Required |

**Query Parameters:**
- `calculate_carbon`: bool (default: false) - Calculate carbon after NDVI

**Request Schema:**
```python
{
  "farm_id": str,           # UUID of farm
  "start_date": str,        # ISO 8601 date
  "end_date": str,          # ISO 8601 date
  "source": str,            # "Sentinel-2", etc.
}
```

**Responses:**
- `202 Accepted`: NDVI queued, carbon optional
- `400 Bad Request`: Invalid request
- `403 Forbidden`: User lacks access
- `404 Not Found`: Farm not found

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid date range: end_date must be >= start_date"
}
```

### 403 Forbidden
```json
{
  "detail": "You don't have access to this resource"
}
```

### 404 Not Found
```json
{
  "detail": "Farm not found"
}
```

### 500 Server Error
```json
{
  "detail": "Internal server error: [error details]"
}
```

## Key Facts

### Calculation Formula
```
AGB (tonnes/ha) = 142.9 × NDVI^1.60
Carbon (tC/ha) = AGB × 0.47
CO2 (tonnes/ha) = Carbon × 44/12
```

### Multi-tenancy
- All endpoints filter by user's company
- Cross-company access returns 403 Forbidden
- Cannot access farms from other companies

### Performance
- ~10ms per 1000 NDVI points
- Async execution (non-blocking)
- Database queries optimized with indexes

### Limitations
- Max date range: 5 years (validated)
- Valid for tropical/subtropical regions
- Requires Sentinel-2 NDVI data as input

## Python Client Example

```python
import httpx
import asyncio

async def calculate_carbon():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/carbon/calculate",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "farm_id": "12345",
                "start_date": "2026-01-01",
                "end_date": "2026-02-01",
            }
        )
        
        if response.status_code == 202:
            data = response.json()
            print(f"Total carbon: {data['statistics']['total_carbon_tonnes']:.2f} tC")
            return data
        else:
            print(f"Error: {response.json()}")

asyncio.run(calculate_carbon())
```

## Database Schema

### Measurement Table (Carbon Records)
```sql
INSERT INTO measurements (
  farm_id,
  measurement_type,  -- "carbon"
  measurement_date,
  value,             -- carbon_tonnes_ha
  meta
) VALUES (
  '...',
  'carbon',
  '2026-01-10T00:00:00',
  36.55,
  {
    "model": "Pan-tropical allometric equation",
    "model_version": "v1.0",
    "agb_tonnes_ha": 77.8,
    "co2_tonnes_ha": 134.02,
    "ndvi_input": 0.65,
    "coefficient_a": 142.9,
    "coefficient_b": 1.60
  }
)
```

## Troubleshooting

### Issue: 404 Farm Not Found
- Verify farm_id is correct UUID
- Ensure farm exists in database
- Check user has access to farm

### Issue: 403 Forbidden
- Verify user is authenticated
- Confirm farm belongs to user's company
- Check authorization token is valid

### Issue: 400 Bad Request
- Verify date format: YYYY-MM-DD
- Ensure end_date >= start_date
- Check date range is valid (max 5 years)
- Verify NDVI data exists for farm

### Issue: Empty Carbon Data
- NDVI measurements must exist first
- Use POST /ndvi/calculate to create NDVI data
- Then use POST /carbon/calculate
- Or use ?calculate_carbon=true on NDVI endpoint

## Support

For issues or questions:
1. Check [PHASE5_COMPLETION.md](./PHASE5_COMPLETION.md) for full documentation
2. Review test cases in [backend/test_phase5.py](./backend/test_phase5.py)
3. Contact: [support details]
