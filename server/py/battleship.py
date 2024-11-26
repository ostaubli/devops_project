"""Battleship game implementation module.

Implements the classic Battleship board game with features including:
- Game state management
- Ship placement mechanics
- Shot targeting system
- Two-player turn management
"""

import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
from server.py.game import Game, Player


class ActionType(str, Enum):
    """Type of possible actions in the game."""
    SET_SHIP = 'set_ship'
    SHOOT = 'shoot'

    @staticmethod
    def list_actions() -> List[str]:
        """List all possible action types."""
        return [action.value for action in ActionType]


@dataclass
class BattleshipAction:
    """Represents an action in the Battleship game."""
    action_type: ActionType
    ship_name: Optional[str]
    location: List[str]

    def is_ship_action(self) -> bool:
        """Check if the action is related to setting a ship."""
        return self.action_type == ActionType.SET_SHIP

    def is_shoot_action(self) -> bool:
        """Check if the action is related to shooting."""
        return self.action_type == ActionType.SHOOT


@dataclass
class Ship:
    """Represents a ship in the Battleship game."""
    name: str
    length: int
    location: Optional[List[str]]

    def is_sunk(self, successful_shots: List[str]) -> bool:
        """Check if the ship is sunk."""
        if self.location is None:
            return False
        return all(loc in successful_shots for loc in self.location)


@dataclass
class ShipPlacement:
    """Represents a ship's placement information."""
    name: str
    length: int

    def is_valid_length(self) -> bool:
        """Validate that the ship length is within standard bounds."""
        return 1 <= self.length <= 5

    def describe(self) -> str:
        """Provide a human-readable description of the ship."""
        return f"Ship '{self.name}' with length {self.length}"


@dataclass
class PlayerState:
    """Represents the state of a player in the game."""

    def __init__(
        self,
        name: str,
        ships: List[Ship],
        shots: List[str],
        successful_shots: List[str]
    ) -> None:
        """Initialize PlayerState."""
        self.name = name
        self.ships = ships
        self.shots = shots
        self.successful_shots = successful_shots

    def reset_shots(self) -> None:
        """Reset all shots for this player."""
        self.shots = []
        self.successful_shots = []

    def count_remaining_ships(self) -> int:
        """Count the number of ships still afloat."""
        return len([ship for ship in self.ships if not ship.is_sunk(self.successful_shots)])


class GamePhase(str, Enum):
    """Type of possible game phases."""
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'


class BattleshipGameState:
    """Represents the complete state of a Battleship game."""

    def __init__(
        self,
        idx_player_active: int,
        phase: GamePhase,
        winner: Optional[int],
        players: List[PlayerState],
    ) -> None:
        """Initialize BattleshipGameState."""
        self.idx_player_active = idx_player_active
        self.phase = phase
        self.winner = winner
        self.players = players

    def is_game_finished(self) -> bool:
        """Check if the game has finished."""
        return self.phase == GamePhase.FINISHED

    def get_active_player(self) -> PlayerState:
        """Get the current active player."""
        return self.players[self.idx_player_active]


