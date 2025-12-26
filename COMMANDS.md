# 🔧 Quick Command Reference - APE Project

## Docker Commands

### Start All Services
```bash
cd "D:\AI Projects\apev5"
docker-compose up -d
```

### Stop All Services
```bash
docker-compose down
```

### Restart Specific Service
```bash
docker-compose restart api      # Restart API only
docker-compose restart postgres # Restart database
docker-compose restart redis    # Restart Redis
```

### View Container Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs api -f
docker-compose logs postgres -f

# Last N lines
docker-compose logs api --tail=50
```

### Rebuild API Container
```bash
docker-compose build api
docker-compose up -d api
```

### Clean Up Everything
```bash
# Stop and remove containers, networks
docker-compose down

# Also remove volumes (DATABASE WILL BE DELETED!)
docker-compose down -v

# Remove all unused Docker resources
docker system prune -a
```

---

## Database Commands

### Run Migrations
```bash
docker-compose exec api alembic upgrade head
```

### Check Current Migration
```bash
docker-compose exec api alembic current
```

### Create New Migration
```bash
docker-compose exec api alembic revision --autogenerate -m "description"
```

### Rollback Migration
```bash
docker-compose exec api alembic downgrade -1
```

### Connect to PostgreSQL
```bash
docker-compose exec postgres psql -U apeuser -d apedb
```

### PostgreSQL Quick Queries
```sql
-- List all tables
\dt

-- Describe users table
\d users

-- Count users
SELECT COUNT(*) FROM users;

-- See all users
SELECT id, email, name, created_at FROM users;

-- Exit
\q
```

### Connect to Redis CLI
```bash
docker-compose exec redis redis-cli
```

### Redis Quick Commands
```bash
# Test connection
PING

# List all keys
KEYS *

# Get value
GET key_name

# Delete key
DEL key_name

# Flush all data (BE CAREFUL!)
FLUSHALL

# Exit
exit
```

---

## API Testing Commands

### Health Check
```bash
curl http://localhost:8000/health
```

### Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "name": "Test User"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'
```

### Get Current User (Protected Route)
```bash
# Replace YOUR_TOKEN with actual access_token from login
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Refresh Token
```bash
# Replace YOUR_REFRESH_TOKEN with actual refresh_token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

### Logout
```bash
# Replace YOUR_REFRESH_TOKEN with actual refresh_token
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

---

## Development Commands

### Install Python Dependencies Locally
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run FastAPI Locally (Without Docker)
```bash
# Make sure .env file exists
# Make sure PostgreSQL, Redis, ChromaDB are running

uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Python Linting/Formatting
```bash
# Check code
ruff check .

# Format code
ruff format .

# Type checking
mypy src/
```

### Run Tests (When Implemented)
```bash
pytest
pytest -v
pytest --cov=src
```

---

## Troubleshooting Commands

### Check If Port is in Use
```bash
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Check Docker Resources
```bash
# Disk usage
docker system df

# List all containers
docker ps -a

# List all images
docker images

# List all volumes
docker volume ls
```

### Remove Specific Container/Image/Volume
```bash
# Stop container
docker stop ape_api

# Remove container
docker rm ape_api

# Remove image
docker rmi apev5-api

# Remove volume
docker volume rm apev5_postgres_data
```

### View Container Details
```bash
# Inspect container
docker inspect ape_api

# Check container health
docker inspect --format='{{.State.Health.Status}}' ape_api

# View container env vars
docker exec ape_api env
```

---

## Environment Variable Commands

### Generate New Secret Keys
```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(48))"

# PowerShell (Windows)
[Convert]::ToBase64String((1..48 | ForEach-Object { Get-Random -Maximum 256 }))
```

### View Environment Variables (in container)
```bash
docker-compose exec api env | grep -E "SECRET|DATABASE|REDIS|GROQ"
```

---

## Backup and Restore

### Backup Database
```bash
# Create backup
docker-compose exec postgres pg_dump -U apeuser apedb > backup_$(date +%Y%m%d).sql

# Or with Docker
docker exec ape_postgres pg_dump -U apeuser apedb > backup.sql
```

### Restore Database
```bash
# Restore from backup
docker exec -i ape_postgres psql -U apeuser apedb < backup.sql
```

### Backup Redis
```bash
# Create RDB snapshot
docker-compose exec redis redis-cli BGSAVE

# Copy snapshot
docker cp ape_redis:/data/dump.rdb ./redis_backup.rdb
```

---

## Quick Fixes

### API Container Won't Start
```bash
# Check logs
docker-compose logs api --tail=50

# Check config
docker-compose config

# Rebuild
docker-compose build api --no-cache
docker-compose up -d api
```

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres --tail=20

# Restart PostgreSQL
docker-compose restart postgres
```

### Redis Connection Error
```bash
# Check if Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli PING

# Restart Redis
docker-compose restart redis
```

### Port Already in Use
```bash
# Find process using port 8000 (Windows)
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
```

---

## Performance Monitoring

### Check Container Resource Usage
```bash
docker stats

# Or specific container
docker stats ape_api
```

### Check Database Size
```sql
-- Connect to PostgreSQL
docker-compose exec postgres psql -U apeuser -d apedb

-- Check database size
SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) 
FROM pg_database;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Check Redis Memory
```bash
docker-compose exec redis redis-cli INFO memory
```

---

## Useful Aliases (Optional)

Add to your shell profile (`.bashrc`, `.zshrc`, or PowerShell profile):

```bash
# Docker Compose shortcuts
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs -f'
alias dcp='docker-compose ps'

# APE specific
alias ape-start='cd "D:\AI Projects\apev5" && docker-compose up -d'
alias ape-stop='cd "D:\AI Projects\apev5" && docker-compose down'
alias ape-logs='cd "D:\AI Projects\apev5" && docker-compose logs -f api'
alias ape-restart='cd "D:\AI Projects\apev5" && docker-compose restart api'
alias ape-health='curl http://localhost:8000/health | jq'
```

---

## Emergency Commands

### Something is Completely Broken
```bash
# Stop everything
docker-compose down

# Remove all volumes (DELETES DATA!)
docker-compose down -v

# Clean Docker
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Reset Database Only
```bash
# Stop API
docker-compose stop api

# Remove database container and volume
docker-compose rm -f postgres
docker volume rm apev5_postgres_data

# Recreate
docker-compose up -d postgres

# Run migrations
docker-compose exec api alembic upgrade head

# Restart API
docker-compose start api
```

---

**Save this file for quick reference!** 📌

Common workflow:
1. `docker-compose ps` - Check status
2. `docker-compose logs api -f` - Watch logs
3. `curl http://localhost:8000/health` - Test API
4. `docker-compose restart api` - Restart after changes
