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
        """Get a list of possible actions for the active player."""
        actions = []
        player = self.state.players[self.state.idx_player_active]

        if self.state.phase == GamePhase.SETUP:
            # Generate SET_SHIP actions for unset ships directly within this method
            for ship in player.ships:
                if ship.location is None:  # Ship not yet placed
                    alphabet = 'ABCDEFGHIJ'
                    grid = [f"{letter}{number}" for letter in alphabet for number in range(1, 11)]
                    for start in grid:
                        x, y = start[0], int(start[1:])
                        valid_locations = []
                        # Generate horizontal placements
                        if y + ship.length - 1 <= 10:
                            valid_locations.append([f"{x}{y + i}" for i in range(ship.length)])
                        # Generate vertical placements
                        if ord(x) - ord('A') + ship.length <= 10:
                            valid_locations.append([f"{chr(ord(x) + i)}{y}" for i in range(ship.length)])
                        # Add valid placement actions
                        for loc in valid_locations:
                            actions.append(BattleshipAction(ActionType.SET_SHIP, ship.name, loc))

        elif self.state.phase == GamePhase.RUNNING:
            # Generate SHOOT actions for valid grid locations
            alphabet = 'ABCDEFGHIJ'
            grid = [f"{letter}{number}" for letter in alphabet for number in range(1, 11)]
            for loc in grid:
                if loc not in player.shots:  # Avoid locations already targeted
                    actions.append(BattleshipAction(ActionType.SHOOT, None, [loc]))

        return actions

    def apply_action(self, action: BattleshipAction) -> None:
        """ Apply the given action to the game """
        pass

    def get_player_view(self, idx_player: int) -> BattleshipGameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        masked_players = []
        for i, player in enumerate(self.state.players):
            if i == idx_player:
                masked_players.append(player)
            else:
                masked_ships = [Ship(ship.name, ship.length, None) for ship in player.ships]
                masked_players.append(PlayerState(player.name, masked_ships, player.shots, player.successful_shots))
        return BattleshipGameState(
            idx_player_active=self.state.idx_player_active,
            phase=self.state.phase,
            winner=self.state.winner,
            players=masked_players
        )


class RandomPlayer(Player):

    def select_action(self, state: BattleshipGameState, actions: List[BattleshipAction]) -> Optional[BattleshipAction]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == "__main__":

    game = Battleship()
