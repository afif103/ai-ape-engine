# 🚀 APE Production Deployment

## Current Production Status

**Status**: Ready for deployment ✅  
**Last Updated**: December 30, 2024  
**Architecture**: Vercel (Frontend) + AWS EC2 (Backend)

---

## Production URLs

- **Frontend**: https://ai-ape-engine-vercel.vercel.app/
- **Backend API**: `http://<ELASTIC_IP>:8000` (to be configured)
- **API Documentation**: `http://<ELASTIC_IP>:8000/docs`
- **Health Check**: `http://<ELASTIC_IP>:8000/health`

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              PRODUCTION ARCHITECTURE                 │
├─────────────────────────────────────────────────────┤
│                                                      │
│  FRONTEND (Vercel - Free)                           │
│  └─ https://ai-ape-engine-vercel.vercel.app/       │
│                                                      │
│  BACKEND (AWS EC2 t3.micro - Free Tier)            │
│  ├─ FastAPI Application (Port 8000)                 │
│  ├─ PostgreSQL 15 (Docker)                          │
│  ├─ Redis 7 (Docker)                                │
│  └─ ChromaDB (Docker)                               │
│                                                      │
│  AI PROVIDER                                         │
│  └─ Groq API (llama-3.1-8b-instant - Free)         │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## Deployment Files

### Production Configuration Files

1. **docker-compose.prod.yml** - Production Docker Compose stack
2. **.env.production** - Environment variables template
3. **DEPLOYMENT_GUIDE.md** - Complete deployment instructions
4. **setup-ec2.sh** - Automated EC2 setup script

### Key Features

- ✅ Multi-stage Docker builds (optimized image size)
- ✅ Health checks for all services
- ✅ Auto-restart policies
- ✅ Network isolation
- ✅ Volume persistence
- ✅ Non-root container users
- ✅ Security headers middleware
- ✅ Dynamic CORS configuration

---

## Security Configuration

### Generated Credentials

**PostgreSQL Database**:
- User: `postgres`
- Password: `PgSQL#2024$aZx9mK!vL8qR`
- Database: `ape_db`

**Redis Cache**:
- Password: `Redis#2024$bNx7mJ!tQ6pW`

**FastAPI Secret Keys**:
- Secret Key: `sk_APE_7nM4$pL9@kR2#wT5&xY8!qV3`
- JWT Secret: `jwt_APE_9xM2$tL5@pK8#wR4&nY7!vQ1`

⚠️ **IMPORTANT**: These are production credentials. Never commit `.env` file to Git.

### CORS Configuration

Production CORS origins (configured via environment):
- `https://ai-ape-engine-vercel.vercel.app`
- `http://<ELASTIC_IP>:8000`

---

## Deployment Checklist

### Pre-Deployment

- [x] Production files created
- [x] CORS updated to use environment variables
- [x] Docker Compose configuration ready
- [x] Deployment guide written
- [x] Security credentials generated
- [x] Changes committed and pushed to GitHub

### AWS EC2 Setup

- [ ] Launch t3.micro instance (Ubuntu 22.04)
- [ ] Configure security group (SSH 22, HTTP 8000)
- [ ] Allocate and attach Elastic IP
- [ ] Download SSH key (.pem file)
- [ ] Connect via SSH

### Server Configuration

- [ ] Run setup-ec2.sh script
- [ ] Install Docker and Docker Compose
- [ ] Clone repository
- [ ] Configure .env file (Groq API key, Elastic IP)
- [ ] Build Docker images
- [ ] Start services
- [ ] Run database migrations
- [ ] Verify health endpoint

### Frontend Connection

- [ ] Update Vercel environment variable (NEXT_PUBLIC_API_URL)
- [ ] Redeploy Vercel frontend
- [ ] Test frontend → backend connection

### Testing

- [ ] Registration works
- [ ] Login works
- [ ] AI Chat works
- [ ] Data Extraction works
- [ ] Code Assistant works
- [ ] Research works
- [ ] Export works
- [ ] No CORS errors in console

### Monitoring

- [ ] Set up AWS cost monitoring
- [ ] Create database backup script
- [ ] Document production credentials
- [ ] Test disaster recovery

---

## Cost Breakdown

### Current Costs (Free Tier)

| Service | Type | Monthly Cost | Notes |
|---------|------|--------------|-------|
| EC2 t3.micro | Compute | $0 | Free Tier: 750 hours/month |
| EBS 30GB gp3 | Storage | $0 | Free Tier: 30GB included |
| Elastic IP | Network | $0 | Free while attached |
| Data Transfer | Network | $0 | Free Tier: 15GB outbound |
| Vercel | Frontend | $0 | Hobby plan |
| Groq API | AI | $0 | Free tier |
| **TOTAL** | | **$0/month** | For next 6 months |

### Post-Free Tier Costs (After 6 months)

| Service | Type | Monthly Cost |
|---------|------|--------------|
| EC2 t3.micro | Compute | ~$7.50 |
| EBS 30GB gp3 | Storage | ~$2.40 |
| Data Transfer | Network | ~$1.00 |
| **TOTAL** | | **~$10.90/month** |

