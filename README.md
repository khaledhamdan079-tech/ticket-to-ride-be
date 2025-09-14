# Ticket to Ride Backend API

A FastAPI backend for the Ticket to Ride multiplayer game, designed to work with the Flutter frontend application.

## 🚀 Live Application

**Production URL:** https://web-production-ec3e.up.railway.app

- **API Documentation:** https://web-production-ec3e.up.railway.app/docs
- **Health Check:** https://web-production-ec3e.up.railway.app/health
- **Database:** PostgreSQL (Railway)
- **Status:** ✅ Live and operational

## Features

- **Game Management**: Create, join, and manage multiplayer games
- **Real-time Updates**: WebSocket support for live game state updates
- **Game Logic**: Complete Ticket to Ride game rules implementation
- **Player Actions**: Draw cards, claim routes, draw destination tickets, end turns
- **Database Support**: SQLAlchemy with SQLite (easily configurable for PostgreSQL)
- **CORS Support**: Ready for web and mobile frontend integration

## API Endpoints

### Game Management
- `POST /api/games` - Create a new game
- `POST /api/games/{game_id}/join` - Join an existing game
- `GET /api/games/{game_id}` - Get game state
- `POST /api/games/{game_id}/start` - Start a game

### Game Actions
- `POST /api/games/{game_id}/draw-cards` - Draw train cards
- `POST /api/games/{game_id}/claim-route` - Claim a route
- `POST /api/games/{game_id}/draw-tickets` - Draw destination tickets
- `POST /api/games/{game_id}/end-turn` - End current turn

### WebSocket
- `WS /api/games/{game_id}/ws?player_id={player_id}` - Real-time game updates

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ticket-to-ride-backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Configuration

### Database
The application uses SQLite by default. To use PostgreSQL:

1. Update `DATABASE_URL` in `database.py`:
   ```python
   DATABASE_URL = "postgresql://username:password@localhost/ticket_to_ride"
   ```

2. Install PostgreSQL dependencies:
   ```bash
   pip install asyncpg psycopg2-binary
   ```

### Environment Variables
Create a `.env` file for configuration:
```env
DATABASE_URL=sqlite:///./ticket_to_ride.db
SECRET_KEY=your-secret-key-here
DEBUG=True
```

## API Usage Examples

### Create a Game
```bash
curl -X POST "http://localhost:8000/api/games" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Game",
    "playerName": "Player1"
  }'
```

### Join a Game
```bash
curl -X POST "http://localhost:8000/api/games/{game_id}/join" \
  -H "Content-Type: application/json" \
  -d '{
    "playerName": "Player2"
  }'
```

### Draw Train Cards
```bash
curl -X POST "http://localhost:8000/api/games/{game_id}/draw-cards" \
  -H "Content-Type: application/json" \
  -d '{
    "playerId": "player_id_here",
    "cardIds": ["card_id_1", "card_id_2"]
  }'
```

### Claim a Route
```bash
curl -X POST "http://localhost:8000/api/games/{game_id}/claim-route" \
  -H "Content-Type: application/json" \
  -d '{
    "playerId": "player_id_here",
    "routeId": "route_id_here",
    "cardIds": ["card_id_1", "card_id_2", "card_id_3"]
  }'
```

## WebSocket Events

The WebSocket connection provides real-time updates for:

- `gameStateUpdate` - Game state changes
- `playerJoined` - New player joined
- `playerLeft` - Player disconnected
- `turnChanged` - Turn moved to next player
- `routeClaimed` - Route was claimed
- `gameEnded` - Game finished

### WebSocket Connection Example
```javascript
const ws = new WebSocket('ws://localhost:8000/api/games/{game_id}/ws?player_id={player_id}');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
  
  switch(data.type) {
    case 'gameStateUpdate':
      // Update game state
      break;
    case 'playerJoined':
      // Handle player joined
      break;
    // ... other event types
  }
};
```

## Game Rules Implementation

The backend implements the complete Ticket to Ride game rules:

- **Player Setup**: 2-5 players, each starts with 45 train cars
- **Initial Cards**: Each player draws 4 train cards and 3 destination tickets
- **Turn Actions**: Draw cards, claim routes, or draw destination tickets
- **Route Claiming**: Must match route color and length with train cards
- **Scoring**: Route points + destination ticket bonuses/penalties
- **Game End**: When any player has 2 or fewer train cars left

## Data Models

The API uses Pydantic models that match the Flutter app's data structures:

- `GameState` - Complete game state
- `Player` - Player information and game data
- `Route` - Game board routes
- `City` - Game board cities
- `TrainCard` - Train cards
- `DestinationTicket` - Destination tickets

## Error Handling

The API provides comprehensive error handling with standard HTTP status codes:

- `400 Bad Request` - Invalid request data
- `404 Not Found` - Game or resource not found
- `409 Conflict` - Game full or invalid game state
- `422 Unprocessable Entity` - Valid request but invalid game state

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
isort .
```

### Database Migrations
```bash
alembic upgrade head
```

## Production Deployment

For production deployment:

1. **Use PostgreSQL** instead of SQLite
2. **Set up Redis** for session management and caching
3. **Configure CORS** properly for your domain
4. **Use environment variables** for sensitive configuration
5. **Set up SSL/TLS** for secure connections
6. **Use a reverse proxy** like Nginx
7. **Set up monitoring** and logging

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For support and questions, please open an issue in the repository.
