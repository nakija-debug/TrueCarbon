# TrueCarbon Development & Deployment Guide

## Quick Start for Developers

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Git
- Mapbox API Token
- Google Earth Engine Account

### Backend Setup (5 minutes)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp ../.env.example .env
# Edit .env with your configuration

# Database setup
alembic upgrade head

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend is ready at**: http://localhost:8000
**API Docs**: http://localhost:8000/docs
**Alternative Docs**: http://localhost:8000/redoc

### Frontend Setup (5 minutes)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.local.example .env.local
# Edit .env.local with your tokens (especially NEXT_PUBLIC_MAPBOX_TOKEN)

# Run development server
npm run dev
```

**Frontend is ready at**: http://localhost:3000

---

## Environment Configuration

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/truecarbon
SQLALCHEMY_ECHO=False

# JWT
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Google Earth Engine
EE_PROJECT_ID=your-project-id
EE_PRIVATE_KEY_PATH=path/to/service-account-key.json

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# API
API_TITLE=TrueCarbon API
API_VERSION=2.0.0
DEBUG=True  # Set to False in production
```

### Frontend (.env.local)
```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1

# Mapbox
NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token_here

# Feature Flags
NEXT_PUBLIC_ENABLE_BETA_FEATURES=false
```

---

## Database Setup

### First Time Setup
```bash
cd backend

# Initialize database
createdb truecarbon

# Run migrations
alembic upgrade head

# Verify tables created
psql truecarbon -c "\dt"
```

### View Alembic History
```bash
alembic history --verbose
```

### Create New Migration
```bash
alembic revision --autogenerate -m "description of changes"
alembic upgrade head
```

---

## Testing

### Run Backend Tests
```bash
cd backend

# Run all tests
pytest tests/ -v

# Run Phase 5 tests
pytest test_phase5.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/services/test_carbon_service.py -v
```

### Test Files Location
- Unit tests: `backend/tests/services/`
- Integration test: `backend/test_phase5.py`

---

## API Testing

### Using cURL

**Login**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'
```

**Get Farms**:
```bash
curl -X GET http://localhost:8000/api/v1/farms \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Create Carbon Estimate**:
```bash
curl -X POST http://localhost:8000/api/v1/carbon/estimate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "farm_id": 1,
    "land_type": "forest",
    "geometry": {...}
  }'
```

### Using Postman

1. Import the OpenAPI spec from `http://localhost:8000/openapi.json`
2. Set authorization header with Bearer token
3. Use provided request templates

---

## Common Development Tasks

### Add a New API Endpoint

1. **Create schema** (`backend/app/schemas/my_schema.py`):
```python
from pydantic import BaseModel

class MyRequest(BaseModel):
    field1: str
    field2: int

class MyResponse(BaseModel):
    result: str
```

2. **Create route** (`backend/app/api/v1/my_route.py`):
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.my_schema import MyRequest, MyResponse

router = APIRouter(prefix="/my-endpoint", tags=["my-endpoint"])

@router.post("", response_model=MyResponse)
async def create_item(request: MyRequest, db: AsyncSession = Depends(get_db)):
    # Your logic here
    return MyResponse(result="success")
```

3. **Register in main** (`backend/app/main.py`):
```python
from app.api.v1 import my_route
app.include_router(my_route.router, prefix="/api/v1")
```

### Add a New React Component

1. **Create component** (`frontend/components/my-component.tsx`):
```typescript
'use client';

import React from 'react';

export function MyComponent() {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6">
      {/* Component content */}
    </div>
  );
}
```

2. **Add to dashboard** (`frontend/app/dashboard/page.tsx`):
```typescript
import { MyComponent } from '@/components/my-component';

export default function Dashboard() {
  return (
    <div className="space-y-4">
      <MyComponent />
    </div>
  );
}
```

---

## Production Deployment

### Backend Deployment

#### Using Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run**:
```bash
docker build -t truecarbon-backend .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://... \
  -e SECRET_KEY=... \
  truecarbon-backend
```

#### Using Gunicorn
```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Deployment

#### Using Vercel (Recommended)
```bash
npm install -g vercel
vercel
# Follow prompts to deploy
```

#### Using Docker
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY package*.json ./
RUN npm ci --production
EXPOSE 3000
CMD ["npm", "start"]
```

### Database in Production

```bash
# Backup
pg_dump truecarbon > backup.sql

# Restore
psql truecarbon < backup.sql

# Connect to production
psql postgresql://user:pass@prod-host:5432/truecarbon
```

---

## Monitoring & Debugging

### Backend Logs
```bash
# With timestamps
uvicorn app.main:app --reload --log-level debug

# See database queries
SQLALCHEMY_ECHO=True
```

### Frontend Debug Mode
```bash
# Development with source maps
npm run dev

# Check for build errors
npm run build
```

### Database Queries
```bash
# Connect to database
psql truecarbon

# List tables
\dt

# View schema
\d farm

# Execute query
SELECT * FROM farms LIMIT 10;
```

---

## Troubleshooting

### Common Issues

**"Database connection refused"**
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Create database if needed
createdb truecarbon

# Verify connection string in .env
```

**"Google Earth Engine authentication failed"**
```bash
# Verify GEE credentials
gcloud auth application-default login

# Check file path in .env
ls -la path/to/service-account-key.json
```

**"Mapbox token invalid"**
```bash
# Get new token from https://account.mapbox.com/
# Update in frontend .env.local
NEXT_PUBLIC_MAPBOX_TOKEN=your_new_token
```

**"Port already in use"**
```bash
# Backend (change port)
uvicorn app.main:app --port 8001

# Frontend (change port)
npm run dev -- -p 3001
```

---

## Code Style & Conventions

### Python (Backend)
- Follow PEP 8
- Use type hints for all functions
- Class names: PascalCase
- Function/variable names: snake_case
- Module docstrings required

### TypeScript (Frontend)
- Use TypeScript strictly (strict mode enabled)
- Class names: PascalCase
- Function/variable names: camelCase
- Component names: PascalCase
- Props interfaces end with "Props"
- All components should be exported

---

## Resources & Documentation

### Official Docs
- FastAPI: https://fastapi.tiangolo.com/
- Next.js: https://nextjs.org/docs
- SQLAlchemy: https://docs.sqlalchemy.org/
- PostgreSQL: https://www.postgresql.org/docs/
- React Query: https://tanstack.com/query/latest
- Mapbox GL JS: https://docs.mapbox.com/mapbox-gl-js/

### Project Files
- [API Reference](API_REFERENCE_PHASE5.md)
- [Phase 5 Completion](PHASE_5_FINAL_COMPLETION.md)
- [Backend README](backend/README.md)

---

## Getting Help

1. **Check Documentation**: Review [PHASE_5_FINAL_COMPLETION.md](PHASE_5_FINAL_COMPLETION.md)
2. **Review Examples**: Check tests and existing components
3. **API Docs**: Visit `/docs` endpoint when backend is running
4. **Type Hints**: Use IDE autocomplete for API reference

---

## Useful Commands Reference

```bash
# Backend
cd backend
uvicorn app.main:app --reload
pytest tests/ -v
alembic upgrade head
alembic revision --autogenerate -m "message"

# Frontend
cd frontend
npm run dev
npm run build
npm run lint
npm test

# Database
psql truecarbon
pg_dump truecarbon > backup.sql
psql truecarbon < backup.sql

# Git
git status
git add .
git commit -m "message"
git push origin main
```

---

**Last Updated**: 2024
**Version**: 2.0.0
**Status**: Production Ready
