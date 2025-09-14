# Railway Deployment Guide

## Quick Setup Steps:

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Ready for Railway deployment"
   git push origin main
   ```

2. **Deploy on Railway:**
   - Go to https://railway.app
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Python and deploys

3. **Add Services:**
   - Click "Add Service" → "PostgreSQL"
   - Click "Add Service" → "Redis"

4. **Environment Variables:**
   ```env
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   REDIS_URL=${{Redis.REDIS_URL}}
   ENVIRONMENT=production
   ALLOWED_ORIGINS=https://yourdomain.com
   ```

5. **Custom Domain:**
   - Go to "Settings" → "Domains"
   - Add your custom domain
   - Railway provides free SSL

## Your API will be available at:
- https://your-app-name.railway.app
- https://yourdomain.com (after adding custom domain)

## API Endpoints:
- Documentation: https://yourdomain.com/docs
- Health Check: https://yourdomain.com/health
- WebSocket: wss://yourdomain.com/ws/{game_id}
