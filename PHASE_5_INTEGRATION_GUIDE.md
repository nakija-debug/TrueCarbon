# Phase 5: Satellite Health Monitoring - Integration Guide

## Overview

This guide covers integrating satellite health monitoring into the TrueCarbon platform frontend and backend systems.

## Backend Integration

### 1. Database Setup

#### Apply Migration
```bash
cd backend
alembic upgrade head
```

#### Verify Migration
```bash
psql -h localhost -U postgres -d truecarbon \
  -c "SELECT * FROM satellite_status ORDER BY satellite_name;"
```

#### Initialize Historical Data
```python
# backend/scripts/init_satellite_health.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.satellite_status import SatelliteStatus
from app.services.satellite_health_service import SatelliteHealthService
from app.core.config import settings

async def initialize_satellite_health():
    """Initialize satellite health records."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as db:
        service = SatelliteHealthService()
        print("Initializing satellite health data...")
        await service.update_all_satellite_status(db)
        print("Initialization complete!")

if __name__ == "__main__":
    asyncio.run(initialize_satellite_health())
```

Run:
```bash
python backend/scripts/init_satellite_health.py
```

### 2. Background Task Setup

#### Configure APScheduler

```python
# backend/app/main.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager

from app.services.satellite_health_service import SatelliteHealthService
from app.core.database import AsyncSessionLocal

# Global scheduler instance
scheduler = None

async def update_satellite_health():
    """Background task to update satellite health."""
    db = AsyncSessionLocal()
    try:
        service = SatelliteHealthService()
        await service.update_all_satellite_status(db)
        logger.info("Background satellite health check completed")
    except Exception as e:
        logger.error(f"Background health check failed: {e}")
    finally:
        await db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        update_satellite_health,
        "interval",
        minutes=60,  # Every hour
        id="satellite_health_check",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Satellite health scheduler started")
    yield
    # Shutdown
    scheduler.shutdown(wait=False)
    logger.info("Satellite health scheduler stopped")

app = FastAPI(
    title="TrueCarbon API",
    lifespan=lifespan
)
```

#### Install APScheduler

```bash
pip install apscheduler
```

### 3. Environment Configuration

Add to `.env`:
```bash
# Satellite Health Check Interval (minutes)
SATELLITE_HEALTH_CHECK_INTERVAL=60

# Earth Engine Configuration
EARTHENGINE_ACCOUNT=<your-service-account-email>
EARTHENGINE_KEY_PATH=/path/to/service-account-key.json

# Database Health History Retention (days)
SATELLITE_HEALTH_RETENTION_DAYS=30
```

Update `config.py`:
```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...
    
    SATELLITE_HEALTH_CHECK_INTERVAL: int = 60  # minutes
    SATELLITE_HEALTH_RETENTION_DAYS: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True
```

### 4. Service Integration

#### Use in Carbon Calculations

```python
# backend/app/services/carbon_calculation_service.py
from app.services.satellite_health_service import SatelliteHealthService

class CarbonCalculationService:
    def __init__(self):
        self.health_service = SatelliteHealthService()
    
    async def calculate_with_health_check(
        self, 
        db: AsyncSession,
        farm_id: int,
        satellite_name: str
    ):
        """Calculate carbon with satellite health check."""
        # Check satellite health first
        summary = await self.health_service.get_satellite_health_summary(db)
        
        sat = next(
            (s for s in summary['satellites'] 
             if s.satellite_name == satellite_name),
            None
        )
        
        if not sat or sat.status == 'offline':
            raise ValueError(f"Satellite {satellite_name} is offline")
        
        if sat.status == 'degraded':
            logger.warning(
                f"Using degraded satellite {satellite_name}: "
                f"coverage={sat.coverage_percent}%"
            )
        
        # Proceed with calculation
        return await self.calculate_carbon(db, farm_id)
```

#### Use in NDVI Calculations

