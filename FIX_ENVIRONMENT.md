# 🔧 Fix Required: Environment Variable Update

## Issue
The API container is failing with a **Pydantic validation error** because the `JWT_SECRET_KEY` in your `.env` file is too short. It needs at least 32 characters.

## ✅ What's Working
- ✅ PostgreSQL container running (healthy)
- ✅ Redis container running (healthy)
- ✅ ChromaDB container running
- ✅ API container built and running (but unhealthy due to validation error)

## 🔑 Secret Keys Generated

I've generated secure random keys for you. **Update these TWO lines in your `.env` file:**

```bash
SECRET_KEY=dZNkcPWnO4u0_aTKWXHzT7hKFqWJjVC5HXUulS69yJww7-21To3Tt1haheJHdouG
JWT_SECRET_KEY=SojvoUzqf1Y7bqFSF-VffsPg_VHMrrDcooduRTz1P3RKAUif8bm9uM7yVk7-QSKR
```

## 📝 Step-by-Step Fix

### 1. Update Your `.env` File

Open `D:\AI Projects\apev5\.env` and replace the following lines:

**OLD (too short):**
```bash
SECRET_KEY=change-this-secret-key
JWT_SECRET_KEY=change-this-jwt-secret-key
```

**NEW (secure and long enough):**
```bash
SECRET_KEY=dZNkcPWnO4u0_aTKWXHzT7hKFqWJjVC5HXUulS69yJww7-21To3Tt1haheJHdouG
JWT_SECRET_KEY=SojvoUzqf1Y7bqFSF-VffsPg_VHMrrDcooduRTz1P3RKAUif8bm9uM7yVk7-QSKR
```

### 2. Restart the API Container

After updating `.env`, run:
```bash
cd "D:\AI Projects\apev5"
docker-compose restart api
```

### 3. Check Container Health

Wait 10-15 seconds, then check:
```bash
docker-compose ps
```

You should see `STATUS` change from `Up X minutes (unhealthy)` to `Up X minutes (healthy)`

### 4. Test the API

Once healthy, test the health endpoint:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2024-12-25T03:00:00.000000"
}
```

## 🐛 If Still Not Working

View detailed logs:
```bash
docker-compose logs api --tail=50
```

## ✅ After This Works

Once the health check passes, we can test authentication and then proceed to **Stage 4-5: Building the Chat Module** with LLM integration!

---

**Complete .env Template**

I've also created `.env.fix` with all required variables. You can reference it or copy specific lines to your `.env` file.
