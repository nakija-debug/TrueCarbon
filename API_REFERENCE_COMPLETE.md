# TrueCarbon API Reference - Phase 5

**Base URL**: `http://localhost:8000/api/v1` (development)
**API Version**: 2.0.0
**Format**: JSON
**Authentication**: JWT Bearer Token

---

## Table of Contents

1. [Authentication Endpoints](#authentication)
2. [User Management](#users)
3. [Farm Management](#farms)
4. [Carbon Analysis](#carbon)
5. [NDVI Analysis](#ndvi)
6. [Error Handling](#errors)
7. [Examples](#examples)

---

## <a id="authentication"></a>Authentication Endpoints

### POST /auth/login
**Description**: Authenticate user and receive JWT token

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Status Codes**:
- `200 OK` - Login successful
- `401 Unauthorized` - Invalid credentials
- `400 Bad Request` - Missing required fields

---

### POST /auth/register
**Description**: Register a new user account

**Request**:
```json
{
  "email": "newuser@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "company_id": 1
}
```

**Response (201 Created)**:
```json
{
  "user_id": 123,
  "email": "newuser@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "company_id": 1,
  "role": "user",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Status Codes**:
- `201 Created` - User registered successfully
- `400 Bad Request` - Invalid input or email already exists
- `422 Unprocessable Entity` - Validation error

---

### POST /auth/refresh
**Description**: Refresh access token using refresh token

**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Status Codes**:
- `200 OK` - Token refreshed
- `401 Unauthorized` - Invalid refresh token
- `403 Forbidden` - Refresh token expired

---

### POST /auth/logout
**Description**: Logout user (invalidate tokens)

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response (200 OK)**:
```json
{
  "message": "Successfully logged out"
}
```

**Status Codes**:
- `200 OK` - Logout successful
- `401 Unauthorized` - No valid token provided

---

## <a id="users"></a>User Management Endpoints

### GET /users
**Description**: List all users (paginated)

**Headers**:
```
Authorization: Bearer <access_token>
```

**Query Parameters**:
```
skip: int (default: 0) - Number of records to skip
limit: int (default: 50) - Number of records to return (max: 100)
role: str (optional) - Filter by role (admin, manager, user)
company_id: int (optional) - Filter by company
```

**Response (200 OK)**:
```json
{
  "items": [
    {
      "user_id": 1,
      "email": "admin@example.com",
      "first_name": "Admin",
      "last_name": "User",
      "role": "admin",
      "company_id": 1,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "last_login": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 100,
  "skip": 0,
  "limit": 50
}
```

---

### GET /users/{user_id}
**Description**: Get specific user details

**Headers**:
```
Authorization: Bearer <access_token>
```

**Path Parameters**:
```
user_id: int - User ID to retrieve
```

**Response (200 OK)**:
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "manager",
  "company_id": 1,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-15T10:30:00Z"
}
```

**Status Codes**:
- `200 OK` - User found
- `404 Not Found` - User does not exist
- `401 Unauthorized` - Invalid token

---

### POST /users
**Description**: Create a new user (Admin only)

**Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request**:
```json
{
  "email": "newuser@example.com",
  "password": "securepassword123",
  "first_name": "Jane",
  "last_name": "Smith",
  "company_id": 1,
  "role": "user"
}
```

**Response (201 Created)**:
```json
{
  "user_id": 456,
  "email": "newuser@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "user",
  "company_id": 1,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Status Codes**:
- `201 Created` - User created successfully
- `403 Forbidden` - Insufficient permissions
- `400 Bad Request` - Invalid input

---

### PUT /users/{user_id}
**Description**: Update user information

**Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request**:
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "is_active": true
}
```

**Response (200 OK)**:
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Smith",
  "role": "manager",
  "company_id": 1,
  "is_active": true,
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### DELETE /users/{user_id}
**Description**: Delete a user

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response (204 No Content)**: User deleted successfully

**Status Codes**:
- `204 No Content` - User deleted
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - User not found

---

## <a id="farms"></a>Farm Management Endpoints

### GET /farms
**Description**: List all farms with pagination and filtering

**Headers**:
```
Authorization: Bearer <access_token>
```

**Query Parameters**:
```
skip: int (default: 0)
limit: int (default: 50, max: 100)
company_id: int (optional) - Filter by company
search: str (optional) - Search by name or description
is_active: bool (optional) - Filter by status
```

**Response (200 OK)**:
```json
{
  "items": [
    {
      "farm_id": 1,
      "company_id": 1,
      "name": "Carbon Farm Alpha",
      "description": "200-hectare farm in the Amazon region",
      "area_hectares": 200.5,
      "location_string": "State of Rondônia, Brazil",
      "geometry": {
        "type": "Feature",
        "geometry": {
          "type": "Polygon",
          "coordinates": [[[-60.123, -10.456], ...]]
        }
      },
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "is_active": true
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 50
}
```

---

### GET /farms/{farm_id}
**Description**: Get detailed farm information

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response (200 OK)**:
```json
{
  "farm_id": 1,
  "company_id": 1,
  "name": "Carbon Farm Alpha",
  "description": "200-hectare farm in the Amazon region",
  "area_hectares": 200.5,
  "location_string": "State of Rondônia, Brazil",
  "geometry": {
    "type": "Feature",
    "geometry": {"type": "Polygon", "coordinates": [...]}
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "is_active": true,
  "latest_carbon_estimate": {
    "estimate_id": 100,
    "carbon_value": 4500.25,
    "uncertainty": 225.13,
    "confidence_score": 92.5,
    "measurement_date": "2024-01-15T00:00:00Z"
  }
}
```

---

### POST /farms
**Description**: Create a new farm

**Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request**:
```json
{
  "company_id": 1,
  "name": "New Carbon Farm",
  "description": "A new farm for carbon credit monitoring",
  "area_hectares": 150.0,
  "location_string": "State of Amazonas, Brazil",
  "geometry": {
    "type": "Feature",
    "geometry": {
      "type": "Polygon",
      "coordinates": [[
        [-60.0, -10.0],
        [-60.0, -11.0],
        [-59.0, -11.0],
        [-59.0, -10.0],
        [-60.0, -10.0]
      ]]
    }
  }
}
```

**Response (201 Created)**:
```json
{
  "farm_id": 2,
  "company_id": 1,
  "name": "New Carbon Farm",
  "area_hectares": 150.0,
  "created_at": "2024-01-15T10:30:00Z",
  "is_active": true
}
```

---

### PUT /farms/{farm_id}
**Description**: Update farm information

**Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request**:
```json
{
  "name": "Updated Farm Name",
  "description": "Updated description",
  "area_hectares": 175.5
}
```

**Response (200 OK)**:
```json
{
  "farm_id": 1,
  "name": "Updated Farm Name",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

---

### DELETE /farms/{farm_id}
**Description**: Delete a farm (soft delete - sets is_active to false)

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response (204 No Content)**: Farm deleted successfully

---

## <a id="carbon"></a>Carbon Analysis Endpoints

### POST /carbon/estimate
**Description**: Calculate carbon estimate for a farm

**Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request**:
```json
{
  "farm_id": 1,
  "measurement_date": "2024-01-15",
  "land_type": "forest",
  "management_practice": "natural_growth",
  "start_date": "2023-01-15",
  "end_date": "2024-01-15",
  "run_monte_carlo": true,
  "monte_carlo_iterations": 10000
}
```

**Response (200 OK)**:
```json
{
  "estimate_id": 100,
  "farm_id": 1,
  "carbon_value": 4500.25,
  "uncertainty": 225.13,
  "confidence_score": 92.5,
  "total_points": 256,
  "measurement_date": "2024-01-15",
  "methodology": "IPCC 2006 Tier 2",
  "statistics": {
    "mean_carbon": 4500.25,
    "std_carbon": 225.13,
    "mean_ndvi": 0.642,
    "std_ndvi": 0.0842,
    "mean_confidence_score": 92.5,
    "overall_std_dev": 0.0562,
    "min_ndvi": 0.456,
    "max_ndvi": 0.855
  },
  "metadata": {
    "data_source": "Sentinel-2 + Dynamic World",
    "processing_timestamp": "2024-01-15T10:30:00Z",
    "uncertainty_method": "Monte Carlo",
    "monte_carlo_iterations": 10000
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Parameters**:
- `farm_id`: ID of the farm (required)
- `land_type`: "forest", "grassland", "cropland", "urban" (required)
- `management_practice`: Type of management (optional)
- `start_date`: Analysis start date YYYY-MM-DD (required)
- `end_date`: Analysis end date YYYY-MM-DD (required)
- `run_monte_carlo`: Enable uncertainty analysis (default: true)
- `monte_carlo_iterations`: Number of iterations (default: 10000)

**Status Codes**:
- `200 OK` - Estimate calculated successfully
- `400 Bad Request` - Invalid parameters
- `404 Not Found` - Farm not found
- `422 Unprocessable Entity` - Invalid date range

---

### GET /carbon/estimate/{farm_id}
**Description**: Get carbon estimates for a farm

**Headers**:
```
Authorization: Bearer <access_token>
```

**Query Parameters**:
```
skip: int (default: 0)
limit: int (default: 50)
start_date: str (optional) - YYYY-MM-DD
end_date: str (optional) - YYYY-MM-DD
```

**Response (200 OK)**:
```json
{
  "items": [
    {
      "estimate_id": 100,
      "farm_id": 1,
      "carbon_value": 4500.25,
      "uncertainty": 225.13,
      "confidence_score": 92.5,
      "measurement_date": "2024-01-15",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 12,
  "skip": 0,
  "limit": 50
}
```

---

### GET /carbon/report/{estimate_id}
**Description**: Get detailed carbon report

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response (200 OK)**:
```json
{
  "estimate_id": 100,
  "farm_id": 1,
  "farm_name": "Carbon Farm Alpha",
  "carbon_value": 4500.25,
  "unit": "tCO2e",
  "uncertainty": 225.13,
  "confidence_score": 92.5,
  "total_points": 256,
  "measurement_date": "2024-01-15",
  "land_type": "forest",
  "statistics": {
    "mean_carbon": 4500.25,
    "std_carbon": 225.13,
    "min_carbon": 4100.5,
    "max_carbon": 4900.0,
    "mean_ndvi": 0.642,
    "std_ndvi": 0.0842,
    "mean_confidence_score": 92.5
  },
  "metadata": {
    "methodology": "IPCC 2006 Tier 2",
    "data_source": "Sentinel-2 + Dynamic World",
    "uncertainty_method": "Monte Carlo",
    "monte_carlo_iterations": 10000,
    "processing_timestamp": "2024-01-15T10:30:00Z"
  },
  "compliance": {
    "ipcc_compliant": true,
    "iso_14064_2_compliant": true,
    "unfccc_vcs_eligible": true
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## <a id="ndvi"></a>NDVI Analysis Endpoints

### GET /ndvi/timeseries/{farm_id}
**Description**: Get NDVI time series data for a farm

**Headers**:
```
Authorization: Bearer <access_token>
```

**Query Parameters**:
```
start_date: str (YYYY-MM-DD) - Start of analysis period (required)
end_date: str (YYYY-MM-DD) - End of analysis period (required)
frequency: str (daily|monthly|quarterly) - Data frequency (default: monthly)
```

**Response (200 OK)**:
```json
{
  "farm_id": 1,
  "farm_name": "Carbon Farm Alpha",
  "area_hectares": 200.5,
  "start_date": "2023-01-15",
  "end_date": "2024-01-15",
  "frequency": "monthly",
  "data_points": [
    {
      "date": "2023-01-15",
      "mean_ndvi": 0.542,
      "std_ndvi": 0.0841,
      "pixels_valid": 2450,
      "pixels_total": 2560,
      "cloud_coverage": 5.2
    },
    {
      "date": "2023-02-15",
      "mean_ndvi": 0.589,
      "std_ndvi": 0.0756,
      "pixels_valid": 2480,
      "pixels_total": 2560,
      "cloud_coverage": 3.1
    }
  ],
  "summary": {
    "overall_mean_ndvi": 0.612,
    "overall_std_ndvi": 0.0842,
    "min_ndvi": 0.456,
    "max_ndvi": 0.855,
    "trend": "increasing"
  }
}
```

---

### GET /ndvi/current/{farm_id}
**Description**: Get current NDVI for a farm

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response (200 OK)**:
```json
{
  "farm_id": 1,
  "farm_name": "Carbon Farm Alpha",
  "current_date": "2024-01-15",
  "ndvi_value": 0.725,
  "ndvi_std": 0.0685,
  "ndvi_min": 0.612,
  "ndvi_max": 0.842,
  "pixels_valid": 2500,
  "pixels_total": 2560,
  "pixel_resolution_m": 10,
  "cloud_coverage": 2.5,
  "previous_month_ndvi": 0.691,
  "change": 0.034,
  "change_percent": 4.9,
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### GET /ndvi/monthly/{farm_id}
**Description**: Get monthly NDVI statistics

**Headers**:
```
Authorization: Bearer <access_token>
```

**Query Parameters**:
```
year: int - Year to retrieve (default: current year)
month: int (1-12) - Optional specific month
```

**Response (200 OK)**:
```json
{
  "farm_id": 1,
  "year": 2024,
  "monthly_stats": [
    {
      "month": 1,
      "month_name": "January",
      "mean_ndvi": 0.725,
      "std_ndvi": 0.0685,
      "median_ndvi": 0.742,
      "min_ndvi": 0.612,
      "max_ndvi": 0.842,
      "days_valid": 28,
      "cloud_free_days": 25
    }
  ]
}
```

---

## <a id="errors"></a>Error Handling

### Standard Error Response Format

**400 Bad Request**:
```json
{
  "detail": "Invalid request parameters",
  "error_code": "INVALID_INPUT",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**401 Unauthorized**:
```json
{
  "detail": "Not authenticated",
  "error_code": "AUTHENTICATION_FAILED",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**403 Forbidden**:
```json
{
  "detail": "Insufficient permissions",
  "error_code": "INSUFFICIENT_PERMISSIONS",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**404 Not Found**:
```json
{
  "detail": "Resource not found",
  "error_code": "RESOURCE_NOT_FOUND",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**422 Unprocessable Entity**:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Internal server error",
  "error_code": "INTERNAL_ERROR",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "abc-123-def-456"
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| INVALID_INPUT | 400 | Invalid input parameters |
| AUTHENTICATION_FAILED | 401 | User not authenticated |
| INVALID_TOKEN | 401 | JWT token invalid or expired |
| INSUFFICIENT_PERMISSIONS | 403 | User lacks required permissions |
| RESOURCE_NOT_FOUND | 404 | Requested resource not found |
| DUPLICATE_RESOURCE | 409 | Resource already exists |
| VALIDATION_ERROR | 422 | Input validation failed |
| INTERNAL_ERROR | 500 | Unexpected server error |

---

## <a id="examples"></a>Complete Usage Examples

### Example 1: Complete Analysis Workflow

```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }' | jq .access_token

# Save TOKEN from response
TOKEN="..."

# 2. List farms
curl -X GET "http://localhost:8000/api/v1/farms?limit=5" \
  -H "Authorization: Bearer $TOKEN"

# 3. Get farm details
curl -X GET "http://localhost:8000/api/v1/farms/1" \
  -H "Authorization: Bearer $TOKEN"

# 4. Calculate carbon estimate
curl -X POST http://localhost:8000/api/v1/carbon/estimate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "farm_id": 1,
    "land_type": "forest",
    "start_date": "2023-01-15",
    "end_date": "2024-01-15",
    "run_monte_carlo": true
  }'

# 5. Get carbon report
curl -X GET "http://localhost:8000/api/v1/carbon/report/100" \
  -H "Authorization: Bearer $TOKEN"

# 6. Get NDVI time series
curl -X GET "http://localhost:8000/api/v1/ndvi/timeseries/1?start_date=2023-01-15&end_date=2024-01-15" \
  -H "Authorization: Bearer $TOKEN"
```

### Example 2: Using Python with Requests

```python
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "user@example.com"
PASSWORD = "password123"

# Login
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": EMAIL, "password": PASSWORD}
)
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get farms
farms_response = requests.get(
    f"{BASE_URL}/farms",
    headers=headers,
    params={"limit": 10}
)
farms = farms_response.json()["items"]

# Calculate carbon
for farm in farms:
    carbon_response = requests.post(
        f"{BASE_URL}/carbon/estimate",
        headers=headers,
        json={
            "farm_id": farm["farm_id"],
            "land_type": "forest",
            "start_date": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d")
        }
    )
    estimate = carbon_response.json()
    print(f"Farm {farm['name']}: {estimate['carbon_value']} tCO2e")
```

---

## Rate Limiting & Quotas

- **Rate Limit**: 100 requests per minute per user
- **Batch Limit**: 20 records per request (for list endpoints)
- **File Size**: 10MB max for geometry uploads
- **Storage**: 100GB per company

---

## Pagination

List endpoints support cursor-based pagination:

```
GET /endpoint?skip=0&limit=50
```

Response includes:
```json
{
  "items": [...],
  "total": 1000,
  "skip": 0,
  "limit": 50
}
```

---

**API Version**: 2.0.0  
**Last Updated**: 2024  
**Status**: Production Ready

For more information, visit the interactive API documentation at `/docs` or `/redoc` when the server is running.
