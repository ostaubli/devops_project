from typing import List, Optional
from enum import Enum
import random

from fontTools.feaLib import location
from mypy.dmypy.client import action

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
    counter = 0 #for counting our rounds
    location = ["A1", "A2", "A3", "A4", "A5","A6","A7","A8","A9","A10",
                "B1", "B2", "B3", "B4", "B5","B6","B7","B8","B9","B10",
                "C1", "C2", "C3", "C4", "C5","C6","C7","C8","C9","C10",
                "D1", "D2", "D3", "D4", "D5","D6","D7","D8","D9","D10",
                "E1", "E2", "E3", "E4", "E5","E6","E7","E8","E9","E10",
                "F1", "F2", "F3", "F4", "F5","F6","F7","F8","F9","F10",
                "G1", "G2", "G3", "G4", "G5","G6","G7","G8","G9","G10",
                "H1", "H2", "H3", "H4", "H5","H6","H7","H8","H9","H10",
                "I1", "I2", "I3", "I4", "I5","I6","I7","I8","I9","I10",
                "J1", "J2", "J3", "J4", "J5","J6","J7","J8","J9","J10"]

    def __init__(self): # Kägi
        """ Game initialization (set_state call not necessary) """
        """ships = [Ship(name= "Carrier", length=5, location=None), #, location=["A1","A2","A3","A4","A5"]
                Ship(name= "Battleship", length=4, location=None),
                Ship(name= "Cruiser", length=3, location=None),
                Ship(name= "Submarine", length=3, location=None),
                Ship(name= "Destroyer", length=2, location=None)
                 ]
        """
        player1 = PlayerState(name = "Player1", ships=[], shots = [], successful_shots=[])
        player2 = PlayerState(name = "Player2", ships=[], shots = [], successful_shots=[])

        self.state = BattleshipGameState(idx_player_active = 0, 
                                         phase= GamePhase.SETUP, 
                                         winner = None, 
                                         players = [player1,player2]
        )
        

    def print_state(self) -> None: # Kägi
        """ Print the current game state """
        print(f"Game Phase: {self.state.phase}")
        print(f"Active Player: {self.state.players}")

    def get_state(self) -> BattleshipGameState: # Kägi
        return self.state

    def set_state(self, state: BattleshipGameState) -> None: # Kägi
        """ Set the game to a given state """
        self.state = state




    def get_list_action(self) -> List[BattleshipAction]: # Kened
        """ Get a list of possible actions for the active player """
        list_action = []



        if self.counter <= 9:   #unfinished
            return list_action
            #ship_name, location, actiontype set ship


        else:   #finished
            for loc in self.location:
                if loc not in self.state.players[self.state.idx_player_active].shots:
                    list_action.append(BattleshipAction(action_type= ActionType.SHOOT,ship_name=None, location = loc))
            return list_action






    def apply_action(self, action: BattleshipAction) -> None:# Kened
        """ Apply the given action to the game """

        if action.action_type.value == ActionType.SET_SHIP:
            self.state.players[self.state.idx_player_active].ships.append(Ship(name=action.ship_name,
                                                                               length=len(action.location),
                                                                               location=action.location))
        else:
            self.state.players[self.state.idx_player_active].shots.append(action.location[0])

        self.state.idx_player_active = (self.state.idx_player_active + 1)%2
        self.counter = self.counter + 1



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