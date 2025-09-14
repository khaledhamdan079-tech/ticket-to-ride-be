# Upload to GitHub via Web Interface

## Step-by-Step Guide:

### 1. Create GitHub Account
- Go to https://github.com
- Sign up for free account

### 2. Create New Repository
- Click "New repository" (green button)
- Repository name: `ticket-to-ride-backend`
- Make it Public
- Click "Create repository"

### 3. Upload Files via Web
- Click "uploading an existing file"
- Drag and drop these files from your project:
  ```
  main.py
  models.py
  game_logic.py
  database.py
  requirements.txt
  Procfile
  railway.json
  test_api_comprehensive.py
  ```

### 4. Commit Files
- Add commit message: "Initial commit - Ticket to Ride Backend"
- Click "Commit changes"

### 5. Deploy on Railway
- Go to https://railway.app
- Sign up with GitHub
- Click "New Project" → "Deploy from GitHub repo"
- Select your `ticket-to-ride-backend` repository
- Railway will auto-deploy your app

### 6. Add Services
- Click "Add Service" → "PostgreSQL"
- Click "Add Service" → "Redis"

### 7. Configure Environment Variables
```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
ENVIRONMENT=production
ALLOWED_ORIGINS=https://yourdomain.com
```

### 8. Add Custom Domain
- Go to "Settings" → "Domains"
- Add your custom domain
- Railway provides free SSL

## Your API will be live at:
- https://your-app-name.railway.app
- https://yourdomain.com (after adding custom domain)
