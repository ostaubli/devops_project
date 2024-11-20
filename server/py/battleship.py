from typing import List, Optional
from enum import Enum
import random

if __name__ == "__main__":
    from game import Game, Player
else:
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

    def __init__(self): # Kägi
        """ Game initialization (set_state call not necessary) """
        self.state = BattleshipGameState(idx_player_active = 0, 
                                         phase= GamePhase.SETUP, 
                                         winner = None, 
                                         players = []
        )
        print("Battleship init")
        

    def print_state(self) -> None: # Kägi
        """ Print the current game state """
        print(f"Game Phase: {self.state.phase}")
        print(f"Active Player: {self.state.players}")

    def get_state(self) -> BattleshipGameState: # Kägi
        """ Get the complete, unmasked game state """
        pass

    def set_state(self, state: BattleshipGameState) -> None: # Kägi
        """ Set the game to a given state """
        
        pass

    def get_list_action(self) -> List[BattleshipAction]: # Kened
        """ Get a list of possible actions for the active player """
        pass

    def apply_action(self, action: BattleshipAction) -> None: # Kened
        """ Apply the given action to the game """
        pass

    def get_player_view(self, idx_player: int) -> BattleshipGameState: # Kened
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
    board = [[' ' for _ in range(10)] for _ in range(10)]
    print(board)