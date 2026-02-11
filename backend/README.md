# True Carbon API - Unified Backend

A production-grade FastAPI backend consolidating NDVI, LULC (carbon estimation), and authentication services for the True Carbon carbon measurement and reporting platform.

## Architecture Overview

This unified backend follows domain-driven design with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Application                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ CORS Middleware | Startup/Shutdown Events | Error Handlers │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  API v1 Router (/api/v1)                 │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐ │   │
│  │  │  Auth    │ │  Farms   │ │   NDVI   │ │ Carbon       │ │   │
│  │  │  (Phase2)│ │ (Phase4) │ │ (Phase3) │ │ (Phase5)     │ │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘ │   │
│  │  ┌──────────────────────────────────────────────────────┐ │   │
│  │  │            Reports (Phase 6)                        │ │   │
│  │  └──────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Core Infrastructure                         │   │
│  │  ┌─────────────┐ ┌────────────┐ ┌──────────────────────┐ │   │
│  │  │ Config      │ │ Database   │ │ Security (JWT/Bcrypt)│ │   │
│  │  │ (Pydantic)  │ │ (Async     │ │                      │ │   │
│  │  │             │ │ SQLAlchemy)│ │                      │ │   │
│  │  └─────────────┘ └────────────┘ └──────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            Business Logic Services                       │   │
│  │  ┌─────────────────┐ ┌──────────────────────────────────┐ │   │
│  │  │ Earth Engine    │ │ Farm Management                  │ │   │
│  │  │ Services        │ │ Carbon Estimation               │ │   │
│  │  │ (NDVI, LULC)    │ │ Reporting                        │ │   │
│  │  └─────────────────┘ └──────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
         ┌──────────▼──────────┐   ┌────▼──────────────┐
         │  PostgreSQL +       │   │  SQLite (dev)     │
         │  PostGIS (prod)     │   │                   │
         └─────────────────────┘   └───────────────────┘
                    │
         ┌──────────▼──────────────┐
         │ Google Earth Engine API │
         │ (NDVI, LULC, imagery)   │
         └─────────────────────────┘
```

## Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app, CORS, startup/shutdown
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py               # Pydantic Settings, environment vars
│   │   ├── database.py             # Async SQLAlchemy, PostGIS, sessions
│   │   └── security.py             # JWT, bcrypt, OAuth2 scheme
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                 # BaseModel with id, created_at, updated_at
│   │   └── [models to be added in subsequent phases]
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       └── __init__.py         # API router aggregation
│   │       └── [endpoint modules to be added]
│   └── services/
│       ├── __init__.py
│       └── [business logic to be added in subsequent phases]
├── alembic/
│   ├── versions/
│   │   └── [migration files]
│   ├── env.py                      # Async migration configuration
│   └── script.py.mako              # Migration template
├── alembic.ini                     # Alembic configuration
├── requirements.txt                # All dependencies
├── .env.example                    # Environment variable template
├── .env                            # Actual environment variables (gitignored)
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 15+ with PostGIS extension (production) OR SQLite (development)
- pip (Python package manager)
- OpenSSL (for generating SECRET_KEY)

### Optional
- Docker & Docker Compose (for containerized PostgreSQL)
- Google Cloud project with Earth Engine API enabled

## Installation & Setup

### 1. Clone and Navigate to Project

```bash
cd /path/to/TrueCarbon/backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# PostgreSQL setup (production)
DATABASE_URL=postgresql://user:password@localhost:5432/truecarbon

# Or SQLite setup (development)
DATABASE_URL=sqlite+aiosqlite:///./truecarbon.db

# Generate with: openssl rand -hex 32
SECRET_KEY=your-generated-secret-key-here

# Google Earth Engine
GEE_PROJECT=your-gee-project-id

# Environment
ENVIRONMENT=development
```

### 5. Initialize Database & Run Migrations

```bash
alembic upgrade head
```

This creates all base tables with timestamps and indexes.

### 6. Run Development Server

```bash
uvicorn app.main:app --reload
```

Server starts at `http://localhost:8000`

API documentation available at: `http://localhost:8000/api/v1/docs`

## API Endpoints Reference

### Health Checks
- `GET /` - Service health status
- `GET /health` - Database connectivity check

### API v1 Status
- `GET /api/v1/status` - List of available API v1 endpoints

