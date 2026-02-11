# TrueCarbon - Deployment Checklist & Quick Start

**Version**: 2.0.0
**Status**: Production Ready
**Last Updated**: January 2024

---

## 🚀 Quick Start (5 minutes)

### Fastest Way to Get Started

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd TrueCarbon

# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Start the backend
uvicorn app.main:app --reload

# Frontend Setup (in new terminal)
cd frontend
npm install
npm run dev

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## ✅ Pre-Deployment Checklist

### Prerequisites
- [ ] Python 3.11 or higher installed
- [ ] Node.js 18+ and npm installed
- [ ] PostgreSQL 14+ installed and running
- [ ] Git installed
- [ ] Mapbox account and API token
- [ ] Google Earth Engine account configured

### Database Setup
- [ ] PostgreSQL database created (truecarbon)
- [ ] Database user created with proper permissions
- [ ] Database connection tested
- [ ] Alembic migrations applied
- [ ] Tables verified with \dt command

### Backend Configuration
- [ ] .env file created with all required variables
- [ ] SECRET_KEY generated (use: `openssl rand -hex 32`)
- [ ] DATABASE_URL correctly configured
- [ ] Google Earth Engine credentials configured
- [ ] CORS_ORIGINS set to frontend URL
- [ ] DEBUG set to False for production

### Frontend Configuration
- [ ] .env.local file created
- [ ] NEXT_PUBLIC_API_BASE_URL set to backend URL
- [ ] NEXT_PUBLIC_MAPBOX_TOKEN added
- [ ] Build succeeds without errors
- [ ] TypeScript checks pass

---

## 📋 Environment Variables Checklist

### Backend (.env)

```env
# Database
[ ] DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/truecarbon

# Security
[ ] SECRET_KEY=<generated-secret-key>
[ ] ALGORITHM=HS256
[ ] ACCESS_TOKEN_EXPIRE_MINUTES=30
[ ] REFRESH_TOKEN_EXPIRE_DAYS=7

# Google Earth Engine (if using satellite features)
[ ] EE_PROJECT_ID=<your-project-id>
[ ] EE_PRIVATE_KEY_PATH=path/to/service-account-key.json

# API Configuration
[ ] API_TITLE=TrueCarbon API
[ ] API_VERSION=2.0.0
[ ] DEBUG=False  # Must be False in production
[ ] CORS_ORIGINS=["https://yourdomain.com"]  # Update for production

# Optional: Monitoring
[ ] SENTRY_DSN=<optional-sentry-dsn>
[ ] LOG_LEVEL=INFO
```

### Frontend (.env.local)

```env
# API
[ ] NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com/api/v1

# Mapbox
[ ] NEXT_PUBLIC_MAPBOX_TOKEN=<your-mapbox-token>

# Optional: Monitoring
[ ] NEXT_PUBLIC_SENTRY_DSN=<optional-sentry-dsn>
```

---

## 🗄️ Database Setup

### Create Database

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE truecarbon;

-- Create user
CREATE USER truecarbon_user WITH PASSWORD 'secure_password_here';

-- Grant privileges
ALTER ROLE truecarbon_user SET client_encoding TO 'utf8';
ALTER ROLE truecarbon_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE truecarbon_user SET default_transaction_deferrable TO on;
ALTER ROLE truecarbon_user SET default_time_zone TO 'UTC';

-- Grant superuser privileges to install extensions
ALTER ROLE truecarbon_user WITH SUPERUSER;

GRANT ALL PRIVILEGES ON DATABASE truecarbon TO truecarbon_user;
```

### Apply Migrations

```bash
cd backend
alembic upgrade head
```

### Verify Setup

```bash
psql -U truecarbon_user -d truecarbon -c "\dt"
```

Expected output: Tables listed (users, companies, farms, measurements, etc.)

---

## 🔧 Build & Test

### Backend Build

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run linting (optional)
pip install pylint
pylint app/

# Run type checking
mypy app/ --ignore-missing-imports

# Run tests
pytest tests/ -v

# Generate coverage report
pytest tests/ --cov=app --cov-report=html
```

### Frontend Build