class Battleship(Game):
    """Main Battleship game implementation."""

    def __init__(self) -> None:
        """Initialize new Battleship game."""
        self.state = BattleshipGameState(
            idx_player_active=0,
            phase=GamePhase.SETUP,
            winner=None,
            players=[
                PlayerState(
                    name='Player 1',
                    ships=[],
                    shots=[],
                    successful_shots=[]
                ),
                PlayerState(
                    name='Player 2',
                    ships=[],
                    shots=[],
                    successful_shots=[]
                )
            ]
        )

    def validate_ship_placement(self, ship: Ship) -> bool:
        """Validate ship placement rules."""
        board_size = 10
        occupied_locations = {
            loc for player in self.state.players
            for s in player.ships
            if s.location for loc in s.location
        }

        if ship.location is None or len(ship.location) != ship.length:
            return False

        rows = {loc[0] for loc in ship.location}
        cols = {int(loc[1:]) for loc in ship.location}
        if not (len(rows) == 1 or len(cols) == 1):
            return False

        for loc in ship.location:
            row, col = ord(loc[0].upper()) - ord('A'), int(loc[1:]) - 1
            if not (0 <= row < board_size and 0 <= col < board_size):
                return False
            if loc in occupied_locations:
                return False

        return True

    def validate_shot(self, location: str) -> bool:
        """Validate shot location."""
        board_size = 10
        row, col = ord(location[0].upper()) - ord('A'), int(location[1:]) - 1
        if not (0 <= row < board_size and 0 <= col < board_size):
            return False
        active_player = self.state.players[self.state.idx_player_active]
        return location not in active_player.shots

    def check_and_update_phase(self) -> None:
        """Check and update game phase based on current state."""
        if self.state.phase == GamePhase.SETUP and \
                all(len(player.ships) == 5 for player in self.state.players):
            self.state.phase = GamePhase.RUNNING
        elif self.state.phase == GamePhase.RUNNING:
            for i, player in enumerate(self.state.players):
                opponent = self.state.players[1 - i]
                if all(
                    any(loc in player.successful_shots for loc in ship.location or [])
                    for ship in opponent.ships
                ):
                    self.state.phase = GamePhase.FINISHED
                    self.state.winner = i
                    break

    def get_state(self) -> BattleshipGameState:
        """Get current game state."""
        return self.state

    def set_state(self, state: BattleshipGameState) -> None:
        """Set game state."""
        self.state = state

    def print_state(self) -> None:
        """Print current game state to console."""
        print(f'Phase: {self.state.phase}')
        print(f'Winner: {self.state.winner}')
        print(f'Active player: {self.state.idx_player_active}')
        for player in self.state.players:
            print(f'Player: {player.name}')
            print(f'Ships: {player.ships}')
            print(f'Shots: {player.shots}')
            print(f'Successful shots: {player.successful_shots}')

    def get_setup_actions(self) -> List[BattleshipAction]:
        """Get available ship placement actions."""
        active_player = self.state.players[self.state.idx_player_active]
        required_ships = [
            ("destroyer", 2),
            ("submarine", 3),
            ("cruiser", 3),
            ("battleship", 4),
            ("carrier", 5)
        ]

        if len(active_player.ships) >= len(required_ships):
            return []

        next_ship_name, next_length = required_ships[len(active_player.ships)]
        return self._generate_ship_placements(next_ship_name, next_length)

    def _generate_ship_placements(self, ship_name: str, ship_length: int) -> List[BattleshipAction]:
        """Generate all valid ship placements for a ship."""
        available_actions: List[BattleshipAction] = []
        ship = ShipPlacement(ship_name, ship_length)

        for start_row in range(10):
            for start_col in range(10):
                self._try_horizontal_placement(
                    available_actions, ship, start_row, start_col
                )
                self._try_vertical_placement(
                    available_actions, ship, start_row, start_col
                )

        return available_actions

    def _try_horizontal_placement(
        self, actions: List[BattleshipAction],
        ship: ShipPlacement,
        start_row: int,
        start_col: int
    ) -> None:
        """Try to place ship horizontally."""
        if start_col + ship.length <= 10:
            locations = [
                f"{chr(ord('A') + start_row)}{start_col + i + 1}"
                for i in range(ship.length)
            ]
            if self.validate_ship_placement(Ship(ship.name, ship.length, locations)):
                actions.append(
                    BattleshipAction(ActionType.SET_SHIP, ship.name, locations)
                )

    def _try_vertical_placement(
        self, actions: List[BattleshipAction],
        ship: ShipPlacement,
        start_row: int,
        start_col: int
    ) -> None:
        """Try to place ship vertically."""
        if start_row + ship.length <= 10:
            locations = [
                f"{chr(ord('A') + start_row + i)}{start_col + 1}"
                for i in range(ship.length)
            ]
            if self.validate_ship_placement(Ship(ship.name, ship.length, locations)):
                actions.append(
                    BattleshipAction(ActionType.SET_SHIP, ship.name, locations)
                )

    def _get_shooting_actions(self) -> List[BattleshipAction]:
        """Get available shooting actions."""
        active_player = self.state.players[self.state.idx_player_active]
        return [
            BattleshipAction(ActionType.SHOOT, None, [f"{row}{col}"])
            for row in "ABCDEFGHIJ"
            for col in range(1, 11)
            if f"{row}{col}" not in active_player.shots
        ]

    def get_list_action(self) -> List[BattleshipAction]:
        """Get a list of possible actions for the active player."""
        if self.state.phase == GamePhase.SETUP:
            return self.get_setup_actions()
        if self.state.phase == GamePhase.RUNNING:
            return self._get_shooting_actions()
        return []

    def apply_action(self, action: BattleshipAction) -> None:
        """Apply game action."""
        if action.action_type == ActionType.SET_SHIP:
            active_player = self.state.players[self.state.idx_player_active]

            required_ships = {
                "destroyer": 2,
                "submarine": 3,
                "cruiser": 3,
                "battleship": 4,
                "carrier": 5
            }

            if action.ship_name and action.ship_name.lower() not in required_ships:
                raise ValueError(f"Invalid ship name: {action.ship_name}")

            expected_length = required_ships[action.ship_name.lower()] if action.ship_name else 0
            if len(action.location) != expected_length:
                raise ValueError(
                    f"Ship {action.ship_name} must have length {expected_length}"
                )

            new_ship = Ship(
                name=action.ship_name.lower() if action.ship_name else "",
                length=expected_length,
                location=action.location
            )

            if not self.validate_ship_placement(new_ship):
                raise ValueError(
                    f"Invalid placement for {new_ship.name} at locations: {new_ship.location}"
                )

            active_player.ships.append(new_ship)
            self.state.idx_player_active = 1 - self.state.idx_player_active
            self.check_and_update_phase()

        elif action.action_type == ActionType.SHOOT:
            location = action.location[0]
            if not self.validate_shot(location):
                raise ValueError(f"Invalid shot location: {location}")

            active_player = self.state.players[self.state.idx_player_active]
            opponent = self.state.players[1 - self.state.idx_player_active]

            active_player.shots.append(location)
            if any(location in ship.location for ship in opponent.ships if ship.location):
                active_player.successful_shots.append(location)

            self.state.idx_player_active = 1 - self.state.idx_player_active

    def get_player_view(self, idx_player: int) -> BattleshipGameState:
        """Get game state from player perspective."""
        masked_state = BattleshipGameState(
            idx_player_active=self.state.idx_player_active,
            phase=self.state.phase,
            winner=self.state.winner,
            players=[]
        )
        for i, player in enumerate(self.state.players):
            if i == idx_player:
                masked_state.players.append(player)
            else:
                masked_state.players.append(
                    PlayerState(
                        name=player.name,
                        ships=[],
                        shots=player.shots,
                        successful_shots=["hit" for _ in player.successful_shots]
                    )
                )
        return masked_state


class RandomPlayer(Player):
    """Player that makes random valid moves."""

    def __init__(self) -> None:
        """Initialize random player."""
        self.past_shots: set[str] = set()

    def select_action(
        self, state: BattleshipGameState, actions: List[BattleshipAction]
    ) -> Optional[BattleshipAction]:
        """Select random valid action."""
        if state.phase == GamePhase.RUNNING:
            valid_shots = [
                action for action in actions if action.location[0] not in self.past_shots
            ]
            if valid_shots:
                chosen_action = random.choice(valid_shots)
                self.past_shots.add(chosen_action.location[0])
                return chosen_action
            return None
        return random.choice(actions) if actions else None

    def reset_shots(self) -> None:
        """Reset the past shots."""
        self.past_shots = set()

    def get_past_shots(self) -> set:
        """Return the list of past shots."""
        return self.past_shots


if __name__ == "__main__":
    game = Battleship()
