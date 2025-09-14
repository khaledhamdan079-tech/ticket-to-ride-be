from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timezone
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# For Railway PostgreSQL, convert postgres:// to postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Game(Base):
    __tablename__ = "games"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(String, default="waiting")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Player(Base):
    __tablename__ = "players"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    game_id = Column(String, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class GameCreate(BaseModel):
    name: str

class GameResponse(BaseModel):
    id: str
    name: str
    status: str
    created_at: datetime
    players: list = []

class PlayerCreate(BaseModel):
    name: str
    game_id: str

class PlayerResponse(BaseModel):
    id: str
    name: str
    game_id: str
    created_at: datetime

# FastAPI app
app = FastAPI(title="Ticket to Ride API with Database")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Ticket to Ride Backend API with Database", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}

@app.get("/api/test")
def test():
    return {"message": "API is working with database", "timestamp": datetime.now(timezone.utc)}

# Database endpoints
@app.post("/api/games", response_model=GameResponse)
def create_game(game: GameCreate, db: Session = Depends(get_db)):
    import uuid
    game_id = str(uuid.uuid4())
    
    db_game = Game(id=game_id, name=game.name, status="waiting")
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    
    return GameResponse(
        id=db_game.id,
        name=db_game.name,
        status=db_game.status,
        created_at=db_game.created_at,
        players=[]
    )

@app.get("/api/games", response_model=list[GameResponse])
def get_games(db: Session = Depends(get_db)):
    games = db.query(Game).all()
    return [
        GameResponse(
            id=game.id,
            name=game.name,
            status=game.status,
            created_at=game.created_at,
            players=[]
        ) for game in games
    ]

@app.get("/api/games/{game_id}", response_model=GameResponse)
def get_game(game_id: str, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    players = db.query(Player).filter(Player.game_id == game_id).all()
    
    return GameResponse(
        id=game.id,
        name=game.name,
        status=game.status,
        created_at=game.created_at,
        players=[{"id": p.id, "name": p.name} for p in players]
    )

@app.post("/api/players", response_model=PlayerResponse)
def create_player(player: PlayerCreate, db: Session = Depends(get_db)):
    import uuid
    player_id = str(uuid.uuid4())
    
    # Check if game exists
    game = db.query(Game).filter(Game.id == player.game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    db_player = Player(id=player_id, name=player.name, game_id=player.game_id)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    
    return PlayerResponse(
        id=db_player.id,
        name=db_player.name,
        game_id=db_player.game_id,
        created_at=db_player.created_at
    )

@app.get("/api/players/{game_id}", response_model=list[PlayerResponse])
def get_players(game_id: str, db: Session = Depends(get_db)):
    players = db.query(Player).filter(Player.game_id == game_id).all()
    return [
        PlayerResponse(
            id=player.id,
            name=player.name,
            game_id=player.game_id,
            created_at=player.created_at
        ) for player in players
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
