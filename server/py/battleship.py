from typing import List, Optional
from enum import Enum
import random
from game import Game, Player


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

    def __repr__(self):
        return (f"BattleshipGameState(active_player={self.idx_player_active}, "
                f"phase={self.phase}, winner={self.winner}, "
                f"players={self.players})")


class Battleship(Game):

    def __init__(self):
        """ Game initialization (set_state call not necessary) """
        self.state = None
        player1 = PlayerState(name='Player 1', ships=[], shots=[], successful_shots=[])
        player2 = PlayerState(name='Player 2', ships=[], shots=[], successful_shots=[])
        
        initial_state = BattleshipGameState(idx_player_active=0,
                                            phase=GamePhase.SETUP,
                                            winner=None,
                                            players=[player1, player2])
        self.state = self.set_state(initial_state)
        

    def print_state(self) -> None:
        """ Print the current game state """
        print(self.state)

    def get_state(self) -> BattleshipGameState:
        """ Get the complete, unmasked game state """
        if not self.state:
            raise ValueError("Game state has not been initialized")
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
