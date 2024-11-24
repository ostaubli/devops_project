import random
from enum import Enum
from typing import List, Optional
from server.py.game import Game, Player


class ActionType(str, Enum):
    SET_SHIP = 'set_ship'
    SHOOT = 'shoot'


class BattleshipAction:

    def __init__(self, action_type: ActionType, ship_name: Optional[str], location: List[str]) -> None:
        self.action_type = action_type
        self.ship_name = ship_name  # only for set_ship actions
        self.location = location


class Ship:

    def __init__(self, name: str, length: int, location: Optional[List[str]]) -> None:
        self.name = name
        self.length = length
        self.location = location


class PlayerState:

    def __init__(self, name: str, ships: List[Ship], shots: List[str], successful_shots: List[str]) -> None:
        self.name = name
        self.ships = ships
        self.shots = shots
        self.successful_shots = successful_shots


class GamePhase(str, Enum):
    SETUP = 'setup'  # before the game has started (including setting ships)
    RUNNING = 'running'  # while the game is running (shooting)
    FINISHED = 'finished'  # when the game is finished


class BattleshipGameState:

    def __init__(self, idx_player_active: int, phase: GamePhase, winner: Optional[int],
                 players: List[PlayerState]) -> None:
        self.idx_player_active = idx_player_active
        self.phase = phase
        self.winner = winner
        self.players = players


class Battleship(Game):

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary) """
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
        """Validate if the ship placement is within bounds, does not overlap, and is aligned.
        :type ship: Ship"""
        board_size = 10
        occupied_locations = {
            loc for player in self.state.players for s in player.ships for loc in s.location
        }

        # Validate ship length
        if len(ship.location) != ship.length:
            return False

        # Validate alignment (horizontal or vertical)
        rows = {loc[0] for loc in ship.location}
        cols = {int(loc[1:]) for loc in ship.location}
        if not (len(rows) == 1 or len(cols) == 1):  # Must be aligned
            return False

        # Check bounds and overlaps
        for loc in ship.location:
            row, col = ord(loc[0].upper()) - ord('A'), int(loc[1:]) - 1
            if not (0 <= row < board_size and 0 <= col < board_size):  # Out of bounds
                return False
            if loc in occupied_locations:  # Overlap
                return False

        return True

    def validate_shot(self, location: str) -> bool:
        """Check if the shot location is valid and not previously targeted.
        :type location: str
        """
        board_size = 10
        row, col = ord(location[0].upper()) - ord('A'), int(location[1:]) - 1
        if not (0 <= row < board_size and 0 <= col < board_size):  # Out of bounds
            return False
        active_player = self.state.players[self.state.idx_player_active]
        if location in active_player.shots:  # Already targeted
            return False
        return True

    def check_and_update_phase(self) -> None:
        """Check game state and update phase if necessary."""
        if self.state.phase == GamePhase.SETUP:
            if all(len(player.ships) == 5 for player in self.state.players):  # Exactly 5 ships per player
                self.state.phase = GamePhase.RUNNING
        elif self.state.phase == GamePhase.RUNNING:
            for i, player in enumerate(self.state.players):
                if all(any(loc in player.successful_shots for loc in s.location) for s in player.ships):
                    self.state.phase = GamePhase.FINISHED
                    self.state.winner = 1 - i
                    break

    def print_state(self) -> None:
        """ Print the current game state """
        print(f'Phase: {self.state.phase}')
        print(f'Winner: {self.state.winner}')
        print(f'Active player: {self.state.idx_player_active}')
        for player in self.state.players:
            print(f'Player: {player.name}')
            print(f'Ships: {player.ships}')
            print(f'Shots: {player.shots}')
            print(f'Successful shots: {player.successful_shots}')

    def get_state(self) -> BattleshipGameState:
        """ Get the complete, unmasked game state """
        return self.state

    def set_state(self, state: BattleshipGameState) -> None:
        """ Set the game to a given state
        :type state: BattleshipGameState
        """
        self.state = state

    def get_list_action(self) -> List[BattleshipAction]:
        """Get a list of possible actions for the active player."""
        if self.state.phase == GamePhase.SETUP:
            available_actions = []
            active_player = self.state.players[self.state.idx_player_active]
            required_ships = [("Destroyer", 2), ("Submarine", 3), ("Cruiser", 3), ("Battleship", 4), ("Carrier", 5)]

            # Determine the next required ship
            if len(active_player.ships) < len(required_ships):
                next_ship_name, next_length = required_ships[len(active_player.ships)]
                for start_row in "ABCDEFGHIJ":
                    for start_col in range(1, 11):
                        for orientation in ["H", "V"]:
                            locations = [
                                f"{chr(ord(start_row) + i if orientation == 'V' else 0)}{start_col + i if orientation == 'H' else start_col}"
                                for i in range(next_length)
                            ]
                            if self.validate_ship_placement(Ship(next_ship_name, next_length, locations)):
                                available_actions.append(
                                    BattleshipAction(ActionType.SET_SHIP, next_ship_name, locations)
                                )
            return available_actions

        elif self.state.phase == GamePhase.RUNNING:
            active_player = self.state.players[self.state.idx_player_active]
            return [
                BattleshipAction(ActionType.SHOOT, None, [f"{row}{col}"])
                for row in "ABCDEFGHIJ"
                for col in range(1, 11)
                if f"{row}{col}" not in active_player.shots
            ]
        return []

    def apply_action(self, action: BattleshipAction) -> None:
        """Apply the given action to the game.
        :type action: BattleshipAction
        """
        if action.action_type == ActionType.SET_SHIP:
            active_player = self.state.players[self.state.idx_player_active]
        
            required_ships = {
                "destroyer": 2,
                "submarine": 3,
                "cruiser": 3,
                "battleship": 4,
                "carrier": 5
            }
        
            if action.ship_name.lower() not in required_ships:
                raise ValueError(f"Invalid ship name: {action.ship_name}")
            
            expected_length = required_ships[action.ship_name.lower()]
            if len(action.location) != expected_length:
                raise ValueError(f"Ship {action.ship_name} must have length {expected_length}")

            new_ship = Ship(
                name=action.ship_name.lower(),
                length=expected_length,
                location=action.location
            )
        
            if not self.validate_ship_placement(new_ship):
                raise ValueError(f"Invalid placement for {new_ship.name} at locations: {new_ship.location}")
            
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
            if any(location in ship.location for ship in opponent.ships):
                active_player.successful_shots.append(location)

            self.state.idx_player_active = 1 - self.state.idx_player_active

    def get_player_view(self, idx_player: int) -> BattleshipGameState:
        """ Get the masked state for the active player (e.g. the opponent's cards are face down)
        :type idx_player: int
        """
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

    def __init__(self) -> None:
        self.past_shots = set()

    def select_action(self, state: BattleshipGameState, actions: List[BattleshipAction]) -> Optional[BattleshipAction]:
        """ Given masked game state and possible actions, select the next action
        :type state: BattleshipGameState
        :type actions: List[BattleshipAction]
        """
        if state.phase == GamePhase.RUNNING:
            valid_shots = [
                action for action in actions
                if action.location[0] not in self.past_shots
            ]
            if valid_shots:
                chosen_action = random.choice(valid_shots)
                self.past_shots.add(chosen_action.location[0])
                return chosen_action
            return None  # No valid actions left
        return random.choice(actions) if actions else None


if __name__ == "__main__":
    game = Battleship()
