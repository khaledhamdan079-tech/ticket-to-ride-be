from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from typing import Dict, List
import json
import uuid
from datetime import datetime, timezone

from models import (
    GameState, Player, Route, City, TrainCard, DestinationTicket,
    CreateGameRequest, JoinGameRequest, StartGameRequest,
    DrawCardsRequest, ClaimRouteRequest, DrawTicketsRequest, EndTurnRequest,
    GameResponse, ErrorResponse
)
from database import init_db, get_db
from game_logic import GameManager
from websocket_manager import WebSocketManager

# Initialize WebSocket manager
websocket_manager = WebSocketManager()

# Initialize game manager
game_manager = GameManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Ticket to Ride API",
    description="Backend API for Ticket to Ride multiplayer game",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Ticket to Ride API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}

# Game Management Endpoints

@app.post("/api/games", response_model=GameResponse)
async def create_game(request: CreateGameRequest):
    """Create a new game with the specified name and add the creator as the first player."""
    try:
        game_id = str(uuid.uuid4())
        player_id = str(uuid.uuid4())
        
        game = await game_manager.create_game(
            game_id=game_id,
            name=request.name,
            player_name=request.playerName,
            player_id=player_id
        )
        
        return GameResponse(
            success=True,
            data={
                "gameId": game_id,
                "playerId": player_id,
                "game": game.dict()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/games/{game_id}/join", response_model=GameResponse)
async def join_game(game_id: str, request: JoinGameRequest):
    """Add a new player to an existing game."""
    try:
        player_id = str(uuid.uuid4())
        game = await game_manager.join_game(
            game_id=game_id,
            player_name=request.playerName,
            player_id=player_id
        )
        
        # Notify all players via WebSocket
        await websocket_manager.broadcast_to_game(
            game_id, 
            {
                "type": "playerJoined",
                "data": {
                    "player": game.players[-1].dict(),  # The newly joined player
                    "game": game.dict()
                }
            }
        )
        
        return GameResponse(
            success=True,
            data={
                "playerId": player_id,
                "game": game.dict()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/games/{game_id}", response_model=GameResponse)
async def get_game_state(game_id: str, player_id: str = None):
    """Retrieve the current state of a game."""
    try:
        game = await game_manager.get_game(game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        
        return GameResponse(
            success=True,
            data={"game": game.dict()}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/games/{game_id}/start", response_model=GameResponse)
async def start_game(game_id: str, request: StartGameRequest):
    """Start a game that has enough players."""
    try:
        game = await game_manager.start_game(game_id, request.playerId)
        
        # Notify all players via WebSocket
        await websocket_manager.broadcast_to_game(
            game_id,
            {
                "type": "gameStateUpdate",
                "data": {"game": game.dict()}
            }
        )
        
        return GameResponse(
            success=True,
            data={"game": game.dict()}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Game Action Endpoints

@app.post("/api/games/{game_id}/draw-cards", response_model=GameResponse)
async def draw_train_cards(game_id: str, request: DrawCardsRequest):
    """Allow a player to draw train cards from face-up cards or the deck."""
    try:
        game = await game_manager.draw_train_cards(
            game_id=game_id,
            player_id=request.playerId,
            card_ids=request.cardIds
        )
        
        # Notify all players via WebSocket
        await websocket_manager.broadcast_to_game(
            game_id,
            {
                "type": "gameStateUpdate",
                "data": {"game": game.dict()}
            }
        )
        
        return GameResponse(
            success=True,
            data={"game": game.dict()}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/games/{game_id}/claim-route", response_model=GameResponse)
async def claim_route(game_id: str, request: ClaimRouteRequest):
    """Allow a player to claim a route using train cards."""
    try:
        game = await game_manager.claim_route(
            game_id=game_id,
            player_id=request.playerId,
            route_id=request.routeId,
            card_ids=request.cardIds
        )
        
        # Find the claimed route and player for WebSocket notification
        claimed_route = next((r for r in game.allRoutes if r.id == request.routeId), None)
        player = next((p for p in game.players if p.id == request.playerId), None)
        
        # Notify all players via WebSocket
        await websocket_manager.broadcast_to_game(
            game_id,
            {
                "type": "routeClaimed",
                "data": {
                    "route": claimed_route.dict() if claimed_route else None,
                    "player": player.dict() if player else None,
                    "game": game.dict()
                }
            }
        )
        
        return GameResponse(
            success=True,
            data={"game": game.dict()}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/games/{game_id}/draw-tickets", response_model=GameResponse)
async def draw_destination_tickets(game_id: str, request: DrawTicketsRequest):
    """Allow a player to draw destination tickets."""
    try:
        game = await game_manager.draw_destination_tickets(
            game_id=game_id,
            player_id=request.playerId,
            ticket_ids=request.ticketIds
        )
        
        # Notify all players via WebSocket
        await websocket_manager.broadcast_to_game(
            game_id,
            {
                "type": "gameStateUpdate",
                "data": {"game": game.dict()}
            }
        )
        
        return GameResponse(
            success=True,
            data={"game": game.dict()}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/games/{game_id}/end-turn", response_model=GameResponse)
async def end_turn(game_id: str, request: EndTurnRequest):
    """End the current player's turn and move to the next player."""
    try:
        game = await game_manager.end_turn(game_id, request.playerId)
        
        # Notify all players via WebSocket
        await websocket_manager.broadcast_to_game(
            game_id,
            {
                "type": "turnChanged",
                "data": {
                    "currentPlayer": game.currentPlayer.dict() if game.currentPlayer else None,
                    "game": game.dict()
                }
            }
        )
        
        return GameResponse(
            success=True,
            data={"game": game.dict()}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# WebSocket endpoint
@app.websocket("/api/games/{game_id}/ws")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    """WebSocket endpoint for real-time game updates."""
    await websocket_manager.connect(websocket, game_id, player_id)
    try:
        while True:
            # Keep the connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Handle any incoming messages from the client if needed
            message = json.loads(data)
            # Process message if needed
    except WebSocketDisconnect:
        websocket_manager.disconnect(game_id, player_id)
        # Notify other players that this player left
        game = await game_manager.get_game(game_id)
        await websocket_manager.broadcast_to_game(
            game_id,
            {
                "type": "playerLeft",
                "data": {
                    "playerId": player_id,
                    "game": game.dict() if game else None
                }
            }
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
