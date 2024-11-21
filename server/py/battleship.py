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
    VALID_LOCATIONS = [f"{chr(65 + row)}{col + 1}" for row in range(10) for col in range(10)]
    SHIP_LENGTHS = {
        'carrier': 5,
        'battleship': 4,
        'cruiser': 3,
        'submarine': 3,
        'destroyer': 2
    }

    def __init__(self):
        """ Game initialization (set_state call not necessary) """
        self.board_size = 10
        self.reset()

    def print_state(self) -> None:
        """ Set the game to a given state """
        for idx, board in enumerate(self.boards):
            print(f"Board for Player {idx + 1}:")
            for row in board:
                print(' '.join(row))
            print()

    def get_state(self) -> BattleshipGameState:
        """ Get the complete, unmasked game state """
        return BattleshipGameState(
            idx_player_active=self.idx_player_active,
            phase=self.phase,
            winner=None,
            players=self.players
        )

    def set_state(self, state: BattleshipGameState) -> None:
        """ Print the current game state """
        self.idx_player_active = state.idx_player_active
        self.phase = state.phase
        self.players = state.players

    def reset(self) -> None:
        """ Reset the game to its initial state """
        self.phase = GamePhase.SETUP
        self.players = [
            PlayerState(name="Player 1", ships=[], shots=[], successful_shots=[]),
            PlayerState(name="Player 2", ships=[], shots=[], successful_shots=[])
        ]
        self.boards = [
            [['~' for _ in range(self.board_size)] for _ in range(self.board_size)],
            [['~' for _ in range(self.board_size)] for _ in range(self.board_size)]
        ]
        self.idx_player_active = 0

    def get_list_action(self) -> List[BattleshipAction]:
        """ Get a list of possible actions for the active player """
        actions = []

        if self.phase == GamePhase.SETUP:
            # Ensure each player has 5 ships to place
            current_player = self.players[self.idx_player_active]
            placed_ship_names = [ship.name for ship in current_player.ships]

            for ship_name in self.SHIP_LENGTHS.keys():
                if ship_name not in placed_ship_names:
                    length = self.SHIP_LENGTHS[ship_name]

                    valid_placement = False
                    while not valid_placement:
                        direction = random.choice(['horizontal', 'vertical'])
                        if direction == 'horizontal':
                            start_row = random.randint(0, self.board_size - 1)
                            start_col = random.randint(0, self.board_size - length)
                            location = [f"{chr(65 + start_row)}{col + 1}" for col in
                                        range(start_col, start_col + length)]
                        else:
                            start_col = random.randint(0, self.board_size - 1)
                            start_row = random.randint(0, self.board_size - length)
                            location = [f"{chr(65 + start_row + i)}{start_col + 1}" for i in range(length)]

                        # Check if all the proposed locations are available
                        valid_placement = all(
                            self.boards[self.idx_player_active][self.convert_location(loc)[0]][
                                self.convert_location(loc)[1]] == '~'
                            for loc in location
                        )

                    actions.append(
                        BattleshipAction(action_type=ActionType.SET_SHIP, ship_name=ship_name, location=location))
                    break  # Only add one ship action at a time

        elif self.phase == GamePhase.RUNNING:
            # Generate shoot actions for all cells that have not been shot at
            target_player_idx = 1 - self.idx_player_active
            target_board = self.boards[target_player_idx]

            # Iterate through all valid locations to ensure none are missed
            for loc in self.VALID_LOCATIONS:
                x, y = self.convert_location(loc)
                if target_board[x][y] == '~':  # Only add locations that have not been shot at
                    actions.append(BattleshipAction(action_type=ActionType.SHOOT, ship_name=None, location=[loc]))

            # Debugging information to verify shoot locations
            available_shoot_locations = {loc for loc in self.VALID_LOCATIONS if
                                         target_board[self.convert_location(loc)[0]][
                                             self.convert_location(loc)[1]] == '~'}
            print(f"Available shoot locations generated by get_list_action: {available_shoot_locations}")
            print(f"Expected valid locations: {set(self.VALID_LOCATIONS)}")

        return actions

    def apply_action(self, action: BattleshipAction) -> None:
        """ Apply the given action to the game """
        if action.action_type == ActionType.SET_SHIP:
            # Set ship action
            player = self.players[self.idx_player_active]
            ship = Ship(name=action.ship_name, length=len(action.location), location=action.location)
            player.ships.append(ship)

            # Update the current player's board with the new ship
            for loc in action.location:
                x, y = self.convert_location(loc)
                if self.boards[self.idx_player_active][x][y] != '~':
                    raise ValueError(f"Invalid ship placement at location {loc}: Location already occupied.")
                self.boards[self.idx_player_active][x][y] = ship.name[
                    0]  # Mark the ship location with its name's first letter

            # Switch to the next player if ship placement is done
            self.idx_player_active = 1 - self.idx_player_active

            # If both players have placed all their ships, move to the RUNNING phase
            if all(len(player.ships) == 5 for player in self.players):
                self.phase = GamePhase.RUNNING

        elif action.action_type == ActionType.SHOOT:
            # Shoot action
            target_player_idx = 1 - self.idx_player_active
            target_board = self.boards[target_player_idx]
            target_location = action.location[0]
            x, y = self.convert_location(target_location)

            # Update the target player's board based on whether it is a hit or miss
            if target_board[x][y] != '~':  # Hit
                self.players[self.idx_player_active].successful_shots.append(target_location)
                target_board[x][y] = 'X'  # Mark hit
            else:  # Miss
                target_board[x][y] = 'O'  # Mark miss

            # Record the shot in the current player's shots list
            self.players[self.idx_player_active].shots.append(target_location)

            # Switch to the next player after shooting
            self.idx_player_active = target_player_idx

            # Check if all ships of the opponent are sunk
            all_ships_sunk = all(
                all(target_board[self.convert_location(loc)[0]][self.convert_location(loc)[1]] == 'X'
                    for loc in ship.location)
                for ship in self.players[target_player_idx].ships if ship.location is not None
            )
            if all_ships_sunk:
                self.phase = GamePhase.FINISHED
                self.winner = self.idx_player_active

    def convert_location(self, loc: str) -> tuple:
        """ Convert a location like 'D4' to board coordinates (row, column) """
        row = ord(loc[0].upper()) - ord('A')
        col = int(loc[1:]) - 1
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            raise ValueError(f"Invalid location {loc}: Out of board bounds.")
        return row, col

    def get_player_view(self, idx_player: int) -> BattleshipGameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        player_view = self.get_state()
        opponent_idx = 1 - idx_player
        for ship in self.players[opponent_idx].ships:
            ship.location = None
        return player_view


class RandomPlayer(Player):

    def select_action(self, state: BattleshipGameState, actions: List[BattleshipAction]) -> Optional[BattleshipAction]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == "__main__":

    game = Battleship()

    while game.phase != GamePhase.FINISHED:
        game.print_state()
        actions = game.get_list_action()
        if actions:
            print("Available actions:")
            for idx, action in enumerate(actions):
                print(f"{idx}: {action.action_type} - {action.ship_name if action.ship_name else ''} at {action.location}")

            # Frage nach der nächsten Aktion
            selected_action_index = int(input("Choose an action by index: "))
            selected_action = actions[selected_action_index]
            game.apply_action(selected_action)
        else:
            print("No available actions, switching to the next player.")
            game.idx_player_active = 1 - game.idx_player_active

    game.print_state()
    print(f"The winner is: Player {game.idx_player_active + 1}")