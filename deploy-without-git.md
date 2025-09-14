# Deploy to Railway Without Git

## Option 1: Railway CLI (Easiest)

1. **Install Railway CLI:**
   - Download from: https://docs.railway.app/develop/cli
   - Or install via npm: `npm install -g @railway/cli`

2. **Login and Deploy:**
   ```powershell
   railway login
   railway init
   railway up
   ```

## Option 2: GitHub Web Interface

1. **Create GitHub Account:**
   - Go to https://github.com
   - Sign up

2. **Create Repository:**
   - Click "New repository"
   - Name: `ticket-to-ride-backend`
   - Make it Public
   - Don't initialize with README

3. **Upload Files:**
   - Click "uploading an existing file"
   - Drag and drop these files:
     - main.py
     - models.py
     - game_logic.py
     - database.py
     - requirements.txt
     - Procfile
     - railway.json
     - test_api_comprehensive.py

4. **Commit:**
   - Add message: "Initial commit"
   - Click "Commit changes"

5. **Deploy on Railway:**
   - Go to https://railway.app
   - Sign up with GitHub
   - Deploy from your repository

## Option 3: Manual File Upload

1. **Create Railway Account:**
   - Go to https://railway.app
   - Sign up

2. **Create Empty Project:**
   - Click "New Project"
   - Select "Empty Project"

3. **Upload Files:**
   - Use Railway's file upload feature
   - Upload all your project files

4. **Configure:**
   - Add PostgreSQL service
   - Add Redis service
   - Set environment variables