```bash
cd frontend

# Install dependencies
npm install

# Type check
npm run type-check

# Build
npm run build

# Start test server
npm run build
npm start
```

---

## 🚢 Deployment Options

### Option 1: Local/Development Server

**Best for**: Testing, development, small deployments

#### Backend
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm run dev
# or for production simulation:
npm run build && npm start
```

---

### Option 2: Docker Deployment

**Best for**: Production, containerized environments, cloud platforms

#### Build Backend Image
```bash
cd backend
docker build -t truecarbon-backend:2.0.0 .
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://..." \
  -e SECRET_KEY="..." \
  truecarbon-backend:2.0.0
```

#### Build Frontend Image
```bash
cd frontend
docker build -t truecarbon-frontend:2.0.0 .
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_BASE_URL="http://api.yourdomain.com/api/v1" \
  -e NEXT_PUBLIC_MAPBOX_TOKEN="..." \
  truecarbon-frontend:2.0.0
```

#### Docker Compose (Complete Stack)
```yaml
version: '3.8'

services:
  postgres:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: truecarbon
      POSTGRES_USER: truecarbon_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql+asyncpg://truecarbon_user:secure_password@postgres:5432/truecarbon
      SECRET_KEY: your-secret-key
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    depends_on:
      - backend
    environment:
      NEXT_PUBLIC_API_BASE_URL: http://backend:8000/api/v1
      NEXT_PUBLIC_MAPBOX_TOKEN: your-mapbox-token
    ports:
      - "3000:3000"

volumes:
  postgres_data:
```

Run with: `docker-compose up -d`

---

### Option 3: Cloud Deployment

#### Vercel (Frontend) - Recommended
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

Configuration (vercel.json):
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "env": [
    {
      "key": "NEXT_PUBLIC_API_BASE_URL",
      "value": "https://api.yourdomain.com/api/v1"
    },
    {
      "key": "NEXT_PUBLIC_MAPBOX_TOKEN",
      "value": "@mapbox_token"
    }
  ]
}
```

#### AWS (Backend Example)
```bash
# Option 1: Deploy to AWS Lambda + ECS
# Use Zappa or Lambda function directly

# Option 2: Deploy to ECS
aws ecs create-service --cluster truecarbon-prod --service-name backend --task-definition truecarbon-backend ...

# Option 3: Deploy to EC2
# Build Docker image, push to ECR, and deploy
```

#### Google Cloud Run (Backend) - Recommended
```bash
# Authenticate
gcloud auth login

# Build and deploy
gcloud run deploy truecarbon-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=postgresql+asyncpg://...
```

#### Heroku (Quick Deployment)
```bash
# Authenticate
heroku login

# Create app
heroku create truecarbon-backend

# Set environment variables
heroku config:set DATABASE_URL=postgresql+asyncpg://...
heroku config:set SECRET_KEY=...

# Deploy
git push heroku main
```

---

## 🔐 Security Checklist

Before going to production:

### Secrets Management
- [ ] SECRET_KEY is strong (32+ random characters)
- [ ] Database passwords are strong
- [ ] No secrets in version control
- [ ] No secrets in environment files (use .env.local)
- [ ] Use secrets manager (AWS Secrets Manager, Vault, etc.)

### Database Security
- [ ] Database backups configured
- [ ] Database encryption enabled (if cloud-based)
- [ ] Restricted database user permissions
- [ ] Connection pooling configured
- [ ] Regular backups tested and verified

### API Security
- [ ] HTTPS/TLS enabled in production
- [ ] CORS properly configured (no wildcard *)
- [ ] Rate limiting enabled
- [ ] JWT token expiration set appropriately
- [ ] Password requirements enforced

### Frontend Security
- [ ] No API keys in JavaScript bundles
- [ ] HTTPS enforced
- [ ] CSP headers configured
- [ ] XSS protection enabled
- [ ] Regular security updates

### Monitoring & Logging
- [ ] Logging enabled for all API calls
- [ ] Error tracking configured (Sentry, etc.)
- [ ] Performance monitoring set up
- [ ] Database query logging enabled
- [ ] Access logs configured

---

