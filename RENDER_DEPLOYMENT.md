# 🚀 Render Deployment Guide for TrueCarbon

## Prerequisites
- GitHub account connected to Render
- Render account (https://render.com)

## Step 1: Create PostgreSQL Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **PostgreSQL**
3. Fill in the form:
   - **Name**: `truecarbon-postgres`
   - **Database**: `truecarbon`
   - **User**: `truecarbon_user`
   - **Region**: `us-east` (or closest to you)
   - **PostgreSQL Version**: 15
4. Click **Create Database**
5. ⏳ Wait 2-3 minutes for database to initialize
6. Copy the **External Database URL** from the dashboard (looks like: `postgresql://truecarbon_user:xxxxx@dpg-xxxxx.render.com:5432/truecarbon`)

## Step 2: Generate SECRET_KEY

Run this in your terminal:
```bash
openssl rand -hex 32
```

Copy the output (you'll need this in Step 4).

## Step 3: Create Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **Web Service**
3. Select **Deploy an existing Git repository**
4. Paste your GitHub repo URL: `https://github.com/nakija-debug/TrueCarbon.git`
5. Select **TrueCarbon** repository
6. Fill in the form:
   - **Name**: `truecarbon-api`
   - **Environment**: Python 3
   - **Region**: `us-east` (same as database)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command**: `gunicorn app.main:app --workers 3 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

## Step 4: Add Environment Variables

Click **Environment** and add these variables:

| Key | Value | Notes |
|-----|-------|-------|
| `DATABASE_URL` | `postgresql+asyncpg://truecarbon_user:PASSWORD@HOST:5432/truecarbon` | Replace with your database URL from Step 1, change `postgresql://` to `postgresql+asyncpg://` |
| `SECRET_KEY` | (paste the value from Step 2) | Generate with `openssl rand -hex 32` |
| `ENVIRONMENT` | `production` | Production environment flag |
| `PYTHONUNBUFFERED` | `1` | Ensures Python output is unbuffered |
| `CORS_ORIGINS` | `https://yourdomain.com` | Update with your frontend URL |

**Format DATABASE_URL correctly:**
- Take the URL from Render Postgres dashboard
- Change `postgresql://` → `postgresql+asyncpg://`
- Example: `postgresql+asyncpg://truecarbon_user:pw@dpg-xxxxx.render.com:5432/truecarbon`

## Step 5: Create the Web Service

Click **Create Web Service** and wait for deployment (5-10 minutes).

## Step 6: Verify Deployment

After deployment is complete:

1. Go to your Web Service dashboard
2. Copy the URL (looks like: `https://truecarbon-api.render.com`)
3. Test these endpoints in your browser:
   - Health check: `https://truecarbon-api.render.com/health`
   - API docs: `https://truecarbon-api.render.com/api/v1/docs`

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "service": "True Carbon API"
}
```

## Step 7: Check Backend Logs

If there are errors:
1. Go to Web Service dashboard
2. Click **Logs** tab
3. Look for errors in the logs
4. Common issues:
   - `DATABASE_URL` format is incorrect → verify `postgresql+asyncpg://` prefix
   - `SECRET_KEY` missing → add it to environment variables
   - Migration errors → check database connection

## Step 8: Update CORS for Your Frontend

When your frontend is deployed:

1. Get your frontend URL (e.g., `https://yourdomain.com`)
2. Update `CORS_ORIGINS` environment variable:
   - `https://yourdomain.com`
   - `https://www.yourdomain.com`
   - Separate multiple values with commas (no spaces)
3. Restart the Web Service

## Troubleshooting

### Database connection fails
- ✅ Verify `postgresql+asyncpg://` prefix in DATABASE_URL
- ✅ Check password doesn't contain special characters (if it does, URL-encode it)
- ✅ Ensure database is running (check Postgres dashboard)

### Alembic migrations fail
- ✅ Check if database exists (should auto-create)
- ✅ Verify DATABASE_URL is correct
- ✅ Check logs for specific SQL errors

### Can't access API
- ✅ Wait 1-2 minutes after deployment
- ✅ Check Web Service is in "Live" state
- ✅ Verify health endpoint returns 200

### Frontend can't reach API
- ✅ Verify CORS_ORIGINS includes your frontend domain
- ✅ Use full URL with `https://` in frontend API calls
- ✅ Check browser console for CORS errors

## API Base URL for Frontend

Use this in your frontend code:
```javascript
const API_BASE_URL = "https://truecarbon-api.render.com/api/v1";
```

## Support

For Render-specific issues: https://render.com/docs
For TrueCarbon backend issues: Check `/backend` folder in repository

---

✅ Your backend is now live on Render!
