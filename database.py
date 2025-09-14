from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import json
import uuid

# Database configuration
DATABASE_URL = "sqlite:///./ticket_to_ride.db"  # Change to PostgreSQL for production

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Database Models
class Game(Base):
    __tablename__ = "games"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="waiting")
    current_player_id = Column(String)
    phase = Column(String(50), default="waiting")
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    game_settings = Column(JSON)
    
    # Relationships
    players = relationship("Player", back_populates="game", cascade="all, delete-orphan")
    routes = relationship("Route", back_populates="game", cascade="all, delete-orphan")

class Player(Base):
    __tablename__ = "players"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    game_id = Column(String, ForeignKey("games.id"), nullable=False)
    name = Column(String(255), nullable=False)
    color = Column(String(50), nullable=False)
    train_cars = Column(Integer, default=45)
    hand_cards = Column(JSON)
    claimed_routes = Column(JSON)
    destination_tickets = Column(JSON)
    score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    game = relationship("Game", back_populates="players")

class Route(Base):
    __tablename__ = "routes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    game_id = Column(String, ForeignKey("games.id"), nullable=False)
    from_city_id = Column(String, nullable=False)
    to_city_id = Column(String, nullable=False)
    length = Column(Integer, nullable=False)
    color = Column(String(50), nullable=False)
    points = Column(Integer, nullable=False)
    is_double_route = Column(Boolean, default=False)
    double_route_id = Column(String)
    claimed_by_player_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    game = relationship("Game", back_populates="routes")

class City(Base):
    __tablename__ = "cities"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    x = Column(String, nullable=False)  # Store as string to handle decimal precision
    y = Column(String, nullable=False)  # Store as string to handle decimal precision
    region = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database initialization
async def init_db():
    """Initialize the database and create tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions for data conversion
def game_to_dict(game: Game) -> dict:
    """Convert Game database model to dictionary."""
    return {
        "id": game.id,
        "name": game.name,
        "status": game.status,
        "current_player_id": game.current_player_id,
        "phase": game.phase,
        "created_at": game.created_at,
        "started_at": game.started_at,
        "finished_at": game.finished_at,
        "game_settings": game.game_settings or {}
    }

def player_to_dict(player: Player) -> dict:
    """Convert Player database model to dictionary."""
    return {
        "id": player.id,
        "game_id": player.game_id,
        "name": player.name,
        "color": player.color,
        "train_cars": player.train_cars,
        "hand_cards": player.hand_cards or [],
        "claimed_routes": player.claimed_routes or [],
        "destination_tickets": player.destination_tickets or [],
        "score": player.score,
        "created_at": player.created_at
    }

def route_to_dict(route: Route) -> dict:
    """Convert Route database model to dictionary."""
    return {
        "id": route.id,
        "game_id": route.game_id,
        "from_city_id": route.from_city_id,
        "to_city_id": route.to_city_id,
        "length": route.length,
        "color": route.color,
        "points": route.points,
        "is_double_route": route.is_double_route,
        "double_route_id": route.double_route_id,
        "claimed_by_player_id": route.claimed_by_player_id,
        "created_at": route.created_at
    }

def city_to_dict(city: City) -> dict:
    """Convert City database model to dictionary."""
    return {
        "id": city.id,
        "name": city.name,
        "x": float(city.x),
        "y": float(city.y),
        "region": city.region,
        "created_at": city.created_at
    }
