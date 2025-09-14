from fastapi import WebSocket
from typing import Dict, List
import json
import asyncio

class WebSocketManager:
    def __init__(self):
        # Dictionary to store active connections by game_id
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Dictionary to store player connections by game_id and player_id
        self.player_connections: Dict[str, Dict[str, WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, game_id: str, player_id: str):
        """Accept a WebSocket connection and add it to the game's connections."""
        await websocket.accept()
        
        # Add to game connections
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)
        
        # Add to player connections
        if game_id not in self.player_connections:
            self.player_connections[game_id] = {}
        self.player_connections[game_id][player_id] = websocket
        
        print(f"Player {player_id} connected to game {game_id}")
    
    def disconnect(self, game_id: str, player_id: str):
        """Remove a WebSocket connection from the game's connections."""
        # Remove from player connections
        if game_id in self.player_connections and player_id in self.player_connections[game_id]:
            websocket = self.player_connections[game_id][player_id]
            del self.player_connections[game_id][player_id]
            
            # Remove from game connections
            if game_id in self.active_connections and websocket in self.active_connections[game_id]:
                self.active_connections[game_id].remove(websocket)
            
            # Clean up empty game entries
            if not self.player_connections[game_id]:
                del self.player_connections[game_id]
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]
            
            print(f"Player {player_id} disconnected from game {game_id}")
    
    async def send_personal_message(self, message: dict, game_id: str, player_id: str):
        """Send a message to a specific player in a game."""
        if game_id in self.player_connections and player_id in self.player_connections[game_id]:
            websocket = self.player_connections[game_id][player_id]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                print(f"Error sending message to player {player_id}: {e}")
                # Remove the connection if it's broken
                self.disconnect(game_id, player_id)
    
    async def broadcast_to_game(self, game_id: str, message: dict):
        """Broadcast a message to all players in a game."""
        if game_id in self.active_connections:
            # Create a list of tasks for concurrent sending
            tasks = []
            broken_connections = []
            
            for websocket in self.active_connections[game_id]:
                try:
                    task = websocket.send_text(json.dumps(message))
                    tasks.append(task)
                except Exception as e:
                    print(f"Error preparing message for game {game_id}: {e}")
                    broken_connections.append(websocket)
            
            # Remove broken connections
            for websocket in broken_connections:
                if websocket in self.active_connections[game_id]:
                    self.active_connections[game_id].remove(websocket)
            
            # Send all messages concurrently
            if tasks:
                try:
                    await asyncio.gather(*tasks, return_exceptions=True)
                except Exception as e:
                    print(f"Error broadcasting to game {game_id}: {e}")
    
    async def broadcast_to_all_players_except(self, game_id: str, message: dict, exclude_player_id: str):
        """Broadcast a message to all players in a game except one."""
        if game_id in self.player_connections:
            tasks = []
            broken_connections = []
            
            for player_id, websocket in self.player_connections[game_id].items():
                if player_id != exclude_player_id:
                    try:
                        task = websocket.send_text(json.dumps(message))
                        tasks.append(task)
                    except Exception as e:
                        print(f"Error preparing message for player {player_id}: {e}")
                        broken_connections.append(player_id)
            
            # Remove broken connections
            for player_id in broken_connections:
                self.disconnect(game_id, player_id)
            
            # Send all messages concurrently
            if tasks:
                try:
                    await asyncio.gather(*tasks, return_exceptions=True)
                except Exception as e:
                    print(f"Error broadcasting to game {game_id} (excluding {exclude_player_id}): {e}")
    
    def get_connected_players(self, game_id: str) -> List[str]:
        """Get list of connected player IDs for a game."""
        if game_id in self.player_connections:
            return list(self.player_connections[game_id].keys())
        return []
    
    def is_player_connected(self, game_id: str, player_id: str) -> bool:
        """Check if a specific player is connected to a game."""
        return (game_id in self.player_connections and 
                player_id in self.player_connections[game_id])
    
    def get_connection_count(self, game_id: str) -> int:
        """Get the number of connected players in a game."""
        if game_id in self.active_connections:
            return len(self.active_connections[game_id])
        return 0
    
    async def send_game_state_update(self, game_id: str, game_state: dict):
        """Send a game state update to all players in a game."""
        message = {
            "type": "gameStateUpdate",
            "data": {"game": game_state}
        }
        await self.broadcast_to_game(game_id, message)
    
    async def send_player_joined(self, game_id: str, player: dict, game_state: dict):
        """Send a player joined event to all players in a game."""
        message = {
            "type": "playerJoined",
            "data": {
                "player": player,
                "game": game_state
            }
        }
        await self.broadcast_to_game(game_id, message)
    
    async def send_player_left(self, game_id: str, player_id: str, game_state: dict):
        """Send a player left event to all players in a game."""
        message = {
            "type": "playerLeft",
            "data": {
                "playerId": player_id,
                "game": game_state
            }
        }
        await self.broadcast_to_game(game_id, message)
    
    async def send_turn_changed(self, game_id: str, current_player: dict, game_state: dict):
        """Send a turn changed event to all players in a game."""
        message = {
            "type": "turnChanged",
            "data": {
                "currentPlayer": current_player,
                "game": game_state
            }
        }
        await self.broadcast_to_game(game_id, message)
    
    async def send_route_claimed(self, game_id: str, route: dict, player: dict, game_state: dict):
        """Send a route claimed event to all players in a game."""
        message = {
            "type": "routeClaimed",
            "data": {
                "route": route,
                "player": player,
                "game": game_state
            }
        }
        await self.broadcast_to_game(game_id, message)
    
    async def send_game_ended(self, game_id: str, game_state: dict, winner: dict, scores: List[dict]):
        """Send a game ended event to all players in a game."""
        message = {
            "type": "gameEnded",
            "data": {
                "game": game_state,
                "winner": winner,
                "scores": scores
            }
        }
        await self.broadcast_to_game(game_id, message)
