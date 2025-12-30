#!/bin/bash
# ============================================
# APE EC2 Setup Script
# ============================================
# This script automates the EC2 server setup
# Run this after connecting via SSH
# ============================================

set -e  # Exit on error

echo "🚀 APE Production Setup - Starting..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Check if running as ubuntu user
if [ "$(whoami)" != "ubuntu" ]; then
    print_error "This script must be run as 'ubuntu' user"
    exit 1
fi

# Step 1: Update system
print_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_success "System updated"

# Step 2: Install Docker
print_info "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    sudo usermod -aG docker ubuntu
    print_success "Docker installed"
else
    print_success "Docker already installed"
fi

# Step 3: Install Docker Compose
print_info "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose installed"
else
    print_success "Docker Compose already installed"
fi

# Step 4: Install essential tools
print_info "Installing essential tools..."
sudo apt install -y git curl vim
print_success "Essential tools installed"

# Step 5: Clone repository
print_info "Cloning APE repository..."
if [ ! -d "$HOME/ai-ape-engine" ]; then
    cd ~
    git clone https://github.com/afif103/ai-ape-engine.git
    print_success "Repository cloned"
else
    print_success "Repository already exists"
fi

echo ""
echo "======================================"
echo "✅ Basic setup complete!"
echo "======================================"
echo ""
echo "⚠️  IMPORTANT NEXT STEPS:"
echo ""
echo "1. LOGOUT and LOGIN again for Docker group to take effect:"
echo "   exit"
echo "   ssh -i ~/.ssh/ape-ec2-key.pem ubuntu@<YOUR_ELASTIC_IP>"
echo ""
echo "2. Navigate to project:"
echo "   cd ~/ai-ape-engine"
echo ""
echo "3. Copy and configure environment:"
echo "   cp .env.production .env"
echo "   vim .env"
echo ""
echo "   Replace these values:"
echo "   - GROQ_API_KEY=<your-actual-key>"
echo "   - CORS_ORIGINS=https://ai-ape-engine-vercel.vercel.app,http://<YOUR_ELASTIC_IP>:8000"
echo ""
echo "4. Build and start services:"
echo "   docker-compose -f docker-compose.prod.yml build"
echo "   docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "5. Run database migrations:"
echo "   docker exec -it ape_backend_prod bash"
echo "   alembic upgrade head"
echo "   exit"
echo ""
echo "6. Test health endpoint:"
echo "   curl http://localhost:8000/health"
echo ""
echo "======================================"
