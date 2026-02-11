# TrueCarbon Project - Local Setup Guide

## Quick Start (Recommended)

### 1. Automated Setup
Run the setup script to configure everything automatically:

```bash
cd /home/grey-ninja/Downloads/TrueCarbon
chmod +x setup.sh
./setup.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Generate a SECRET_KEY
- Initialize the database
- Verify all imports

### 2. Start the Backend API Server

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 3. Access the API Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **API Root:** http://localhost:8000

---

## Manual Setup (If Automated Script Fails)

### 1. Prerequisites

- Python 3.10+ (currently running 3.13.9 ✓)
- pip and venv
- PostgreSQL (optional, SQLite used by default)

### 2. Create Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and configure:

```dotenv
# SQLite (default, no setup needed)
DATABASE_URL=sqlite+aiosqlite:///./truecarbon.db

# OR PostgreSQL (if you prefer)
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/truecarbon

# Generate SECRET_KEY
# openssl rand -hex 32
SECRET_KEY=your-generated-secret-key-here

# Google Earth Engine (optional for later phases)
GEE_PROJECT=student-research-carbon
```

### 5. Initialize Database

```bash
alembic upgrade head
```

### 6. Verify Setup

```bash
python -c "from app.main import app; print('✓ App imported successfully')"
```

### 7. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Project Structure

```
TrueCarbon/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── core/                     # Configuration, database, security
│   │   ├── models/                   # SQLAlchemy ORM models
│   │   ├── schemas/                  # Pydantic validation schemas
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth.py          # Authentication endpoints
│   │   │       ├── users.py         # User management
│   │   │       ├── farms.py         # Farm CRUD
│   │   │       ├── ndvi.py          # NDVI time-series
│   │   │       └── carbon.py        # Carbon estimation (Phase 5)
│   │   ├── services/                 # Business logic
│   │   │   ├── carbon_service.py    # Carbon calculations
│   │   │   ├── ndvi_service.py      # NDVI calculations
│   │   │   └── ...
│   │   └── main.py                   # FastAPI app entry point
│   ├── alembic/                      # Database migrations
│   ├── requirements.txt
│   ├── .env.example
│   └── .env                          # Configuration (git-ignored)
├── frontend/                         # React/Vue Frontend
│   └── true_carbon/
│       ├── src/
│       ├── package.json
│       └── ...
└── README.md
```

---

## API Endpoints

### Authentication (Phase 1-3)
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token

### User Management
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/{user_id}` - Update user
- `POST /api/v1/users/` - Create user (admin)

### Farm Management (Phase 2)
- `POST /api/v1/farms/` - Create farm
- `GET /api/v1/farms/` - List farms
- `GET /api/v1/farms/{farm_id}` - Get farm details
- `PUT /api/v1/farms/{farm_id}` - Update farm
- `DELETE /api/v1/farms/{farm_id}` - Delete farm

### NDVI Time-Series (Phase 4)
- `POST /api/v1/ndvi/calculate` - Calculate NDVI measurements
- `GET /api/v1/ndvi/{farm_id}` - Get NDVI measurements

### Carbon Estimation (Phase 5)
- `POST /api/v1/carbon/calculate` - Calculate carbon sequestration
- `GET /api/v1/carbon/{farm_id}` - Get carbon estimates

---

## Testing the API

### Using cURL

```bash
# 1. Register a new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'

# 2. Login to get token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'

# 3. Use token to access protected endpoints
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/users/me
```

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Register
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
})
print(response.json())

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "user@example.com",
    "password": "securepassword123"
})
token = response.json()["access_token"]

# Access protected endpoint
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/users/me", headers=headers)
print(response.json())
```

---

## Database

### SQLite (Default)
- **File Location:** `backend/truecarbon.db`
- **No setup required** - automatically created on first migration
- **Best for:** Local development

### PostgreSQL (Optional)
If you prefer PostgreSQL:

```bash
# Update .env
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/truecarbon

# Make sure PostgreSQL is running
# Then run migrations
alembic upgrade head
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'app'"

**Solution:** Make sure you're in the backend directory and have the venv activated:
```bash
cd backend
source venv/bin/activate
```

### Issue: "DATABASE_URL not set"

**Solution:** Check that `.env` file exists with DATABASE_URL:
```bash
cat backend/.env | grep DATABASE_URL
```

### Issue: "Port 8000 already in use"

**Solution:** Use a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

### Issue: Database migration errors

**Solution:** Reset the database:
```bash
rm backend/truecarbon.db  # For SQLite
alembic upgrade head       # Reinitialize
```

### Issue: Import errors after editing code

**Solution:** Restart the uvicorn server (--reload should handle this automatically)

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DATABASE_URL | ✓ | - | SQLite or PostgreSQL connection string |
| SECRET_KEY | ✓ | - | JWT secret (generate with `openssl rand -hex 32`) |
| ENVIRONMENT | - | development | development, staging, or production |
| GEE_PROJECT | - | - | Google Earth Engine project ID |
| CORS_ORIGINS | - | localhost:3000 | Allowed CORS origins (JSON list) |

---

## Development Features

### Auto-reload on Changes
The `--reload` flag automatically restarts the server when code changes.

### Interactive API Documentation
- Visit http://localhost:8000/docs for Swagger UI
- Try API endpoints directly from the browser

### Database Migrations
```bash
# Create new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply all pending migrations
alembic upgrade head

# Downgrade one migration
alembic downgrade -1
```

### Running Tests (Optional)
```bash
pytest backend/
```

---

## Common Tasks

### Create a Test Farm

```bash
# 1. Get a token (as shown above)
TOKEN="your-token-here"

# 2. Create a farm
curl -X POST "http://localhost:8000/api/v1/farms/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Farm",
    "area_ha": 50.0,
    "location": "Latitude 37.7749, Longitude -122.4194"
  }'
```

### Calculate NDVI for a Farm

```bash
curl -X POST "http://localhost:8000/api/v1/ndvi/calculate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "farm_id": "farm-uuid-here",
    "start_date": "2026-01-01",
    "end_date": "2026-02-01",
    "source": "Sentinel-2"
  }'
```

### Calculate Carbon from NDVI

```bash
curl -X POST "http://localhost:8000/api/v1/carbon/calculate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "farm_id": "farm-uuid-here",
    "start_date": "2026-01-01",
    "end_date": "2026-02-01"
  }'
```

---

## Performance

- **Async I/O:** All database operations are asynchronous
- **Connection Pooling:** SQLAlchemy manages connection pools automatically
- **Caching:** Token validation is cached within request lifecycle

---

## Next Steps

1. ✅ Set up local environment
2. 📚 Read API documentation at `/docs`
3. 🧪 Test endpoints using Swagger UI or cURL
4. 🔐 Understand authentication and token flow
5. 🌾 Create test data (users, companies, farms)
6. 📊 Explore farm and NDVI endpoints
7. 🌱 Calculate carbon sequestration estimates

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API documentation: http://localhost:8000/docs
3. Check console output for error messages
4. Review `.env` configuration

---

## Production Deployment

For production deployment, refer to:
- FastAPI deployment docs: https://fastapi.tiangolo.com/deployment/
- Uvicorn production settings: https://www.uvicorn.org/
- Database: Switch to PostgreSQL with proper backups
- Security: Use strong SECRET_KEY, restrict CORS_ORIGINS, enable HTTPS