### Planned Endpoints (Subsequent Phases)

**Authentication (Phase 2)**
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user profile

**Farms (Phase 4)**
- `GET /api/v1/farms` - List user's farms
- `POST /api/v1/farms` - Create new farm
- `GET /api/v1/farms/{farm_id}` - Get farm details
- `PUT /api/v1/farms/{farm_id}` - Update farm
- `DELETE /api/v1/farms/{farm_id}` - Delete farm

**NDVI (Phase 3)**
- `POST /api/v1/ndvi/analyze` - Compute NDVI for farm geometry
- `GET /api/v1/ndvi/{analysis_id}` - Get NDVI results
- `GET /api/v1/ndvi/timeseries/{farm_id}` - Historical NDVI time series

**LULC (Phase 3)**
- `POST /api/v1/lulc/classify` - Classify land use/cover
- `GET /api/v1/lulc/{classification_id}` - Get classification results

**Carbon (Phase 5)**
- `POST /api/v1/carbon/estimate` - Estimate carbon stock
- `GET /api/v1/carbon/{farm_id}` - Get carbon measurements
- `GET /api/v1/carbon/trend/{farm_id}` - Historical carbon trend

**Reports (Phase 6)**
- `GET /api/v1/reports/{farm_id}/pdf` - Generate PDF report
- `GET /api/v1/reports/{farm_id}/csv` - Export CSV data

## Database Management

### Create a New Migration

After modifying models, create an auto-generated migration:

```bash
alembic revision --autogenerate -m "Add user model"
```

Review the generated file in `alembic/versions/`, then apply:

```bash
alembic upgrade head
```

### View Migration History

```bash
alembic history
```

### Rollback to Previous State

```bash
alembic downgrade -1  # One migration back
alembic downgrade -2  # Two migrations back
```

## Testing

Run tests with pytest:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app
```

## Development Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/new-endpoint
   ```

2. **Make changes** to relevant modules

3. **Create migration** if modifying models
   ```bash
   alembic revision --autogenerate -m "description"
   ```

4. **Test locally**
   ```bash
   pytest
   uvicorn app.main:app --reload
   ```

5. **Push and create pull request**

## Security Considerations

### Password Security
- Uses bcrypt with automatic salt generation
- Never store plaintext passwords
- Passwords validated before hashing

### JWT Tokens
- Access tokens expire in 30 minutes (configurable)
- Refresh tokens expire in 7 days (configurable)
- Tokens signed with SECRET_KEY
- Use `Authorization: Bearer <token>` header

### Database Security
- Async SQLAlchemy prevents SQL injection
- Pydantic validates all input
- Environment variables for sensitive data
- PostGIS spatial queries with proper indexing

### CORS Configuration
- Restrict to known frontend URLs in production
- Default: `http://localhost:3000` (development only)

## Environment Configuration

Configuration uses Pydantic Settings with environment file support:

| Variable | Default | Description |
|----------|---------|-------------|
| `PROJECT_NAME` | True Carbon API | API title |
| `VERSION` | 1.0.0 | API version |
| `API_V1_PREFIX` | /api/v1 | API endpoint prefix |
| `DATABASE_URL` | required | Database connection string |
| `SECRET_KEY` | required | JWT signing key (32+ chars) |
| `ALGORITHM` | HS256 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 7 | Refresh token lifetime |
| `GEE_PROJECT` | required | Google Earth Engine project ID |
| `GEE_SERVICE_ACCOUNT` | optional | GEE service account JSON |
| `CORS_ORIGINS` | ["http://localhost:3000"] | Allowed CORS origins |
| `ENVIRONMENT` | development | Environment name |

## Docker Setup (Optional)

For PostgreSQL with PostGIS:

```bash
docker run -d \
  --name truecarbon-db \
  -e POSTGRES_USER=truecarbon \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=truecarbon \
  -p 5432:5432 \
  postgis/postgis:15-3.3
```

Update DATABASE_URL in `.env`:
```
DATABASE_URL=postgresql://truecarbon:password@localhost:5432/truecarbon
```

## Integration with Frontend

Frontend proxy configuration (if using mock Express server as fallback):

**File:** `frontend/true_carbon/dashboard/frontend/src/services/api.js`

Example frontend call:
```javascript
const response = await axios.get('/api/v1/farms', {
  headers: { Authorization: `Bearer ${token}` }
});
```

