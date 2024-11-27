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
        # Define the ships for each player
        ships = [
            Ship("Carrier", 5, None),
            Ship("Battleship", 4, None),
            Ship("Cruiser", 3, None),
            Ship("Submarine", 3, None),
            Ship("Destroyer", 2, None)
        ]

        # Initialize players with empty shots and successful shots
        players = [
            PlayerState("Player 1", ships=[Ship(ship.name, ship.length, None) for ship in ships], shots=[],
                        successful_shots=[]),
            PlayerState("Player 2", ships=[Ship(ship.name, ship.length, None) for ship in ships], shots=[],
                        successful_shots=[])
        ]

        # Initialize the game state
        self.state = BattleshipGameState(
            idx_player_active=0,
            phase=GamePhase.SETUP,
            winner=None,
            players=players
        )

    def print_state(self) -> None:
        """ Print the current game state """
        for player in self.state.players:
            print(f"{player.name}'s ships:")
            for ship in player.ships:
                print(f"  {ship.name}: {ship.location}")
            print(f"Shots taken: {player.shots}")
            print(f"Successful shots: {player.successful_shots}")
        print(f"Current phase: {self.state.phase}")
        if self.state.winner is not None:
            print(f"Winner: Player {self.state.winner + 1}")

    def get_state(self) -> BattleshipGameState:
        """ Get the complete, unmasked game state """
        return self.state

    def set_state(self, state: BattleshipGameState) -> None:
        """ Set the game to a given state """
        self.state = state

    def get_list_action(self) -> List[BattleshipAction]:
        """ Get a list of possible actions for the active player """
        pass

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