## 📊 Setup Verification

After deployment, verify everything is working:

### Backend Checks
```bash
# Check API is running
curl http://localhost:8000/docs

# Check database connection
curl http://localhost:8000/api/v1/health

# Test authentication endpoint
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test"}'
```

### Frontend Checks
```bash
# Check frontend loads
curl http://localhost:3000

# Check API connectivity
curl http://localhost:3000/_next/static/
```

### Database Checks
```bash
# Connect to database
psql -U truecarbon_user -d truecarbon

# Verify tables
\dt

# Check row counts
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM farms;
SELECT COUNT(*) FROM measurements;
```

---

## 🔄 Maintenance & Updates

### Regular Maintenance Tasks

**Daily**:
- [ ] Check application logs for errors
- [ ] Monitor database performance
- [ ] Check API response times

**Weekly**:
- [ ] Review error reports
- [ ] Check for security updates
- [ ] Verify backups completed

**Monthly**:
- [ ] Database optimization
- [ ] Update dependencies
- [ ] Security audit
- [ ] Performance review

### Database Backups

```bash
# Manual backup
pg_dump -U truecarbon_user -d truecarbon > backup_$(date +%Y%m%d).sql

# Automated backup (cron job)
0 2 * * * pg_dump -U truecarbon_user -d truecarbon > /backups/truecarbon_$(date +\%Y\%m\%d).sql

# Restore from backup
psql -U truecarbon_user -d truecarbon < backup_20240115.sql
```

### Update Dependencies

```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update
npm outdated  # Check for updates
```

---

## 🆘 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Test connection
psql -U truecarbon_user -d truecarbon -c "SELECT 1"

# Check DATABASE_URL in .env
echo $DATABASE_URL
```

**Port Already in Use**
```bash
# Find process using port
lsof -i :8000
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

**Google Earth Engine Error**
```bash
# Verify credentials
gcloud auth list

# Reinitialize EE
python -c "import ee; ee.Initialize(); print('Connected')"
```

**Frontend Build Error**
```bash
cd frontend
rm -rf .next node_modules package-lock.json
npm install
npm run build
```

---

## 📈 Performance Optimization

### Backend Optimization
- Enable database connection pooling
- Use Redis for caching (optional)
- Add database query indexes
- Implement request pagination
- Use async/await throughout

### Frontend Optimization
- Enable Next.js image optimization
- Use dynamic imports for large components
- Enable gzip compression
- Set up CDN for static assets
- Enable service worker for offline support

---

## 📞 Post-Deployment Support

### Monitoring Setup

**Recommended Tools**:
- Sentry: Error tracking
- DataDog: Full monitoring
- New Relic: APM
- LogRocket: Frontend monitoring

### Health Checks

```bash
# Add health check endpoint to monitor
curl http://yourdomain.com/api/v1/health

# Should return 200 OK with status
```

---

## 🎯 Final Checklist Before Going Live

- [ ] All environment variables configured
- [ ] Database backup strategy in place
- [ ] SSL/TLS certificate installed
- [ ] DNS configured correctly
- [ ] Monitoring and alerting set up
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Documentation complete
- [ ] Team trained on operations
- [ ] Incident response plan ready
- [ ] 24/7 support plan in place
- [ ] Rollback plan documented

---

## 📞 Support Resources

- **API Documentation**: `/docs` endpoint when server running
- **GitHub Issues**: Check repository issues for solutions
- **Type Definitions**: Check `frontend/types/` for API types
- **Examples**: Check test files for usage examples

---

## Version Information

- **TrueCarbon Version**: 2.0.0
- **Python Version**: 3.11+
- **Node.js Version**: 18+
- **PostgreSQL Version**: 14+
- **Next.js Version**: 14.0.0
- **React Version**: 18.2.0

---

**Last Updated**: January 2024
**Status**: Production Ready
**Approval**: ✅ Verified

For more detailed information, see:
- [PHASE_5_FINAL_COMPLETION.md](../PHASE_5_FINAL_COMPLETION.md)
- [DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md)
- [API_REFERENCE_COMPLETE.md](../API_REFERENCE_COMPLETE.md)