Development: Backend at `http://localhost:8000`
Production: Backend at `https://api.truecarbon.com`

## Migration from Previous Backends

### From `backend_v1` (NDVI)
- NDVI logic from `backend_v1/ndvi.py` → `backend/app/services/ndvi_service.py` (Phase 3)
- Earth Engine initialization → `backend/app/services/earth_engine.py` (lazy loading)
- API endpoints → `backend/app/api/v1/ndvi.py`

### From `backend_v2` (LULC & Carbon)
- Phase 2 logic from `backend_v2/phases/phase2.py` → `backend/app/services/lulc_service.py` (Phase 3)
- Carbon calculations → `backend/app/services/carbon_service.py` (Phase 5)
- FPDF reporting → `backend/app/api/v1/reports.py` (Phase 6)
- Streamlit removed; replace with FastAPI endpoints

### From `frontend/true_carbon/backend` (Auth)
- User model patterns → `backend/app/models/user.py` (Phase 2)
- Password hashing → Uses `backend/app/core/security.py`
- Database patterns → Async SQLAlchemy with same config pattern
- Auth endpoints → `backend/app/api/v1/auth.py` (Phase 2)

## Phase Roadmap

**Phase 1 (Current):** ✅ Core infrastructure
- ✅ Async SQLAlchemy with PostGIS
- ✅ Environment configuration with Pydantic Settings
- ✅ JWT & bcrypt security layer
- ✅ Base model with timestamps
- ✅ API v1 router structure
- ✅ Alembic migrations

**Phase 2:** Authentication & User Management
- Implement User model
- User registration & login endpoints
- JWT token refresh mechanism
- Role-based access control (RBAC)
- Password reset functionality

**Phase 3:** Earth Engine Services
- NDVI computation service (from `backend_v1`)
- LULC classification service (from `backend_v2`)
- Lazy Earth Engine initialization
- Time series data collection
- Imagery retrieval & caching

**Phase 4:** Farm Management
- Farm CRUD endpoints
- Geospatial boundary storage (PostGIS)
- Farm metadata & configuration
- Multi-farm user support

**Phase 5:** Carbon Estimation
- IPCC Tier 2 methodology implementation
- Carbon stock calculation service
- Measurement storage & versioning
- Carbon trend analysis

**Phase 6:** Reporting & Export
- PDF report generation (FPDF from `backend_v2`)
- CSV data export
- Chart visualization data
- Report caching & delivery

**Phase 7:** Frontend Integration
- Connect frontend to real API endpoints
- Replace mock Express server
- JWT-based authentication flow
- Real-time data loading

## Troubleshooting

### Database Connection Error
```
sqlalchemy.exc.OperationalError: unable to connect
```
- Verify DATABASE_URL in `.env`
- Check PostgreSQL/SQLite service is running
- Ensure database exists and credentials are correct

### SECRET_KEY Error
```
pydantic_core._pydantic_core.ValidationError: 1 validation error
```
- Generate key: `openssl rand -hex 32`
- Add to `.env`: `SECRET_KEY=<generated-key>`

### GEE Authentication Error
```
ee.EEException: Invalid credentials
```
- Verify GEE_PROJECT in `.env`
- For service account, set GEE_SERVICE_ACCOUNT JSON
- Ensure GEE project has Earth Engine API enabled

### PostGIS Extension Error
```
ProgrammingError: CREATE EXTENSION requires superuser privilege
```
- Use PostgreSQL superuser account, or
- Ask database admin to enable PostGIS, or
- Use SQLite for development

### Migration Conflicts
```
alembic.util.exc.CommandError: Can't find base revision
```
- Ensure models import `BaseModel` from `backend/app/models/base.py`
- Run: `alembic stamp head` to sync version

## Contributing

1. Follow the modular structure: keep features in separate routers
2. Use async/await for all I/O operations
3. Add type hints to all functions
4. Write tests for new endpoints
5. Document complex business logic
6. Keep dependencies updated: `pip list --outdated`

## License

Part of the True Carbon project. See root LICENSE file.

## Support

For issues or questions:
1. Check this README and inline code documentation
2. Review upcoming phase documentation
3. Check FastAPI docs: https://fastapi.tiangolo.com
4. SQLAlchemy async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
5. Alembic docs: https://alembic.sqlalchemy.org
