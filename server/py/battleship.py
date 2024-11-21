from typing import List, Optional
from enum import Enum
import random
from server.py.game import Game, Player


class ActionType(str, Enum):
    SET_SHIP = 'set_ship'
    SHOOT = 'shoot'


class BattleshipAction:

    def __init__(self, action_type: ActionType, ship_name: Optional[str], location: List[str]) -> None:
        self.action_type = action_type
        self.ship_name = ship_name # only for set_ship actions
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
    SETUP = 'setup'            # before the game has started (including setting ships)
    RUNNING = 'running'        # while the game is running (shooting)
    FINISHED = 'finished'      # when the game is finished


class BattleshipGameState:

    def __init__(self, idx_player_active: int, phase: GamePhase, winner: Optional[int], players: List[PlayerState]) -> None:
        self.idx_player_active = idx_player_active
        self.phase = phase
        self.winner = winner
        self.players = players


class Battleship(Game):

    def __init__(self):
        """ Game initialization (set_state call not necessary) """
        pass

    def print_state(self) -> None:
        """ Set the game to a given state """
        pass

    def get_state(self) -> BattleshipGameState:
        """ Get the complete, unmasked game state """
        pass

    def set_state(self, state: BattleshipGameState) -> None:
        """ Print the current game state """
        pass

    def get_list_action(self) -> List[BattleshipAction]:
        """ Get a list of possible actions for the active player """
        state = self.get_state()  # Retrieve the current game state
        actions = []  # Initialize the list of possible actions

        # Get the active player and their state
        active_player_idx = state.idx_player_active
        active_player = state.players[active_player_idx]

        if state.phase == GamePhase.SETUP:
            # SETUP Phase: Generate actions to set ships
            for ship in active_player.ships:
                if not ship.location:  # Check if the ship is not yet placed
                    # Example logic to add potential ship placement actions
                    # Assuming a 10x10 grid labeled "A1" to "J10"
                    grid_positions = [f"{chr(row)}{col}" for row in range(65, 75) for col in range(1, 11)]
                    for position in grid_positions:
                        # Assuming ships are placed horizontally (you can expand to other orientations)
                        if self.is_valid_ship_placement(position, ship.length):
                            actions.append(BattleshipAction(ActionType.SET_SHIP, ship.name, [position]))

        elif state.phase == GamePhase.RUNNING:
            # RUNNING Phase: Generate actions to shoot
            # Assuming a 10x10 grid labeled "A1" to "J10"
            grid_positions = [f"{chr(row)}{col}" for row in range(65, 75) for col in range(1, 11)]
            for position in grid_positions:
                if position not in active_player.shots:  # Avoid duplicate shots
                    actions.append(BattleshipAction(ActionType.SHOOT, None, [position]))

        elif state.phase == GamePhase.FINISHED:
            # FINISHED Phase: No actions possible
            pass

        return actions

    def is_valid_ship_placement(self, start_position: str, length: int) -> bool:
        """Check if a ship can be placed starting from the given position."""
        # Example logic to validate ship placement (you can expand this as needed)
        row, col = start_position[0], int(start_position[1:])
        for i in range(length):
            if col + i > 10:  # Ensure it doesn't exceed grid boundaries
                return False
            if f"{row}{col + i}" in self.get_occupied_positions():  # Avoid collisions
                return False
        return True

    def get_occupied_positions(self) -> List[str]:
        """Get all positions occupied by ships."""
        state = self.get_state()
        occupied_positions = []
        for player in state.players:
            for ship in player.ships:
                if ship.location:
                    occupied_positions.extend(ship.location)
        return occupied_positions


def apply_action(self, action: BattleshipAction) -> None:
        """ Apply the given action to the game """
        pass

    def get_player_view(self, idx_player: int) -> BattleshipGameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        pass


class RandomPlayer(Player):

    def select_action(self, state: BattleshipGameState, actions: List[BattleshipAction]) -> Optional[BattleshipAction]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == "__main__":

    game = Battleship()
