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

    # set of ships and their lengths
    SHIPS_TO_PLACE = [
        ("Carrier", 5), 
        ("Battleship", 4), 
        ("Cruiser", 3), 
        ("Submarine", 3), 
        ("Destroyer", 2)
    ]

    def __init__(self):
        """ Game initialization (set_state call not necessary) """
        # initialize player list and game phase
        self.players = [] 
        self.phase = GamePhase.SETUP

        # create an initial empty game state 
        self.state = BattleshipGameState(
            idx_player_active=0, 
            phase = self. phase, 
            winner=None, 
            players=[])
        
        # create two players and add their initial states
        player1 = PlayerState(name="Player 1", ships=[], shots=[], successful_shots=[])
        player2 = PlayerState(name="Player 2", ships=[], shots=[], successful_shots=[])

        # add players to the game state
        self.state.players.extend([player1, player2])

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
        if self.phase != GamePhase.SETUP:
            # enter here all action why in other GamePhase (e.g. running)
            return []

        # check how many ships the active player has placed
        active_player = self.state.players[self.state.idx_player_active]
        if len(active_player.ships) == len(ships_to_place):
            return []
        
        # Get the next ship to place
        ship_name, ship_length = ships_to_place[len(active_player.ships)]

        # Generate possible placements (horizontal and vertical)
        actions = []
        rows = "ABCDEFGHIJ" 
        columns = [str(i) for i in range(1, 11)]
        
        # Horizontal placements
        for row in rows:  
            for col_start in range(11 - ship_length):  
                location = [f"{row}{int(columns[col_start + i])}" for i in range(ship_length)]
                actions.append(BattleshipAction(action_type=ActionType.SET_SHIP, ship_name=ship_name, location=location))

        # Vertical placements
        for col in columns:
            for row_start in range(11 - ship_length):
                location = [f"{rows[row_start + i]}{col}" for i in range(ship_length)]
                actions.append(BattleshipAction(action_type=ActionType.SET_SHIP, ship_name=ship_name, location=location))

        return actions

    def apply_action(self, action: BattleshipAction) -> None:
        """ Apply the given action to the game """
        active_player = self.state.players[self.state.idx_player_active]
        
        if action.action_type == ActionType.SET_SHIP:
            # Check for overlap
            occupied_cells = set()
            for ship in active_player.ships:
                occupied_cells.update(ship.location)

            # Check if any of the new ship's locations are already occupied
            if any(cell in occupied_cells for cell in action.location):
                print(f"Invalid placement: The ship's location overlaps with an existing ship.")
                return
            
            # Add the new ship to the player's list of ships
            ship = Ship(name=action.ship_name, length=len(action.location), location=action.location)
            active_player.ships.append(ship)
            print(f"{action.ship_name} placed at {action.location}.")

             # Check if the current player has placed all ships
            if len(active_player.ships) == len(Battleship.SHIPS_TO_PLACE):
                # Switch to the next player
                next_player_idx = (self.state.idx_player_active + 1) % len(self.state.players)
                self.state.idx_player_active = next_player_idx
                
                # Check if both players have placed all ships
                if len(self.state.players[0].ships) == len(Battleship.SHIPS_TO_PLACE) and len(self.state.players[1].ships) == len(Battleship.SHIPS_TO_PLACE):
                    self.state.phase = GamePhase.RUNNING
                    print("Both players have placed their ships. Let the shooting begin!!")
                else:
                    print(f"{self.state.players[self.state.idx_player_active].name}'s turn to place ships.")
            else:
                print(f"{active_player.name} has placed {len(active_player.ships)}/{len(Battleship.SHIPS_TO_PLACE)} ships.")

        # Other action types (e.g., shooting) can be handled here in future

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
