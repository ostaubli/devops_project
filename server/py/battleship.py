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
        self.state = BattleshipGameState(
            idx_player_active=0,
            phase=GamePhase.SETUP,
            winner=None,
            players=[
                PlayerState(name="Player 1", ships=[], shots=[], successful_shots=[]),
                PlayerState(name="Player 2", ships=[], shots=[], successful_shots=[])
            ]
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
        """ Get the complete, unmasked game state. Returns a copy of current game state to ensure no external modifications affect the internal game state afterwards."""
        if not self.state:
            raise ValueError("Game state not initialized")
        
        # Create new lists to avoid external modification
        players = [
            PlayerState(
                name=player.name,
                ships=[Ship(s.name, s.length, s.location.copy() if s.location else None) 
                      for s in player.ships],
                shots=player.shots.copy(),
                successful_shots=player.successful_shots.copy()
            )
            for player in self.state.players
        ]
        
        # Return new state object with copied data
        return BattleshipGameState(
            idx_player_active=self.state.idx_player_active,
            phase=self.state.phase,
            winner=self.state.winner,
            players=players
        )

    def set_state(self, state: BattleshipGameState) -> None:
        """Set the game state with defensive copying to ensure encapsulation."""
        if not state:
            raise ValueError("Cannot set None state")
        if not isinstance(state, BattleshipGameState):
            raise ValueError("Invalid state type")
        if not state.players or len(state.players) != 2:
            raise ValueError("State must contain exactly 2 players")
            
        # Create defensive copy
        self.state = BattleshipGameState(
            idx_player_active=state.idx_player_active,
            phase=state.phase,
            winner=state.winner,
            players=[
                PlayerState(
                    name=p.name,
                    ships=[Ship(s.name, s.length, s.location.copy() if s.location else None) for s in p.ships],
                    shots=p.shots.copy(),
                    successful_shots=p.successful_shots.copy()
                ) for p in state.players
            ]
        )

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
    
    

