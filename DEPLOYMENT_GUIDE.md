# 🚀 APE Production Deployment Guide

## EC2 Instance Setup

### Step 1: Launch EC2 Instance (AWS Console)

1. **Go to**: AWS Console → EC2 Dashboard → Launch Instance
2. **Configure**:
   - **Name**: `ape-production-backend`
   - **AMI**: Ubuntu Server 22.04 LTS (64-bit x86)
   - **Instance Type**: t3.micro (free tier eligible)
   - **Key Pair**: Create new → Name: `ape-ec2-key` → Download `.pem` file
   - **Network Settings**:
     - VPC: Use your existing VPC
     - Auto-assign Public IP: **Enable**
     - Security Group: **Create new** → Name: `ape-backend-sg`
   - **Storage**: 30 GB gp3 (free tier)
3. **Click**: Launch Instance

### Step 2: Configure Security Group

**Inbound Rules** (Edit security group after launch):
- SSH: TCP 22, Source: 0.0.0.0/0
- Custom TCP: TCP 8000, Source: 0.0.0.0/0

### Step 3: Allocate Elastic IP

1. EC2 Dashboard → Elastic IPs → **Allocate Elastic IP**
2. Select allocated IP → Actions → **Associate Elastic IP**
3. Select instance: `ape-production-backend` → Associate
4. **Note the Elastic IP**: You'll need this for Vercel config

### Step 4: Secure SSH Key

```bash
# Move key to secure location
mkdir -p ~/.ssh
mv ~/Downloads/ape-ec2-key.pem ~/.ssh/
chmod 400 ~/.ssh/ape-ec2-key.pem
```

---

## Server Setup Commands

### Connect to EC2

```bash
# Replace XX.XX.XX.XX with your Elastic IP
ssh -i ~/.ssh/ape-ec2-key.pem ubuntu@XX.XX.XX.XX
```

### Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install git and curl
sudo apt install -y git curl vim

# Logout and login for docker group to take effect
exit
```

### Reconnect and Clone Repository

```bash
# Reconnect to EC2
ssh -i ~/.ssh/ape-ec2-key.pem ubuntu@XX.XX.XX.XX

# Verify docker works
docker --version
docker-compose --version

# Clone repository
cd ~
git clone https://github.com/afif103/ai-ape-engine.git
cd ai-ape-engine
```

### Configure Environment Variables

```bash
# Copy production template
cp .env.production .env

# Edit .env file
vim .env

# IMPORTANT: Update these values in .env:
# 1. GROQ_API_KEY=<your-actual-groq-key>
# 2. CORS_ORIGINS=https://ai-ape-engine-vercel.vercel.app,http://XX.XX.XX.XX:8000
#    (Replace XX.XX.XX.XX with your Elastic IP)
```

**Quick vim instructions**:
- Press `i` to enter insert mode
- Navigate and edit the file
- Press `Esc` then type `:wq` and press Enter to save and quit

---

## Deploy Services

### Build and Start All Services

```bash
# Build Docker images (takes 5-10 minutes)
docker-compose -f docker-compose.prod.yml build

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check all containers are running
docker ps

# You should see 4 containers:
# - ape_backend_prod
# - ape_postgres_prod
# - ape_redis_prod
# - ape_chroma_prod
```

### Run Database Migrations

```bash
# Access backend container
docker exec -it ape_backend_prod bash

# Run migrations
alembic upgrade head

# Exit container
exit
```

### Verify Backend Health

```bash
# Test health endpoint locally
curl http://localhost:8000/health

# Expected: {"status":"healthy"}

# Test from external (replace XX.XX.XX.XX with your Elastic IP)
curl http://XX.XX.XX.XX:8000/health
```

---

## Connect Vercel Frontend

### Update Vercel Environment Variable

1. **Go to**: Vercel Dashboard → Project `ai-ape-engine-vercel`
2. **Settings** → **Environment Variables**
3. **Add/Update**:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `http://XX.XX.XX.XX:8000` (replace with your Elastic IP)
   - Environments: Production, Preview, Development
4. **Save**
5. **Deployments** → Latest deployment → **Redeploy**

---

## Testing Checklist

After deployment, test all features:

- [ ] Navigate to: https://ai-ape-engine-vercel.vercel.app/
- [ ] Register new account
- [ ] Login
- [ ] Test AI Chat
- [ ] Test Data Extraction
- [ ] Test Code Assistant
- [ ] Test Research
- [ ] Test Export
- [ ] Open browser console (F12) → Check for errors

---

## Useful Commands

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker logs ape_backend_prod -f
docker logs ape_postgres_prod -f
docker logs ape_redis_prod -f
```

### Restart Services

```bash
# Restart backend only
docker-compose -f docker-compose.prod.yml restart backend

# Restart all services
docker-compose -f docker-compose.prod.yml restart

# Stop all services
docker-compose -f docker-compose.prod.yml down

# Start all services
docker-compose -f docker-compose.prod.yml up -d
```

### Database Backup

```bash
# Create backup directory
mkdir -p ~/backups

# Backup database
docker exec -t ape_postgres_prod pg_dump -U postgres ape_db > ~/backups/backup_$(date +%Y%m%d).sql

# Restore database (if needed)
cat ~/backups/backup_20241230.sql | docker exec -i ape_postgres_prod psql -U postgres ape_db
```

### Monitor Resources

```bash
# Container stats
docker stats --no-stream

# Disk usage
df -h

# Docker disk usage
docker system df
```

---

## Troubleshooting

### Backend Container Exits

```bash
# Check logs
docker logs ape_backend_prod

# Common issues:
# - Database not ready: Wait 30 seconds and check docker ps
# - Missing env vars: Check .env file
# - Port conflict: sudo lsof -i :8000
```

### CORS Errors

```bash
# 1. Verify CORS_ORIGINS in .env includes Vercel domain
# 2. Restart backend
docker-compose -f docker-compose.prod.yml restart backend
```

### Out of Disk Space

```bash
# Clean Docker
docker system prune -a --volumes

# Check disk
df -h
```

---

## Cost Monitoring

### Weekly Checks (Every Monday)
1. AWS Console → Billing Dashboard
2. Check Free Tier Usage
3. Verify EC2 hours < 750/month
4. Verify data transfer < 15GB/month

### Expected Costs
- **Free Tier (6 months remaining)**: $0/month
- **After Free Tier**: ~$10-12/month
- **Vercel**: $0/month (Hobby plan)

---

## Production Info

**Frontend**: https://ai-ape-engine-vercel.vercel.app/
**Backend API**: http://XX.XX.XX.XX:8000
**SSH Access**: `ssh -i ~/.ssh/ape-ec2-key.pem ubuntu@XX.XX.XX.XX`

**Credentials**: All stored in `.env` file on EC2 (never commit to Git)

---

## Security Checklist

- [ ] SSH key secured (chmod 400)
- [ ] `.env` file not committed to Git
- [ ] Strong passwords generated for DB and Redis
- [ ] Security group allows only necessary ports
- [ ] Backend authentication required on protected endpoints
- [ ] CORS configured to allow only Vercel domain

---

**Deployment Status**: Ready to execute ✅
**Estimated Time**: 3-4 hours
**Cost**: $0/month (Free Tier)

🚀 **Let's deploy!**