```python
# backend/app/services/ndvi_service.py
from app.services.satellite_health_service import SatelliteHealthService

class NDVIService:
    def __init__(self):
        self.health_service = SatelliteHealthService()
    
    async def get_ndvi_with_health(self, db: AsyncSession, area_id: int):
        """Get NDVI with satellite health validation."""
        # Get health status
        summary = await self.health_service.get_satellite_health_summary(db)
        
        # Log health info
        logger.info(
            f"NDVI query - "
            f"Operational: {summary['operational_count']}, "
            f"Degraded: {summary['degraded_count']}, "
            f"Offline: {summary['offline_count']}"
        )
        
        # Perform NDVI calculation with healthy satellites
        for sat in summary['satellites']:
            if sat.status != 'offline':
                try:
                    return await self.calculate_ndvi(area_id, sat.satellite_name)
                except Exception as e:
                    logger.warning(f"NDVI calc with {sat.satellite_name} failed: {e}")
        
        raise ValueError("No operational satellites available for NDVI")
```

---

## Frontend Integration

### 1. Create Satellite Health Hook (React)

```typescript
// frontend/hooks/use-satellite-health.ts
import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

interface SatelliteHealth {
  satellite_name: string;
  status: 'operational' | 'degraded' | 'offline' | 'unknown';
  coverage_percent: number;
  accuracy_percent: number;
  data_quality: 'high' | 'medium' | 'low' | 'unknown';
  last_update: string;
  uptime_percent: number;
  metadata: Record<string, any>;
}

interface SatelliteHealthSummary {
  satellites: SatelliteHealth[];
  total_satellites: number;
  operational_count: number;
  degraded_count: number;
  offline_count: number;
  average_uptime: number;
  last_check: string;
}

export function useSatelliteHealth(
  refresh: boolean = false
): UseQueryResult<SatelliteHealthSummary> {
  return useQuery({
    queryKey: ['satellite-health', refresh],
    queryFn: async () => {
      const params = new URLSearchParams({
        refresh: refresh.toString()
      });
      const response = await apiClient.get(
        `/satellites/health?${params}`
      );
      return response.data;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 10000, // Cache for 10 seconds
    enabled: true
  });
}

export function useSatelliteHealthByName(
  satelliteName: string
): UseQueryResult<SatelliteHealth> {
  return useQuery({
    queryKey: ['satellite-health', satelliteName],
    queryFn: async () => {
      const response = await apiClient.get(
        `/satellites/health/${satelliteName}`
      );
      return response.data;
    },
    refetchInterval: 30000,
    staleTime: 10000
  });
}

export function useRefreshSatelliteHealth() {
  return useMutation({
    mutationFn: async () => {
      const response = await apiClient.post('/satellites/health/refresh');
      return response.data;
    }
  });
}
```

### 2. Satellite Status Card Component

```typescript
// frontend/components/satellite-status-card.tsx
import React from 'react';
import { 
  Card, 
  CardContent, 
  CardHeader 
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert } from '@/components/ui/alert';

interface SatelliteStatusCardProps {
  satellite_name: string;
  status: string;
  coverage_percent: number;
  accuracy_percent: number;
  data_quality: string;
  uptime_percent: number;
  last_update: string;
}

export function SatelliteStatusCard({
  satellite_name,
  status,
  coverage_percent,
  accuracy_percent,
  data_quality,
  uptime_percent,
  last_update
}: SatelliteStatusCardProps) {
  
  const statusColor = {
    'operational': 'bg-green-100 text-green-800',
    'degraded': 'bg-yellow-100 text-yellow-800',
    'offline': 'bg-red-100 text-red-800',
    'unknown': 'bg-gray-100 text-gray-800'
  }[status] || 'bg-gray-100 text-gray-800';

  const qualityColor = {
    'high': 'bg-blue-100 text-blue-800',
    'medium': 'bg-amber-100 text-amber-800',
    'low': 'bg-orange-100 text-orange-800',
    'unknown': 'bg-gray-100 text-gray-800'
  }[data_quality] || 'bg-gray-100 text-gray-800';

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <div className="text-lg font-semibold capitalize">
          {satellite_name.replace('-', ' ')}
        </div>
        <Badge className={statusColor}>
          {status}
        </Badge>
      </CardHeader>
      <CardContent className="space-y-4">
        {status === 'offline' && (
          <Alert className="bg-red-50 border-red-200">
            <span className="text-red-800">
              This satellite is currently offline
            </span>
          </Alert>
        )}
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Coverage</p>
            <p className="text-2xl font-bold">{coverage_percent.toFixed(1)}%</p>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${coverage_percent}%` }}
              />
            </div>
          </div>
          
          <div>
            <p className="text-sm text-gray-600">Accuracy</p>
            <p className="text-2xl font-bold">{accuracy_percent.toFixed(1)}%</p>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div
                className="bg-green-600 h-2 rounded-full"
                style={{ width: `${accuracy_percent}%` }}
              />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-4 border-t">
          <div>
            <p className="text-xs text-gray-500 uppercase">Uptime</p>
            <p className="text-lg font-semibold">{uptime_percent.toFixed(1)}%</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase">Quality</p>
            <Badge className={qualityColor}>
              {data_quality}
            </Badge>
          </div>
        </div>

        <div className="pt-4 border-t">
          <p className="text-xs text-gray-500">
            Last updated: {new Date(last_update).toLocaleString()}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