---

## Useful Commands

### SSH Connection

```bash
ssh -i ~/.ssh/ape-ec2-key.pem ubuntu@<ELASTIC_IP>
```

### Service Management

```bash
# Navigate to project
cd ~/ai-ape-engine

# View all containers
docker ps

# View logs
docker logs ape_backend_prod -f
docker logs ape_postgres_prod -f

# Restart services
docker-compose -f docker-compose.prod.yml restart backend
docker-compose -f docker-compose.prod.yml restart

# Stop all services
docker-compose -f docker-compose.prod.yml down

# Start all services
docker-compose -f docker-compose.prod.yml up -d
```

### Database Operations

```bash
# Backup database
docker exec -t ape_postgres_prod pg_dump -U postgres ape_db > backup_$(date +%Y%m%d).sql

# Restore database
cat backup_20241230.sql | docker exec -i ape_postgres_prod psql -U postgres ape_db

# Access PostgreSQL shell
docker exec -it ape_postgres_prod psql -U postgres -d ape_db
```

### Monitoring

```bash
# Container stats
docker stats --no-stream

# Disk usage
df -h
docker system df

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## Troubleshooting

### Backend Not Responding

```bash
# Check logs
docker logs ape_backend_prod --tail 100

# Check if container is running
docker ps | grep ape_backend

# Restart backend
docker-compose -f docker-compose.prod.yml restart backend
```

### Database Connection Issues

```bash
# Check PostgreSQL logs
docker logs ape_postgres_prod

# Check if PostgreSQL is running
docker exec -it ape_postgres_prod pg_isready -U postgres

# Restart database
docker-compose -f docker-compose.prod.yml restart db
```

### CORS Errors

1. Verify `.env` file has correct CORS_ORIGINS
2. Restart backend: `docker-compose -f docker-compose.prod.yml restart backend`
3. Clear browser cache
4. Check browser console for exact error

### Out of Disk Space

```bash
# Clean Docker system
docker system prune -a --volumes

# Check disk usage
df -h
```

---

## Backup Strategy

### Automated Daily Backups

Create cron job for daily database backups:

```bash
# Create backup script
cat > ~/backup-ape.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/backups
DATE=$(date +%Y%m%d)
docker exec -t ape_postgres_prod pg_dump -U postgres ape_db > $BACKUP_DIR/ape_db_$DATE.sql
# Keep only last 7 days
find $BACKUP_DIR -name "ape_db_*.sql" -mtime +7 -delete
EOF

chmod +x ~/backup-ape.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * ~/backup-ape.sh") | crontab -
```

---

## Monitoring & Alerts

### Weekly Manual Checks

Every Monday, verify:
1. AWS Billing Dashboard → Free Tier usage
2. EC2 instance running hours (should be ~168/week)
3. Data transfer (should be < 2GB/week)
4. No unexpected charges

### Health Monitoring

```bash
# Check backend health
curl http://localhost:8000/health

# Check all services
docker ps
docker stats --no-stream
```

---

## Update Procedure

### Update Backend Code

```bash
# SSH into EC2
ssh -i ~/.ssh/ape-ec2-key.pem ubuntu@<ELASTIC_IP>

# Navigate to project
cd ~/ai-ape-engine

# Pull latest changes
git pull origin master

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build backend
docker-compose -f docker-compose.prod.yml up -d backend

# Run migrations if needed
docker exec -it ape_backend_prod bash
alembic upgrade head
exit
```

### Update Environment Variables

```bash
# Edit .env file
vim .env

# Restart backend
docker-compose -f docker-compose.prod.yml restart backend
```

---

## Disaster Recovery

### Complete System Failure

1. **Backup exists**: Restore from daily backup
2. **No backup**: Launch new EC2, follow deployment guide
3. **Data recovery**: User data in PostgreSQL volume (persists)

### Rollback Procedure

```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Checkout previous version
git checkout <previous-commit>

# Rebuild and start
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

---

## Support & Contact

**Repository**: https://github.com/afif103/ai-ape-engine  
**Frontend Repo**: https://github.com/afif103/ai-ape-engine-vercel  
**Documentation**: See DEPLOYMENT_GUIDE.md

---

## Next Steps After Deployment

1. ✅ Test all features thoroughly
2. ✅ Monitor costs for first week
3. ✅ Set up automated backups
4. ✅ Document any issues encountered
5. ✅ Update portfolio with live demo link
6. ⏳ Consider adding custom domain (optional)
7. ⏳ Consider AWS Bedrock upgrade for production AI (optional)
8. ⏳ Consider adding monitoring tools (CloudWatch, etc.)

---

**Status**: Ready for deployment  
**Next Action**: Follow DEPLOYMENT_GUIDE.md step-by-step  
**Estimated Time**: 3-4 hours  
**Cost**: $0/month for 6 months

🚀 **Let's deploy!**
