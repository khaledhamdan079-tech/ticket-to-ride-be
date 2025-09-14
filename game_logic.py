from typing import List, Dict, Optional
import uuid
import random
from datetime import datetime, timezone
from models import (
    GameState, Player, Route, City, TrainCard, DestinationTicket,
    GamePhase, RouteColor
)
from database import SessionLocal, Game, Player as DBPlayer, Route as DBRoute, City as DBCity
from game_data import GAME_CITIES, GAME_ROUTES, TRAIN_CARDS, DESTINATION_TICKETS

class GameManager:
    def __init__(self):
        self.games: Dict[str, GameState] = {}
    
    async def create_game(self, game_id: str, name: str, player_name: str, player_id: str) -> GameState:
        """Create a new game with the specified name and add the creator as the first player."""
        # Create player
        player = Player(
            id=player_id,
            name=player_name,
            color="red",  # First player gets red
            trainCars=45,
            hand=[],
            claimedRoutes=[],
            destinationTickets=[],
            score=0,
            isActive=True
        )
        
        # Initialize game data
        cities = self._initialize_cities()
        routes = self._initialize_routes(cities)
        train_cards = self._initialize_train_cards()
        destination_tickets = self._initialize_destination_tickets(cities)
        
        # Shuffle decks
        random.shuffle(train_cards)
        random.shuffle(destination_tickets)
        
        # Deal initial cards to player (4 train cards)
        player_hand = train_cards[:4]
        train_cards = train_cards[4:]
        
        # Set up face-up cards (5 cards)
        face_up_cards = train_cards[:5]
        train_cards = train_cards[5:]
        
        # Assign the initial hand to the player
        player.hand = player_hand
        
        # Create game state
        game = GameState(
            id=game_id,
            name=name,
            players=[player],
            currentPlayer=player,
            phase=GamePhase.WAITING,
            trainCardDeck=train_cards,
            faceUpCards=face_up_cards,
            destinationTicketDeck=destination_tickets,
            availableRoutes=routes,
            allRoutes=routes,
            cities=cities,
            createdAt=datetime.now(timezone.utc),
            gameSettings={}
        )
        
        # Store in memory
        self.games[game_id] = game
        
        # Save to database
        await self._save_game_to_db(game)
        
        return game
    
    async def join_game(self, game_id: str, player_name: str, player_id: str) -> GameState:
        """Add a new player to an existing game."""
        if game_id not in self.games:
            raise Exception("Game not found")
        
        game = self.games[game_id]
        
        if len(game.players) >= 5:  # Maximum 5 players
            raise Exception("Game is full")
        
        if game.phase != GamePhase.WAITING:
            raise Exception("Game has already started")
        
        # Assign color to new player
        used_colors = {p.color for p in game.players}
        available_colors = ["red", "blue", "green", "yellow", "black"]
        player_color = next((c for c in available_colors if c not in used_colors), "blue")
        
        # Create new player
        new_player = Player(
            id=player_id,
            name=player_name,
            color=player_color,
            trainCars=45,
            hand=[],
            claimedRoutes=[],
            destinationTickets=[],
            score=0,
            isActive=False
        )
        
        # Deal initial cards to new player
        if len(game.trainCardDeck) >= 4:
            player_hand = game.trainCardDeck[:4]
            game.trainCardDeck = game.trainCardDeck[4:]
            new_player.hand = player_hand
        
        # Add player to game
        game.players.append(new_player)
        
        # Save to database
        await self._save_game_to_db(game)
        
        return game
    
    async def get_game(self, game_id: str) -> Optional[GameState]:
        """Get game state by ID."""
        if game_id in self.games:
            return self.games[game_id]
        
        # Try to load from database
        game = await self._load_game_from_db(game_id)
        if game:
            self.games[game_id] = game
        
        return game
    
    async def start_game(self, game_id: str, player_id: str) -> GameState:
        """Start a game that has enough players."""
        game = await self.get_game(game_id)
        if not game:
            raise Exception("Game not found")
        
        if len(game.players) < 2:
            raise Exception("Need at least 2 players to start")
        
        if game.phase != GamePhase.WAITING:
            raise Exception("Game has already started")
        
        # Check if requesting player is in the game
        if not any(p.id == player_id for p in game.players):
            raise Exception("Player not in game")
        
        # Start the game
        game.phase = GamePhase.INITIAL_TICKETS
        game.startedAt = datetime.now(timezone.utc)
        
        # Deal initial destination tickets to each player (3 tickets, keep at least 2)
        for player in game.players:
            if len(game.destinationTicketDeck) >= 3:
                player_tickets = game.destinationTicketDeck[:3]
                game.destinationTicketDeck = game.destinationTicketDeck[3:]
                player.destinationTickets = player_tickets
        
        # Save to database
        await self._save_game_to_db(game)
        
        return game
    
    async def draw_train_cards(self, game_id: str, player_id: str, card_ids: List[str]) -> GameState:
        """Allow a player to draw train cards from face-up cards or the deck."""
        game = await self.get_game(game_id)
        if not game:
            raise Exception("Game not found")
        
        if game.phase != GamePhase.PLAYING:
            raise Exception("Game is not in playing phase")
        
        # Find player
        player = next((p for p in game.players if p.id == player_id), None)
        if not player:
            raise Exception("Player not found")
        
        if game.currentPlayer.id != player_id:
            raise Exception("Not your turn")
        
        # Validate card IDs
        available_cards = game.faceUpCards + game.trainCardDeck
        available_card_ids = [card.id for card in available_cards]
        
        for card_id in card_ids:
            if card_id not in available_card_ids:
                raise Exception(f"Card {card_id} not available")
        
        # Draw cards
        drawn_cards = []
        for card_id in card_ids:
            # Try to find in face-up cards first
            face_up_card = next((c for c in game.faceUpCards if c.id == card_id), None)
            if face_up_card:
                game.faceUpCards.remove(face_up_card)
                drawn_cards.append(face_up_card)
            else:
                # Find in deck
                deck_card = next((c for c in game.trainCardDeck if c.id == card_id), None)
                if deck_card:
                    game.trainCardDeck.remove(deck_card)
                    drawn_cards.append(deck_card)
        
        # Add cards to player's hand
        player.hand.extend(drawn_cards)
        
        # Refill face-up cards if needed
        while len(game.faceUpCards) < 5 and game.trainCardDeck:
            game.faceUpCards.append(game.trainCardDeck.pop(0))
        
        # Save to database
        await self._save_game_to_db(game)
        
        return game
    
    async def claim_route(self, game_id: str, player_id: str, route_id: str, card_ids: List[str]) -> GameState:
        """Allow a player to claim a route using train cards."""
        game = await self.get_game(game_id)
        if not game:
            raise Exception("Game not found")
        
        if game.phase != GamePhase.PLAYING:
            raise Exception("Game is not in playing phase")
        
        # Find player
        player = next((p for p in game.players if p.id == player_id), None)
        if not player:
            raise Exception("Player not found")
        
        if game.currentPlayer.id != player_id:
            raise Exception("Not your turn")
        
        # Find route
        route = next((r for r in game.availableRoutes if r.id == route_id), None)
        if not route:
            raise Exception("Route not found")
        
        # Validate cards
        if not self._validate_route_claim(player, route, card_ids):
            raise Exception("Invalid cards for route claim")
        
        # Remove cards from player's hand
        for card_id in card_ids:
            card = next((c for c in player.hand if c.id == card_id), None)
            if card:
                player.hand.remove(card)
        
        # Claim route
        player.claimedRoutes.append(route)
        player.score += route.points
        player.trainCars -= route.length
        
        # Remove route from available routes
        game.availableRoutes.remove(route)
        
        # Check for game end conditions
        if player.trainCars <= 2:
            game.phase = GamePhase.FINISHED
            game.finishedAt = datetime.utcnow()
            await self._calculate_final_scores(game)
        
        # Save to database
        await self._save_game_to_db(game)
        
        return game
    
    async def draw_destination_tickets(self, game_id: str, player_id: str, ticket_ids: List[str]) -> GameState:
        """Allow a player to draw destination tickets."""
        game = await self.get_game(game_id)
        if not game:
            raise Exception("Game not found")
        
        if game.phase not in [GamePhase.INITIAL_TICKETS, GamePhase.PLAYING]:
            raise Exception("Cannot draw tickets in current phase")
        
        # Find player
        player = next((p for p in game.players if p.id == player_id), None)
        if not player:
            raise Exception("Player not found")
        
        if game.currentPlayer.id != player_id:
            raise Exception("Not your turn")
        
        # Validate ticket IDs
        available_ticket_ids = [t.id for t in game.destinationTicketDeck]
        for ticket_id in ticket_ids:
            if ticket_id not in available_ticket_ids:
                raise Exception(f"Ticket {ticket_id} not available")
        
        # Draw tickets
        drawn_tickets = []
        for ticket_id in ticket_ids:
            ticket = next((t for t in game.destinationTicketDeck if t.id == ticket_id), None)
            if ticket:
                game.destinationTicketDeck.remove(ticket)
                drawn_tickets.append(ticket)
        
        # Add tickets to player
        player.destinationTickets.extend(drawn_tickets)
        
        # If in initial tickets phase, move to playing phase
        if game.phase == GamePhase.INITIAL_TICKETS:
            game.phase = GamePhase.PLAYING
        
        # Save to database
        await self._save_game_to_db(game)
        
        return game
    
    async def end_turn(self, game_id: str, player_id: str) -> GameState:
        """End the current player's turn and move to the next player."""
        game = await self.get_game(game_id)
        if not game:
            raise Exception("Game not found")
        
        if game.phase not in [GamePhase.INITIAL_TICKETS, GamePhase.PLAYING]:
            raise Exception("Cannot end turn in current phase")
        
        # Find player
        player = next((p for p in game.players if p.id == player_id), None)
        if not player:
            raise Exception("Player not found")
        
        if game.currentPlayer.id != player_id:
            raise Exception("Not your turn")
        
        # Move to next player
        current_index = game.players.index(player)
        next_index = (current_index + 1) % len(game.players)
        game.currentPlayer = game.players[next_index]
        
        # Update isActive flags
        for p in game.players:
            p.isActive = (p.id == game.currentPlayer.id)
        
        # Save to database
        await self._save_game_to_db(game)
        
        return game
    
    def _validate_route_claim(self, player: Player, route: Route, card_ids: List[str]) -> bool:
        """Validate if player can claim route with given cards."""
        if len(card_ids) != route.length:
            return False
        
        # Get cards from player's hand
        cards = [c for c in player.hand if c.id in card_ids]
        if len(cards) != route.length:
            return False
        
        # Check if cards match route requirements
        if route.color == RouteColor.GRAY:
            # Gray routes can be claimed with any color
            return True
        else:
            # Check if all cards match route color or are locomotives
            return all(card.color == route.color or card.isLocomotive for card in cards)
    
    async def _calculate_final_scores(self, game: GameState):
        """Calculate final scores including destination ticket bonuses/penalties."""
        for player in game.players:
            # Calculate destination ticket scores
            for ticket in player.destinationTickets:
                # Check if player has connected the cities
                if self._has_connected_cities(player, ticket.from_city, ticket.to_city):
                    player.score += ticket.points
                else:
                    player.score -= ticket.penalty
    
    def _has_connected_cities(self, player: Player, from_city: City, to_city: City) -> bool:
        """Check if player has connected two cities through their claimed routes."""
        # This is a simplified implementation
        # In a real implementation, you'd need to implement pathfinding
        # For now, we'll assume all destination tickets are completed
        return True
    
    def _initialize_cities(self) -> List[City]:
        """Initialize all game cities."""
        cities = []
        for city_data in GAME_CITIES:
            city = City(
                id=city_data["id"],
                name=city_data["name"],
                x=city_data["x"],
                y=city_data["y"],
                region=city_data["region"]
            )
            cities.append(city)
        return cities
    
    def _initialize_routes(self, cities: List[City]) -> List[Route]:
        """Initialize all game routes."""
        routes = []
        city_dict = {city.id: city for city in cities}
        
        for route_data in GAME_ROUTES:
            from_city = city_dict[route_data["from_city_id"]]
            to_city = city_dict[route_data["to_city_id"]]
            
            route = Route(
                id=route_data["id"],
                from_city=from_city,
                to_city=to_city,
                length=route_data["length"],
                color=RouteColor(route_data["color"]),
                points=route_data["points"],
                isDoubleRoute=route_data.get("is_double_route", False),
                doubleRouteId=route_data.get("double_route_id")
            )
            routes.append(route)
        return routes
    
    def _initialize_train_cards(self) -> List[TrainCard]:
        """Initialize train card deck."""
        cards = []
        for card_data in TRAIN_CARDS:
            for _ in range(card_data["count"]):
                card = TrainCard(
                    id=str(uuid.uuid4()),
                    color=RouteColor(card_data["color"]),
                    isLocomotive=card_data.get("is_locomotive", False)
                )
                cards.append(card)
        return cards
    
    def _initialize_destination_tickets(self, cities: List[City]) -> List[DestinationTicket]:
        """Initialize destination ticket deck."""
        tickets = []
        city_dict = {city.id: city for city in cities}
        
        for i, ticket_data in enumerate(DESTINATION_TICKETS):
            try:
                if "from_city_id" not in ticket_data:
                    print(f"Missing from_city_id in ticket {i}: {ticket_data}")
                    continue
                if "to_city_id" not in ticket_data:
                    print(f"Missing to_city_id in ticket {i}: {ticket_data}")
                    continue
                    
                from_city = city_dict[ticket_data["from_city_id"]]
                to_city = city_dict[ticket_data["to_city_id"]]
                
                ticket = DestinationTicket(
                    id=str(uuid.uuid4()),
                    from_city=from_city,
                    to_city=to_city,
                    points=ticket_data["points"],
                    penalty=ticket_data["penalty"]
                )
                tickets.append(ticket)
            except KeyError as e:
                print(f"KeyError in ticket {i}: {e}, ticket_data: {ticket_data}")
                continue
        return tickets
    
    async def _save_game_to_db(self, game: GameState):
        """Save game state to database."""
        # This is a simplified implementation
        # In a real implementation, you'd save all the game data to the database
        pass
    
    async def _load_game_from_db(self, game_id: str) -> Optional[GameState]:
        """Load game state from database."""
        # This is a simplified implementation
        # In a real implementation, you'd load all the game data from the database
        return None
