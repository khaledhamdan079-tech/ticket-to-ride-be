from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Union, Literal
from datetime import datetime, timezone
from enum import Enum
import json

# Enums matching Flutter app
class GamePhase(str, Enum):
    WAITING = "waiting"
    INITIAL_TICKETS = "initialTickets"
    PLAYING = "playing"
    FINISHED = "finished"

class RouteColor(str, Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    PINK = "pink"
    WHITE = "white"
    BLACK = "black"
    GRAY = "gray"
    WILD = "wild"

# Core Game Models matching Flutter app structure
class City(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    id: str
    name: str
    x: float
    y: float
    region: str

class TrainCard(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    id: str
    color: RouteColor
    isLocomotive: bool = False

class DestinationTicket(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    id: str
    from_city: City
    to_city: City
    points: int
    penalty: int

class Route(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    id: str
    from_city: City
    to_city: City
    length: int
    color: RouteColor
    points: int
    isDoubleRoute: bool = False
    doubleRouteId: Optional[str] = None

class Player(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    id: str
    name: str
    color: str  # Player's color for UI
    trainCars: int = 45
    hand: List[TrainCard] = []
    destinationTickets: List[DestinationTicket] = []
    claimedRoutes: List[Route] = []
    score: int = 0
    isActive: bool = False

class GameState(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    id: str
    name: str
    players: List[Player] = []
    currentPlayer: Optional[Player] = None
    phase: GamePhase = GamePhase.WAITING
    trainCardDeck: List[TrainCard] = []
    faceUpCards: List[TrainCard] = []
    destinationTicketDeck: List[DestinationTicket] = []
    availableRoutes: List[Route] = []
    allRoutes: List[Route] = []
    cities: List[City] = []
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    startedAt: Optional[datetime] = None
    finishedAt: Optional[datetime] = None
    gameSettings: dict = {}

# Request Models
class CreateGameRequest(BaseModel):
    name: str
    playerName: str

class JoinGameRequest(BaseModel):
    playerName: str

class StartGameRequest(BaseModel):
    playerId: str

class DrawCardsRequest(BaseModel):
    playerId: str
    cardIds: List[str]

class ClaimRouteRequest(BaseModel):
    playerId: str
    routeId: str
    cardIds: List[str]

class DrawTicketsRequest(BaseModel):
    playerId: str
    ticketIds: List[str]

class EndTurnRequest(BaseModel):
    playerId: str

# Response Models
class GameResponse(BaseModel):
    success: bool
    data: dict
    error: Optional[dict] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: dict

# WebSocket Event Models
class WebSocketEvent(BaseModel):
    type: str
    data: dict

class GameStateUpdateEvent(WebSocketEvent):
    type: Literal["gameStateUpdate"] = "gameStateUpdate"
    data: dict

class PlayerJoinedEvent(WebSocketEvent):
    type: Literal["playerJoined"] = "playerJoined"
    data: dict

class PlayerLeftEvent(WebSocketEvent):
    type: Literal["playerLeft"] = "playerLeft"
    data: dict

class TurnChangedEvent(WebSocketEvent):
    type: Literal["turnChanged"] = "turnChanged"
    data: dict

class RouteClaimedEvent(WebSocketEvent):
    type: Literal["routeClaimed"] = "routeClaimed"
    data: dict

class GameEndedEvent(WebSocketEvent):
    type: Literal["gameEnded"] = "gameEnded"
    data: dict
