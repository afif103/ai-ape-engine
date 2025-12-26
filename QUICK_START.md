# APE - Quick Start Guide

## Current Implementation Status

✅ **COMPLETED** (Ready to test):
- Database models (all tables)
- Authentication system (register, login, JWT)
- Health check endpoint
- Docker environment
- Core utilities (security, logging, config)

⏳ **REMAINING** (for full MVP):
- LLM Service (Groq, Bedrock, OpenAI with fallback)
- Chat Module (conversations, messages)
- Research, Code, Data Extraction modules

---

## 🚀 Quick Start - Test Current Implementation

### Step 1: Start the application

```bash
# Make sure you're in the project directory
cd "D:\AI Projects\apev5"

# Start all services with Docker
docker-compose up --build
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- ChromaDB (port 8001)
- API (port 8000)

### Step 2: Create database tables

Open a new terminal and run:

```bash
# Generate migration
docker-compose exec api alembic revision --autogenerate -m "Initial schema"

# Apply migration
docker-compose exec api alembic upgrade head
```

### Step 3: Test the API

**Health Check**:
```bash
curl http://localhost:8000/health
```

**Register a user**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"Test123!\",\"name\":\"Test User\"}"
```

**Login**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"Test123!\"}"
```

**Get your profile**:
```bash
# Save the access_token from login response
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### Step 4: View API Documentation

Open your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📝 What's Working Now

| Feature | Status | Endpoints |
|---------|--------|-----------|
| Health Check | ✅ Ready | GET /health |
| User Registration | ✅ Ready | POST /api/v1/auth/register |
| User Login | ✅ Ready | POST /api/v1/auth/login |
| Get Profile | ✅ Ready | GET /api/v1/auth/me |
| AI Chat | ⏳ Pending | - |
| Code Assistant | ⏳ Pending | - |
| Research | ⏳ Pending | - |
| Data Extraction | ⏳ Pending | - |

---

## 🔧 Troubleshooting

### Issue: "Connection refused" to database

**Solution**: Wait a few seconds for PostgreSQL to fully start, then try again.

### Issue: "Module not found" errors

**Solution**: The API container has all dependencies. Make sure you're using docker-compose, not running locally.

### Issue: Alembic command not found

**Solution**: Make sure the API container is running:
```bash
docker-compose ps  # Check if 'api' service is up
```

### Issue: Port already in use

**Solution**: Stop other services using these ports:
- 8000 (API)
- 5432 (PostgreSQL)
- 6379 (Redis)

```bash
# On Windows
netstat -ano | findstr :8000
# Kill process if needed
taskkill /PID <PID> /F
```

---

## 📚 Next Development Steps

To continue developing APE and add chat functionality:

1. **Create LLM Service** (5 files)
   - Base provider interface
   - Groq, Bedrock, OpenAI providers
   - Multi-provider orchestrator

2. **Create Chat Module** (4 files)
   - Chat schemas
   - Conversation repository
   - Chat service
   - Chat routes

3. **Test end-to-end chat**

---

## 📂 Project Structure

```
apev5/
├── src/
│   ├── main.py              ✅ FastAPI app
│   ├── config.py            ✅ Settings
│   ├── dependencies.py      ✅ DI
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py    ✅ Health check
│   │   │   └── auth.py      ✅ Authentication
│   │   ├── schemas/
│   │   │   └── auth.py      ✅ Auth schemas
│   │   └── middleware/      ✅ Logging, rate limit
│   │
│   ├── services/
│   │   └── auth_service.py  ✅ Auth logic
│   │
│   ├── repositories/
│   │   └── user_repository.py ✅ User CRUD
│   │
│   ├── models/              ✅ All DB models
│   ├── core/                ✅ Utilities
│   └── db/                  ✅ Session, Redis
│
├── docs/                    ✅ Requirements, architecture
├── docker-compose.yml       ✅ Local environment
└── requirements.txt         ✅ Dependencies
```

---

## 🎯 Success Criteria

After testing, you should be able to:

- [x] Start the application with Docker
- [x] Create database tables
- [x] Register a new user
- [x] Login and receive JWT tokens
- [x] Access protected endpoints with the token
- [ ] Send chat messages (after Stage 4-5 implementation)

---

## Need Help?

Check the logs:
```bash
# View API logs
docker-compose logs -f api

# View database logs
docker-compose logs -f postgres

# View all logs
docker-compose logs -f
```

---

**Ready to proceed?** Try the Quick Start steps above and let me know if you encounter any issues!