```

### 3. Satellite Health Dashboard Panel

```typescript
// frontend/components/satellite-health-panel.tsx
import React from 'react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useSatelliteHealth, useRefreshSatelliteHealth } from '@/hooks/use-satellite-health';
import { SatelliteStatusCard } from './satellite-status-card';
import { Spinner } from '@/components/ui/spinner';
import { Alert, AlertDescription } from '@/components/ui/alert';

export function SatelliteHealthPanel() {
  const { data: health, isLoading, error, refetch } = useSatelliteHealth();
  const { mutate: triggerRefresh, isPending: isRefreshing } = useRefreshSatelliteHealth();

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex justify-center items-center py-8">
          <Spinner />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert className="bg-red-50 border-red-200">
        <AlertDescription className="text-red-800">
          Failed to load satellite health: {(error as Error).message}
        </AlertDescription>
      </Alert>
    );
  }

  if (!health) return null;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Satellite Health Status</CardTitle>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => triggerRefresh()}
            disabled={isRefreshing}
          >
            {isRefreshing ? 'Refreshing...' : 'Refresh Now'}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        
        {/* Summary Stats */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-green-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Operational</p>
            <p className="text-3xl font-bold text-green-600">
              {health.operational_count}
            </p>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Degraded</p>
            <p className="text-3xl font-bold text-yellow-600">
              {health.degraded_count}
            </p>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Offline</p>
            <p className="text-3xl font-bold text-red-600">
              {health.offline_count}
            </p>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Avg Uptime</p>
            <p className="text-3xl font-bold text-blue-600">
              {health.average_uptime.toFixed(1)}%
            </p>
          </div>
        </div>

        {/* Individual Satellite Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {health.satellites.map((satellite) => (
            <SatelliteStatusCard
              key={satellite.satellite_name}
              {...satellite}
            />
          ))}
        </div>

        {/* Last Check Info */}
        <div className="pt-4 border-t text-sm text-gray-500">
          Last checked: {new Date(health.last_check).toLocaleString()}
        </div>
      </CardContent>
    </Card>
  );
}
```

### 4. Integration in Dashboard

```typescript
// frontend/app/dashboard/page.tsx
import React from 'react';
import { SatelliteHealthPanel } from '@/components/satellite-health-panel';
import { KPICards } from '@/components/kpi-cards';
import { PortfolioView } from '@/components/portfolio-view';

export default function DashboardPage() {
  return (
    <div className="space-y-6 p-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      
      {/* Satellite Health Status */}
      <SatelliteHealthPanel />
      
      {/* KPIs - only show if satellites operational */}
      <KPICards />
      
      {/* Portfolio View */}
      <PortfolioView />
    </div>
  );
}
```

---

## API Client Integration

### Python Client

```python
# backend/app/clients/satellite_health_client.py
import asyncio
from typing import Optional
from app.services.satellite_health_service import SatelliteHealthService
from app.core.database import AsyncSessionLocal

