# 🎯 Quick Start: Deploy TrueCarbon in 5 Steps

## Step 1️⃣ Generate Secret Key (1 min)
```bash
openssl rand -hex 32
```
**Copy the output** - you'll need this in Step 4.

---

## Step 2️⃣ Create Database on Render (5 min)

1. Go to **https://dashboard.render.com/**
2. Click **New +** → **PostgreSQL**
3. Fill in:
   - Name: `truecarbon-postgres`
   - Database: `truecarbon`
   - User: `truecarbon_user`
   - Region: `us-east` (or your region)
4. Click **Create Database**
5. **Wait 2-3 minutes**, then copy the **External Database URL**

Your URL will look like:
```
postgresql://truecarbon_user:PASSWORD@dpg-xxxxxx.render.com:5432/truecarbon
```

---

## Step 3️⃣ Create Web Service on Render (5 min)

1. Go to **https://dashboard.render.com/**
2. Click **New +** → **Web Service**
3. Select **Deploy an existing Git repository**
4. Paste: `https://github.com/nakija-debug/TrueCarbon.git`
5. Click **Connect**
6. Fill in the form:
   - **Name:** `truecarbon-api`
   - **Environment:** Python 3
   - **Region:** `us-east` (same as database)
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Build Command:**
     ```
     pip install -r requirements.txt && alembic upgrade head
     ```
   - **Start Command:**
     ```
     gunicorn app.main:app --workers 3 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
     ```

---

## Step 4️⃣ Add Environment Variables (2 min)

Click **Environment** and add these 4 variables:

### Variable 1: DATABASE_URL
**Key:** `DATABASE_URL`
**Value:** (Copy from Step 2, but change `postgresql://` to `postgresql+asyncpg://`)

**Example:**
```
postgresql+asyncpg://truecarbon_user:PASSWORD@dpg-xxxxxx.render.com:5432/truecarbon
```

### Variable 2: SECRET_KEY
**Key:** `SECRET_KEY`
**Value:** (Paste from Step 1)

**Example:**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### Variable 3: ENVIRONMENT
**Key:** `ENVIRONMENT`
**Value:** `production`

### Variable 4: PYTHONUNBUFFERED
**Key:** `PYTHONUNBUFFERED`
**Value:** `1`

---

## Step 5️⃣ Deploy! (10 min)

Click **Create Web Service** and wait for deployment to complete.

**Status indicators:**
- 🟡 Building → Your code is installing dependencies
- 🟡 Deploying → Running migrations and starting app
- 🟢 Live → Your API is online!

---

## ✅ Test Your Deployment

Once deployed, copy your service URL (e.g., `https://truecarbon-api.render.com`)

### Test Health Endpoint
Visit in browser:
```
https://truecarbon-api.render.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "service": "True Carbon API"
}
```

### View API Documentation
Visit:
```
https://truecarbon-api.render.com/api/v1/docs
```

---

## 🆘 Troubleshooting

**🔴 Deployment failed?**
- Check the **Logs** tab for error messages
- Most common: Wrong DATABASE_URL format

**🔴 Database connection error?**
- Make sure URL starts with `postgresql+asyncpg://` (not `postgresql://`)
- Verify the password doesn't have special characters

**🔴 Service won't start?**
- Check if SECRET_KEY is set
- Verify ENVIRONMENT=production
- Look at logs for Python errors

---

## 📊 Your API is Now Live! 🎉

### Endpoints you can use:

```
Health Check:
GET https://your-service.render.com/health

API Documentation:
GET https://your-service.render.com/api/v1/docs

Swagger UI:
https://your-service.render.com/api/v1/docs

ReDoc:
https://your-service.render.com/api/v1/redoc
```

---

## 🔗 Use in Your Frontend

Update your frontend API base URL:

```javascript
const API_BASE_URL = "https://your-service-name.render.com/api/v1";
```

Example API call:
```javascript
fetch(`${API_BASE_URL}/auth/register`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com', password: 'secure' })
})
```

---

## 📞 Need Help?

- **Full Guide:** See [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md)
- **Checklist:** See [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
- **Render Docs:** https://render.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com

---

**That's it! Your backend is now live on Render! 🚀**
