# 🧪 Testing Guide - Authentication Flow

## Prerequisites
- `.env` file updated with proper secret keys
- API container healthy: `docker-compose ps` shows `(healthy)` status
- Health endpoint responding: `curl http://localhost:8000/health`

## Test 1: User Registration

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "name": "Test User"
  }'
```

**Expected Response (201):**
```json
{
  "id": 1,
  "email": "test@example.com",
  "name": "Test User",
  "is_active": true,
  "created_at": "2024-12-25T03:00:00.000000"
}
```

## Test 2: User Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'
```

**Expected Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "name": "Test User",
    "is_active": true
  }
}
```

**Save the `access_token` for next tests!**

## Test 3: Get Current User (Protected Route)

```bash
# Replace YOUR_ACCESS_TOKEN with the token from login response
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response (200):**
```json
{
  "id": 1,
  "email": "test@example.com",
  "name": "Test User",
  "is_active": true,
  "created_at": "2024-12-25T03:00:00.000000"
}
```

## Test 4: Refresh Token

```bash
# Replace YOUR_REFRESH_TOKEN with the refresh_token from login
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

**Expected Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

## 🔴 Error Cases to Test

### Duplicate Email
```bash
# Try registering same email again
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "AnotherPassword123!",
    "name": "Another User"
  }'
```

**Expected: 400 Bad Request** - "Email already registered"

### Invalid Password
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "WrongPassword123!"
  }'
```

**Expected: 401 Unauthorized** - "Invalid credentials"

### Invalid/Expired Token
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer invalid_token_here"
```

**Expected: 401 Unauthorized** - "Could not validate credentials"

## ✅ Success Criteria

All tests passing means:
- ✅ User registration works
- ✅ Password hashing (bcrypt) works
- ✅ JWT token generation works
- ✅ JWT token validation works
- ✅ Protected routes work
- ✅ Refresh token flow works
- ✅ Error handling works

## 🚀 Next Steps After Tests Pass

We can proceed to **Stage 4-5: Chat Module Implementation**

This will add:
- Multi-provider LLM service (Groq/Bedrock/OpenAI)
- Conversation management
- Chat API endpoints
- Message streaming
- Token usage tracking

Estimated: ~10 files, 800-1000 lines of code, 30-45 minutes

---

**Quick Command Reference:**
```bash
# Check containers
docker-compose ps

# View logs
docker-compose logs api -f

# Restart API
docker-compose restart api

# Stop all
docker-compose down

# Start all
docker-compose up -d
```
