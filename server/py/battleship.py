"""
Battleship game implementation with player actions and game state management.
This module provides classes for managing a two-player Battleship game.
"""

from typing import List, Optional
from enum import Enum
import random
from pydantic import BaseModel, Field, model_validator
from server.py.game import Game, Player

# Constants
MAX_SHIP_COUNT = 5  # Max. Number of Ships
EXIT_ACTION = 999   # Exit the Game
GRID_ROWS = 'ABCDEFGHIJ'
GRID_COLS = range(1, 11)

class ActionType(str, Enum):
    """
    Represents the possible action types in battleship.
    """
    SET_SHIP = 'set_ship'
    SHOOT = 'shoot'

class BattleshipAction(BaseModel):
    """
    Represents an action in the Battleship game.
    """
    action_type: ActionType
    ship_name: Optional[str]  # Only for set_ship actions
    location: List[str]

class Ship(BaseModel):
    """
    Represents a ship in the game.
    """
    name: str
    length: int
    location: Optional[List[str]] = Field(default=None)

class PlayerState(BaseModel):
    """
    Represents all information of a player.
    """
    name: str
    ships: List[Ship] = Field(default_factory=list)
    shots: List[str] = Field(default_factory=list)
    successful_shots: List[str] = Field(default_factory=list)

class GamePhase(str, Enum):
    """
    Represents the current phase in the game.
    """
    SETUP = 'setup'            # before the game has started (including setting ships)
    RUNNING = 'running'        # while the game is running (shooting)
    FINISHED = 'finished'      # when the game is finished

class BattleshipGameState(BaseModel):
    """
    Represents the current state of the game.
    """
    idx_player_active: int
    phase: GamePhase
    winner: Optional[int] = None
    players: List[PlayerState]

    @model_validator(mode="after")
    def validate_players(cls, values: "BattleshipGameState"):
        """Ensure exactly two players are present."""
        if len(values.players) != 2:
            raise ValueError("There must be exactly two players.")
        return values

