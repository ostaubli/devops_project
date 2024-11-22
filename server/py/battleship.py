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
        # just setting players to 2 is not working. Players need to be initialized as well with their parameters
        # from class PlayerState.
        self.state = BattleshipGameState(
            idx_player_active=0,
            phase=GamePhase.SETUP,
            winner=None,
            players=[
                PlayerState("Player 1", [], [], []),
                PlayerState("Player 2", [], [], [])
            ])

    def print_state(self) -> None:
        """ Set the game to a given state """
        print(self.state)

    def get_state(self) -> BattleshipGameState:
        """ Get the complete, unmasked game state """
        return self.state

    def set_state(self, state: BattleshipGameState) -> None:
        """ Print the current game state """
        self.state = state

    def get_list_action(self) -> List[BattleshipAction]:
        """ Get a list of possible actions for the active player """
        actions: List[BattleshipAction] = []
        
        active_player_idx = self.state.idx_player_active
        active_player = self.state.players[active_player_idx]

        def is_valid_ship_placement(self, locations: List[str], existing_ship_locations: List[str]) -> bool:
            """
            Validate that the proposed locations:
            - Do not overlap with any existing ship.
            - Do not touch (including diagonals) any existing ship.
            """
            # Create a set of all occupied cells, including adjacent cells
            occupied_cells = set()
            for loc in existing_ship_locations:
                row, col = ord(loc[0]), int(loc[1:])
                # Add the cell and its surrounding cells
                for r in range(row - 1, row + 2):
                    for c in range(col - 1, col + 2):
                        occupied_cells.add(f"{chr(r)}{c}")

            # Check if any of the proposed locations overlap or touch existing ships
            for loc in locations:
                if loc in occupied_cells:
                    return False

            return True

        if self.state.phase == GamePhase.SETUP:
            # Generate ship placement actions
            for ship in active_player.ships:
                if not ship.location:
                    board_size = 10
                    # Collect all existing ship locations
                    existing_ship_locations = [
                        loc for other_ship in active_player.ships if other_ship.location for loc in other_ship.location
                    ]
                    for row in range(board_size):
                        for col in range(board_size):
                            # Generate all possible horizontal and vertical placements
                            if col + ship.length <= board_size:
                                # Horizontal placement
                                locations = [f"{chr(65 + row)}{c + 1}" for c in range(col, col + ship.length)]
                                if self.is_valid_ship_placement(locations, existing_ship_locations):
                                    actions.append(BattleshipAction(ActionType.SET_SHIP, ship.name, locations))
                            if row + ship.length <= board_size:
                                # Vertical placement
                                locations = [f"{chr(65 + r)}{col + 1}" for r in range(row, row + ship.length)]
                                if self.is_valid_ship_placement(locations, existing_ship_locations):
                                    actions.append(BattleshipAction(ActionType.SET_SHIP, ship.name, locations))


        elif self.state.phase == GamePhase.RUNNING:
            # Generate shooting actions
            board_size = 10
            for row in range(board_size):
                for col in range(board_size):
                    location = f"{chr(65 + row)}{col + 1}"
                    if location not in active_player.shots:
                        actions.append(BattleshipAction(ActionType.SHOOT, None, [location]))

        return actions

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
    Player1 = RandomPlayer()
    Player2 = RandomPlayer()

    while game.get_state().phase != GamePhase.FINISHED:
        state = game.get_player_view(game.get_state().idx_player_active)
        actions = game.get_list_action()
        action = Player1.select_action(state, actions) if state.idx_player_active == 0 else Player2.select_action(state, actions)
        if action:
            game.apply_action(action)
        game.print_state()

    print("\nGame Over!")
    winner = game.get_state().winner
    if winner is not None:
        print(f"Winner: {game.get_state().players[winner].name}")