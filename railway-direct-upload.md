# Deploy to Railway Without Git

## Method 1: Railway CLI (Recommended)

1. **Install Railway CLI:**
   ```powershell
   # Install via npm (if you have Node.js)
   npm install -g @railway/cli
   
   # Or download from: https://docs.railway.app/develop/cli
   ```

2. **Login to Railway:**
   ```powershell
   railway login
   ```

3. **Deploy directly:**
   ```powershell
   railway init
   railway up
   ```

## Method 2: Manual Upload

1. **Create Railway Account:**
   - Go to https://railway.app
   - Sign up with email

2. **Create New Project:**
   - Click "New Project"
   - Select "Empty Project"

3. **Upload Files:**
   - Use Railway's file upload feature
   - Upload all your project files

4. **Configure Environment:**
   - Add PostgreSQL service
   - Add Redis service
   - Set environment variables

## Method 3: Use GitHub Web Interface

1. **Create GitHub Account:**
   - Go to https://github.com
   - Sign up

2. **Create New Repository:**
   - Click "New repository"
   - Name it "ticket-to-ride-backend"

3. **Upload Files via Web:**
   - Click "uploading an existing file"
   - Drag and drop all your files
   - Commit changes

4. **Deploy on Railway:**
   - Connect Railway to your GitHub repo
   - Auto-deploy