class SatelliteHealthClient:
    """Client for accessing satellite health data."""
    
    def __init__(self):
        self.service = SatelliteHealthService()
    
    async def get_health(self, satellite_name: Optional[str] = None):
        """Get satellite health."""
        db = AsyncSessionLocal()
        try:
            if satellite_name:
                summary = await self.service.get_satellite_health_summary(db)
                return next(
                    (s for s in summary['satellites'] 
                     if s.satellite_name == satellite_name),
                    None
                )
            return await self.service.get_satellite_health_summary(db)
        finally:
            await db.close()
    
    async def refresh_health(self):
        """Trigger health refresh."""
        db = AsyncSessionLocal()
        try:
            await self.service.update_all_satellite_status(db)
        finally:
            await db.close()
    
    def is_operational(self, satellite_name: str) -> bool:
        """Check if satellite is operational."""
        health = asyncio.run(self.get_health(satellite_name))
        return health.status == 'operational' if health else False

# Usage in other services
satellite_client = SatelliteHealthClient()
if satellite_client.is_operational('sentinel-2'):
    # Use Sentinel-2 data
    pass
```

---

## Testing Integration

### Test Satellite Health Workflow

```python
# backend/tests/test_satellite_integration.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.satellite_health_service import SatelliteHealthService

@pytest.mark.asyncio
async def test_satellite_health_integration(db: AsyncSession):
    """Test satellite health monitoring workflow."""
    service = SatelliteHealthService()
    
    # 1. Perform health check
    await service.update_all_satellite_status(db)
    
    # 2. Verify data saved
    summary = await service.get_satellite_health_summary(db)
    assert summary['total_satellites'] == 3
    assert summary['operational_count'] > 0
    
    # 3. Verify satellite details
    sentinel2 = next(
        (s for s in summary['satellites'] 
         if s.satellite_name == 'sentinel-2'),
        None
    )
    assert sentinel2 is not None
    assert sentinel2.status in ['operational', 'degraded', 'offline']
    assert 0 <= sentinel2.coverage_percent <= 100
    assert 0 <= sentinel2.uptime_percent <= 100
```

---

## Deployment Considerations

### Production Environment

#### Docker Setup

```dockerfile
# Dockerfile additions
ENV SATELLITE_HEALTH_CHECK_INTERVAL=60
ENV EARTHENGINE_ACCOUNT=${EARTHENGINE_ACCOUNT}
ENV EARTHENGINE_KEY_PATH=/run/secrets/earthengine_key
```

#### Docker Compose

```yaml
version: '3.8'
services:
  backend:
    # ... existing config ...
    environment:
      - SATELLITE_HEALTH_CHECK_INTERVAL=60
      - EARTHENGINE_ACCOUNT=${EARTHENGINE_ACCOUNT}
    secrets:
      - earthengine_key
    volumes:
      - ${EARTHENGINE_KEY_PATH}:/run/secrets/earthengine_key:ro

secrets:
  earthengine_key:
    file: ${EARTHENGINE_KEY_PATH}
```

### Monitoring

#### Prometheus Metrics

```python
# backend/app/metrics/satellite_health.py
from prometheus_client import Gauge, Counter

satellite_health_check_duration = Gauge(
    'satellite_health_check_duration_seconds',
    'Duration of satellite health check',
    ['satellite']
)

satellite_health_check_errors = Counter(
    'satellite_health_check_errors_total',
    'Number of satellite health check errors',
    ['satellite', 'error_type']
)

satellite_operational = Gauge(
    'satellite_operational',
    'Satellite operational status',
    ['satellite']
)
```

#### Adding Metrics to Service

```python
from prometheus_client import Counter, Gauge
import time

class SatelliteHealthService:
    async def update_all_satellite_status(self, db: AsyncSession):
        for sat_name in ['sentinel-2', 'landsat-8', 'era5-land']:
            start = time.time()
            try:
                # ... health check ...
                duration = time.time() - start
                satellite_health_check_duration.labels(satellite=sat_name).set(duration)
                satellite_operational.labels(satellite=sat_name).set(1)
            except Exception as e:
                satellite_health_check_errors.labels(
                    satellite=sat_name,
                    error_type=type(e).__name__
                ).inc()
```

---

## Summary

Phase 5 integrates satellite health monitoring throughout the TrueCarbon platform:

✅ **Backend**: Database models, service layer, API endpoints
✅ **Frontend**: React hooks, components, dashboard integration
✅ **Background Tasks**: Scheduled health checks via APScheduler
✅ **Testing**: Integration tests and API testing
✅ **Monitoring**: Prometheus metrics and alerting
✅ **Deployment**: Docker and production configuration

The satellite monitoring system is now ready for production use!