class Battleship(Game):
    """
    Main Battleship game class.
    Handles game state and game logic for battleship.
    """
    def __init__(self):
        """ Game initialization (set_state call not necessary) """
        self.state = BattleshipGameState(
            idx_player_active=0,
            phase=GamePhase.SETUP,
            players=[
                PlayerState(name="Player 1"),
                PlayerState(name="Player 2"),
            ],
        )

    def print_state(self) -> None:
        """ Print the current game state """
        print(f"Game Phase: {self.state.phase}")
        print(f"Active Player: {self.state.idx_player_active + 1}")
        if self.state.winner is not None:
            print(f"Winner: Player {self.state.winner + 1}")

        for idx, player in enumerate(self.state.players):
            print(f"\nPlayer {idx + 1}:")
            print(f"Ships: {[f'{ship.name} at {ship.location}' for ship in player.ships]}")
            print(f"Shots: {player.shots}")
            print(f"Hits: {player.successful_shots}")

    def get_state(self) -> BattleshipGameState:
        """ Get the complete, unmasked game state. Returns a copy of current game state to 
        ensure no external modifications affect the internal game state afterwards."""
        return self.state.copy(deep=True)

    def set_state(self, state: BattleshipGameState) -> None:
        """Set the game state with defensive copying to ensure encapsulation."""
        if not isinstance(state, BattleshipGameState):
            raise ValueError("Invalid state type.")
        self.state = state.copy()

    def get_list_action(self) -> List[BattleshipAction]:
        """ Get a list of possible actions for the active player """
        actions = []
        if not self.state:
            return actions

        current_player = self.state.players[self.state.idx_player_active]

        if self.state.phase == GamePhase.SETUP:
            # Define available ships
            SHIPS_CONFIG = [
                ("Carrier", 5),
                ("Battleship", 4),
                ("Cruiser", 3),
                ("Submarine", 3),
                ("Destroyer", 2)
            ]

            if len(current_player.ships) < len(SHIPS_CONFIG):
                ship_name, length = SHIPS_CONFIG[len(current_player.ships)]
                # Get existing ship locations for validation
                existing_locations = set(
                    loc
                    for ship in current_player.ships
                    for loc in ship.location
                )

                # Simplified ship placement - both horizontal and vertical
                for row in GRID_ROWS:
                    for col in range(1, 11 - length + 1):
                        # Horizontal placement
                        horizontal_location = [f"{row}{col + i}" for i in range(length)]
                        if set(horizontal_location).isdisjoint(existing_locations):
                            actions.append(BattleshipAction(
                                action_type=ActionType.SET_SHIP,
                                ship_name=ship_name,
                                location=horizontal_location
                            ))

                        # Vertical placement
                        if ord(row) + length - 1 <= ord('J'):
                            vertical_location = [f"{chr(ord(row) + i)}{col}" for i in range(length)]
                            if set(vertical_location).isdisjoint(existing_locations):
                                actions.append(BattleshipAction(
                                    action_type=ActionType.SET_SHIP,
                                    ship_name=ship_name,
                                    location=vertical_location
                                ))

        elif self.state.phase == GamePhase.RUNNING:
            # Generate all possible shots excluding already taken shots
            taken_shots = set(current_player.shots)
            for row in GRID_ROWS:
                for col in GRID_COLS:
                    location = f"{row}{col}"
                    if location not in taken_shots:  # Exclude already shot locations
                        actions.append(BattleshipAction(
                            action_type=ActionType.SHOOT,
                            ship_name=None,
                            location=[location]
                        ))

        return actions

    def apply_action(self, action: Optional[BattleshipAction] = None) -> None:
        """Apply the given action to the game."""
        if not self.state or not action:
            return

        current_player = self.state.players[self.state.idx_player_active]
        opponent = self.state.players[1 - self.state.idx_player_active]

        if self.state.phase == GamePhase.SETUP:
            if action.action_type == ActionType.SET_SHIP:
                # Validate that the new ship's location does not overlap with existing ships
                existing_locations = set(
                    loc
                    for ship in current_player.ships
                    for loc in ship.location
                )
                new_ship_locations = set(action.location)
                if not set(action.location).isdisjoint(existing_locations):
                    raise ValueError("Ships cannot overlap.")

                # Add ship to the current player's fleet
                ship = Ship(name=action.ship_name, length=len(action.location), location=action.location)
                current_player.ships.append(ship)

                # Check if all ships are placed for all players
                if all(len(player.ships) == MAX_SHIP_COUNT for player in self.state.players):
                    self.state.phase = GamePhase.RUNNING
                else:
                    # Switch to the next player
                    self.switch_turn()

        elif self.state.phase == GamePhase.RUNNING:
            if action.action_type == ActionType.SHOOT:
                shot_location = action.location[0]
                current_player.shots.append(shot_location)  # Record the shot

                # Check if shot hit any opponent ships
                for ship in opponent.ships:
                    if shot_location in ship.location:
                        current_player.successful_shots.append(shot_location)  # Record successful shot
                        if all(loc in current_player.successful_shots for loc in ship.location):
                            print(f"{ship.name} has been sunk!") 

                        # Check win condition
                        if all(
                            all(loc in current_player.successful_shots for loc in ship.location) 
                            for ship in opponent.ships):
                            self.state.phase = GamePhase.FINISHED
                            self.state.winner = self.state.idx_player_active
                        break

                # Always switch turns unless game is finished
                if self.state.phase != GamePhase.FINISHED:
                    self.switch_turn()

    def switch_turn(self) -> None:
        """Switch the active player's turn."""
        self.state.idx_player_active = 1 - self.state.idx_player_active

    def get_player_view(self, idx_player: int) -> BattleshipGameState:
        """Get the masked state for the active player (e.g., the opponent's ships are hidden)."""
        # Current player's view
        current_player = self.state.players[idx_player]
        
        # Opponent's view
        opponent_player = self.state.players[1 - idx_player]
        
        # Create masked opponent player state
        masked_opponent = PlayerState(
            name=opponent_player.name,
            ships=[Ship(ship.name, ship.length, None) for ship in opponent_player.ships],  # Hide ship locations
            shots=opponent_player.shots,  # Opponent's shots are visible
            successful_shots=opponent_player.successful_shots  # Opponent's successful hits are visible
        )
        
        # Create full view of current player's state
        visible_current_player = PlayerState(
            name=current_player.name,
            ships=current_player.ships,  # All ships are visible
            shots=current_player.shots,
            successful_shots=current_player.successful_shots
        )
        
        # Construct and return the masked game state
        return BattleshipGameState(
            idx_player_active=self.state.idx_player_active,
            phase=self.state.phase,
            winner=self.state.winner,
            players=[visible_current_player, masked_opponent] if idx_player == 0 else [masked_opponent, visible_current_player]
        )

class RandomPlayer(Player):
    """
    A random player for the Battleship game. This player selects actions randomly from the available list of actions.
    """

    def select_action(self, 
        state: BattleshipGameState, 
        actions: List[BattleshipAction]) -> Optional[BattleshipAction]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None

if __name__ == "__main__":

    game = Battleship()
    
    while game.state.phase != GamePhase.FINISHED:
        game.print_state()
        actions = game.get_list_action()

        # Display possible actions
        print("\nPossible Actions:")
        for idx, action in enumerate(actions):
            if action.action_type == ActionType.SET_SHIP:
                print(f"{idx}: {action.action_type.value} - Ship: {action.ship_name}, Location: {action.location}")
            elif action.action_type == ActionType.SHOOT:
                print(f"{idx}: {action.action_type.value} - Location: {action.location}")

        # Get user input
        choice = int(input("\nSelect an action (enter the number): "))
        if choice == EXIT_ACTION:
            print("Exiting the game. Goodbye!")
            break
