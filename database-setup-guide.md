# Database Setup Guide for Railway

## Step 1: Add PostgreSQL Database in Railway

1. **Go to your Railway project dashboard**
2. **Click "Add Service"** (or the "+" button)
3. **Select "Database" → "PostgreSQL"**
4. **Railway will automatically:**
   - Create a PostgreSQL database
   - Provide connection credentials
   - Set up environment variables

## Step 2: Environment Variables

Railway automatically sets these environment variables:

```env
DATABASE_URL=postgresql://postgres:password@host:port/database
PGHOST=host
PGPORT=port
PGDATABASE=database
PGUSER=postgres
PGPASSWORD=password
```

## Step 3: Update Your App

Replace `app.py` with `app-with-db.py` to enable database functionality.

## Step 4: Deploy

1. **Commit and push changes:**
   ```bash
   git add .
   git commit -m "Add database support"
   git push origin main
   ```

2. **Railway will automatically redeploy**

## Step 5: Test Database Endpoints

### Create a Game
```bash
curl -X POST "https://your-app.railway.app/api/games" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Test Game"}'
```

### Get All Games
```bash
curl "https://your-app.railway.app/api/games"
```

### Get Specific Game
```bash
curl "https://your-app.railway.app/api/games/{game_id}"
```

### Add Player to Game
```bash
curl -X POST "https://your-app.railway.app/api/players" \
  -H "Content-Type: application/json" \
  -d '{"name": "Player 1", "game_id": "{game_id}"}'
```

### Get Players in Game
```bash
curl "https://your-app.railway.app/api/players/{game_id}"
```

## Database Schema

### Games Table
- `id` (String, Primary Key)
- `name` (String)
- `status` (String, default: "waiting")
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Players Table
- `id` (String, Primary Key)
- `name` (String)
- `game_id` (String, Foreign Key)
- `created_at` (DateTime)

## Features

✅ **Automatic table creation**
✅ **Game management**
✅ **Player management**
✅ **Database relationships**
✅ **Error handling**
✅ **Pydantic validation**

## Next Steps

1. Add more game logic
2. Add WebSocket support
3. Add authentication
4. Add more game features
