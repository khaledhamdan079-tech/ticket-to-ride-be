# 🚀 Ticket to Ride Backend - Production Deployment Guide

This guide covers multiple deployment options for your Ticket to Ride backend API.

## 📋 Prerequisites

- Docker and Docker Compose installed
- Git (for version control)
- Domain name (for production)
- SSL certificates (for HTTPS)

## 🏗️ Deployment Options

### 1. 🐳 Docker Compose (Recommended for VPS/Cloud)

**Best for:** VPS, dedicated servers, cloud instances

```bash
# Clone your repository
git clone <your-repo-url>
cd ticket-to-ride-backend

# Copy environment template
cp env.example .env

# Edit configuration
nano .env

# Deploy
docker-compose up -d
```

**Access your API:**
- API: http://your-server-ip:8000
- Documentation: http://your-server-ip:8000/docs
- Health Check: http://your-server-ip:8000/health

### 2. ☁️ Cloud Platform Deployments

#### **Railway**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### **Render**
1. Connect your GitHub repository
2. Select "Web Service"
3. Use these settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Python 3.11

#### **Heroku**
```bash
# Install Heroku CLI
# Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev
git push heroku main
```

#### **DigitalOcean App Platform**
1. Connect GitHub repository
2. Configure:
   - **Source:** Your repository
   - **Type:** Web Service
   - **Build Command:** `pip install -r requirements.txt`
   - **Run Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. 🖥️ VPS Deployment (Ubuntu/Debian)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone and deploy
git clone <your-repo>
cd ticket-to-ride-backend
cp env.example .env
# Edit .env with your configuration
docker-compose up -d
```

### 4. 🏢 AWS/GCP/Azure

#### **AWS ECS with Fargate**
1. Create ECS cluster
2. Create task definition with your Docker image
3. Create service with load balancer
4. Configure auto-scaling

#### **Google Cloud Run**
```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT-ID/ticket-to-ride-backend

# Deploy
gcloud run deploy --image gcr.io/PROJECT-ID/ticket-to-ride-backend --platform managed
```

#### **Azure Container Instances**
```bash
# Create resource group
az group create --name ticket-to-ride-rg --location eastus

# Deploy container
az container create \
  --resource-group ticket-to-ride-rg \
  --name ticket-to-ride-backend \
  --image your-registry/ticket-to-ride-backend:latest \
  --ports 8000
```

## 🔧 Configuration

### Environment Variables

Create `.env` file with these variables:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
POSTGRES_PASSWORD=secure_password_123

# Redis
REDIS_URL=redis://host:6379

# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your_super_secret_key_here

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4
```

### SSL/HTTPS Setup

#### **Using Let's Encrypt with Nginx**
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### **Using Cloudflare**
1. Add your domain to Cloudflare
2. Update nameservers
3. Enable SSL/TLS encryption mode: "Full (strict)"
4. Enable "Always Use HTTPS"

## 📊 Monitoring & Logging

### **Health Checks**
- Endpoint: `/health`
- Returns: `{"status": "healthy", "timestamp": "..."}`

### **Logging**
```bash
# View logs
docker-compose logs -f app

# View specific service logs
docker-compose logs -f postgres
docker-compose logs -f redis
```

### **Monitoring Tools**
- **Prometheus + Grafana** for metrics
- **ELK Stack** for log aggregation
- **Uptime Robot** for uptime monitoring

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit `.env` files
2. **Database**: Use strong passwords and restrict access
3. **Firewall**: Only open necessary ports (80, 443, 22)
4. **Updates**: Keep system and dependencies updated
5. **Backups**: Regular database backups
6. **Rate Limiting**: Implement API rate limiting
7. **CORS**: Configure allowed origins properly

## 🚀 Quick Deploy Commands

```bash
# Local development
./deploy.sh  # Select option 1

# Production deployment
./deploy.sh  # Select option 2

# Build image only
./deploy.sh  # Select option 3

# Run tests
./deploy.sh  # Select option 4
```

## 🆘 Troubleshooting

### **Common Issues**

1. **Port already in use**
   ```bash
   sudo lsof -i :8000
   sudo kill -9 <PID>
   ```

2. **Database connection failed**
   - Check DATABASE_URL format
   - Verify database is running
   - Check firewall rules

3. **Redis connection failed**
   - Verify REDIS_URL
   - Check Redis service status

4. **CORS errors**
   - Update ALLOWED_ORIGINS
   - Check frontend URL

### **Useful Commands**

```bash
# Check container status
docker-compose ps

# Restart services
docker-compose restart

# View resource usage
docker stats

# Clean up
docker system prune -a
```

## 📞 Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f app`
2. Verify environment variables
3. Test endpoints: `curl http://localhost:8000/health`
4. Check database connectivity

---

**🎮 Your Ticket to Ride backend is now ready for production!**
