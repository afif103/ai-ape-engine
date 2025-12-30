# ⚡ APE Quick Start - AWS EC2 Deployment

## 🎯 **30-Second Overview**

Deploy APE to AWS EC2 in under 4 hours. Frontend already live on Vercel, just need to deploy backend.

---

## 📋 **Prerequisites Checklist**

- [x] AWS Account with free tier (6 months remaining)
- [x] Vercel account (frontend deployed)
- [x] Groq API key (in local .env file)
- [x] GitHub repos accessible
- [ ] 3-4 hours available
- [ ] Terminal/SSH access ready

---

## 🚀 **5-Step Deployment**

### **STEP 1: Launch EC2** (15 min)

**AWS Console → EC2 → Launch Instance**

- **Name**: `ape-production-backend`
- **AMI**: Ubuntu 22.04 LTS
- **Type**: t3.micro (free tier)
- **Key**: Create new → Download `ape-ec2-key.pem`
- **Security Group**: New → Allow SSH (22) + HTTP (8000)
- **Storage**: 30 GB gp3

**Allocate Elastic IP**:
- EC2 → Elastic IPs → Allocate → Associate with instance
- **Note the IP**: `___.___.___.___ ` (write it down!)

---

### **STEP 2: Connect & Setup** (45 min)

**Secure SSH key**:
```bash
mv ~/Downloads/ape-ec2-key.pem ~/.ssh/
chmod 400 ~/.ssh/ape-ec2-key.pem
```

**Connect to EC2**:
```bash
ssh -i ~/.ssh/ape-ec2-key.pem ubuntu@<YOUR_ELASTIC_IP>
```

**Run automated setup**:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install tools
sudo apt install -y git curl vim

# IMPORTANT: Logout and login for docker group
exit
```

**Reconnect**:
```bash
ssh -i ~/.ssh/ape-ec2-key.pem ubuntu@<YOUR_ELASTIC_IP>
```

---

### **STEP 3: Deploy Backend** (60 min)

**Clone repository**:
```bash
cd ~
git clone https://github.com/afif103/ai-ape-engine.git
cd ai-ape-engine
```

**Configure environment**:
```bash
# Copy production template
cp .env.production .env

# Edit with vim
vim .env
```

**In vim editor** (press `i` to edit):
1. Find line: `GROQ_API_KEY=<REPLACE_WITH_YOUR_GROQ_API_KEY>`
2. Replace with your actual Groq key from local .env
3. Find line: `CORS_ORIGINS=https://ai-ape-engine-vercel.vercel.app,http://XX.XX.XX.XX:8000`
4. Replace `XX.XX.XX.XX` with your Elastic IP
5. Press `Esc`, type `:wq`, press `Enter` (save and quit)

**Build and start services**:
```bash
# Build (takes 5-10 minutes)
docker-compose -f docker-compose.prod.yml build

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check all running
docker ps
# Should see: ape_backend_prod, ape_postgres_prod, ape_redis_prod, ape_chroma_prod
```

**Run database migrations**:
```bash
docker exec -it ape_backend_prod bash
alembic upgrade head
exit
```

**Test backend**:
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

curl http://<YOUR_ELASTIC_IP>:8000/health
# Expected: {"status":"healthy"}
```

---

### **STEP 4: Connect Vercel** (15 min)

**Update Vercel environment**:
1. Go to: https://vercel.com/dashboard
2. Select project: `ai-ape-engine-vercel`
3. Settings → Environment Variables
4. Add/Update:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `http://<YOUR_ELASTIC_IP>:8000`
   - **Environments**: Production, Preview, Development
5. Click **Save**
6. Deployments → Latest → **Redeploy**

---

### **STEP 5: Test Everything** (30 min)

**Open**: https://ai-ape-engine-vercel.vercel.app/

Test each feature:
- [ ] Register new account
- [ ] Login
- [ ] AI Chat (send message)
- [ ] Data Extraction (upload file)
- [ ] Code Assistant (generate code)
- [ ] Research (run query)
- [ ] Export (download file)

**Check browser console** (F12):
- [ ] No CORS errors
- [ ] No 401/403 errors
- [ ] No red errors

---

## ✅ **Success Checklist**

After deployment, verify:

- [ ] EC2 instance running
- [ ] Elastic IP attached
- [ ] 4 Docker containers running
- [ ] Health endpoint returns `{"status":"healthy"}`
- [ ] Vercel frontend accessible
- [ ] All features working
- [ ] No console errors
- [ ] AWS bill still $0.00

---

## 🆘 **Quick Troubleshooting**

### Backend container not running
```bash
docker logs ape_backend_prod
docker-compose -f docker-compose.prod.yml restart backend
```

### CORS errors in browser
```bash
# Verify .env has correct CORS_ORIGINS
cat .env | grep CORS

# Restart backend
docker-compose -f docker-compose.prod.yml restart backend
```

### Can't connect to backend from Vercel
1. Check security group allows port 8000 from 0.0.0.0/0
2. Check backend is running: `docker ps`
3. Test health: `curl http://<ELASTIC_IP>:8000/health`
4. Verify Vercel env var is correct

---

## 📊 **Useful Commands**

**View logs**:
```bash
docker logs ape_backend_prod -f
```

**Restart services**:
```bash
docker-compose -f docker-compose.prod.yml restart backend
```

**Stop everything**:
```bash
docker-compose -f docker-compose.prod.yml down
```

**Backup database**:
```bash
docker exec -t ape_postgres_prod pg_dump -U postgres ape_db > backup.sql
```

---

## 💰 **Cost Monitor**

**Weekly check** (Every Monday):
- AWS Console → Billing Dashboard
- Free Tier Usage → Verify EC2 < 750 hours
- Check total bill: Should be $0.00

---

## 🎓 **Full Documentation**

For detailed guides, see:
- **DEPLOYMENT_GUIDE.md** - Complete step-by-step
- **PRODUCTION.md** - Production status & operations
- **README.md** - Project overview

---

## 📝 **Important Notes**

1. **Security**: SSH key secured (chmod 400)
2. **Credentials**: Never commit .env to Git
3. **Backups**: Set up after successful deployment
4. **Monitoring**: Check AWS billing weekly
5. **Free Tier**: Valid for 6 more months

---

## 🚀 **Timeline**

| Step | Duration | Cumulative |
|------|----------|------------|
| 1. Launch EC2 | 15 min | 15 min |
| 2. Setup Server | 45 min | 1 hour |
| 3. Deploy Backend | 60 min | 2 hours |
| 4. Connect Vercel | 15 min | 2h 15m |
| 5. Test Everything | 30 min | 2h 45m |
| **TOTAL** | | **~3 hours** |

---

## 🎯 **Your Elastic IP**

Write it here for reference: `___.___.___.___`

---

**Ready? Let's go!** 🚀

Start with: [STEP 1: Launch EC2](#step-1-launch-ec2-15-min)
