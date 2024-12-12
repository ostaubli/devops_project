"""
Dog game implementation module.
This module contains the core game logic and data structures for the Dog card game.
"""

# runcmd: cd ../.. & venv\Scripts\python server/py/dog_template.py
import random
from enum import Enum
from typing import List, Optional, ClassVar
from pydantic import BaseModel
from server.py.game import Game, Player


class Card(BaseModel):
    """Represents the card charcteristics"""
    suit: str  # card suit (color)
    rank: str  # card rank


class Marble(BaseModel):
    """Represents the marble information"""
    pos: int       # position on board (0 to 95) --> Changed from str to int
    is_save: bool  # true if marble was moved out of kennel and was not yet moved


class PlayerState(BaseModel):
    """Represents the playerstate information"""
    name: str                  # name of player
    list_card: List[Card]      # list of cards
    list_marble: List[Marble]  # list of marbles


class Action(BaseModel):
    """Represents the action information"""
    card: Card                 # card to play
    pos_from: Optional[int]    # position to move the marble from
    pos_to: Optional[int]      # position to move the marble to
    card_swap: Optional[Card] = None  # optional card to swap (default is None)


class GamePhase(str, Enum):
    """Defines the possible game phases """
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class GameState(BaseModel):
    """Defines the game state characteristics """

    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']  # 4 suits (colors)
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10',      # 13 ranks + Joker
        'J', 'Q', 'K', 'A', 'JKR'
    ]
    LIST_CARD: ClassVar[List[Card]] = [
        # 2: Move 2 spots forward
        Card(suit='♠', rank='2'), Card(suit='♥', rank='2'), Card(suit='♦', rank='2'), Card(suit='♣', rank='2'),
        # 3: Move 3 spots forward
        Card(suit='♠', rank='3'), Card(suit='♥', rank='3'), Card(suit='♦', rank='3'), Card(suit='♣', rank='3'),
        # 4: Move 4 spots forward or back
        Card(suit='♠', rank='4'), Card(suit='♥', rank='4'), Card(suit='♦', rank='4'), Card(suit='♣', rank='4'),
        # 5: Move 5 spots forward
        Card(suit='♠', rank='5'), Card(suit='♥', rank='5'), Card(suit='♦', rank='5'), Card(suit='♣', rank='5'),
        # 6: Move 6 spots forward
        Card(suit='♠', rank='6'), Card(suit='♥', rank='6'), Card(suit='♦', rank='6'), Card(suit='♣', rank='6'),
        # 7: Move 7 single steps forward
        Card(suit='♠', rank='7'), Card(suit='♥', rank='7'), Card(suit='♦', rank='7'), Card(suit='♣', rank='7'),
        # 8: Move 8 spots forward
        Card(suit='♠', rank='8'), Card(suit='♥', rank='8'), Card(suit='♦', rank='8'), Card(suit='♣', rank='8'),
        # 9: Move 9 spots forward
        Card(suit='♠', rank='9'), Card(suit='♥', rank='9'), Card(suit='♦', rank='9'), Card(suit='♣', rank='9'),
        # 10: Move 10 spots forward
        Card(suit='♠', rank='10'), Card(suit='♥', rank='10'), Card(suit='♦', rank='10'), Card(suit='♣', rank='10'),
        # Jake: A marble must be exchanged
        Card(suit='♠', rank='J'), Card(suit='♥', rank='J'), Card(suit='♦', rank='J'), Card(suit='♣', rank='J'),
        # Queen: Move 12 spots forward
        Card(suit='♠', rank='Q'), Card(suit='♥', rank='Q'), Card(suit='♦', rank='Q'), Card(suit='♣', rank='Q'),
        # King: Start or move 13 spots forward
        Card(suit='♠', rank='K'), Card(suit='♥', rank='K'), Card(suit='♦', rank='K'), Card(suit='♣', rank='K'),
        # Ass: Start or move 1 or 11 spots forward
        Card(suit='♠', rank='A'), Card(suit='♥', rank='A'), Card(suit='♦', rank='A'), Card(suit='♣', rank='A'),
        # Joker: Use as any other card you want
        Card(suit='', rank='JKR'), Card(suit='', rank='JKR'), Card(suit='', rank='JKR')
    ] * 2

    cnt_player: int = 4                # number of players (must be 4)
    phase: GamePhase                   # current phase of the game
    cnt_round: int                     # current round
    bool_card_exchanged: bool          # true if cards was exchanged in round
    idx_player_started: int            # index of player that started the round
    idx_player_active: int             # index of active player in round
    list_player: List[PlayerState]     # list of players
    list_card_draw: List[Card]         # list of cards to draw
    list_card_discard: List[Card]      # list of cards discarded
    card_active: Optional[Card]        # active card (for 7 and JKR with sequence of actions)
    bool_game_finished: bool
    board_positions: List[Optional[int]]

class Dog(Game):
    """
    Dog board game implementation.

    Constants define board layout, card values, and game rules.
    """

    # Constants
    BOARD_SIZE = 96
    STARTING_CARDS = {'A', 'K', 'JKR'}
    MOVEMENT_CARDS = {'2', '3', '4', '5', '6', '8', '9', '10', 'Q', 'K', 'A', 'JKR'}
    SAFE_SPACES = {
        0: [68, 69, 70, 71],  # Player 1's safe spaces, blue
        1: [76, 77, 78, 79],  # Player 2's safe spaces, green
        2: [84, 85, 86, 87],  # Player 3's safe spaces, red
        3: [92, 93, 94, 95]   # Player 4's safe spaces, yellow
        }
    KENNEL_POSITIONS = {
        0: [64, 65, 66, 67],  # Player 1's kennel positions
        1: [72, 73, 74, 75],  # Player 2's kennel positions
        2: [80, 81, 82, 83],  # Player 3's kennel positions
        3: [88, 89, 90, 91]   # Player 4's kennel positions
    }
    START_POSITIONS = {
        0: 0,    # Player 1
        1: 16,   # Player 2
        2: 32,   # Player 3
        3: 48    # Player 4
    }
    CARD_VALUES = {
        'A': [1, 11],
        'Q': [12],
        'K': [13],
        'JKR': [-4] + list(range(1, 14)),  # Joker can take on any value
        '4': [-4, 4],
        '7': [7]
    }

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """
        self.state: Optional[GameState] = None
        self.initialize_game()  # Ensure the game state is initialized

    def initialize_game(self) -> None:
        """
        Initialize the game state with players, deck, and board positions.

        Each player (i: range 0-3) has 4 marbles (j: range 0-3), initialized from unique positions (pos).
        """

        # Initialize players with empty card hands and marbles in their kennel positions
        players = [
            PlayerState(
                name=f"Player {i+1}",
                list_card=[],
                list_marble=[
                    Marble(pos=self.KENNEL_POSITIONS[i][j], is_save=True) for j in range(4)
                ]
            )
            for i in range(4)
        ]

        #prepare deck
        deck = GameState.LIST_CARD.copy()
        random.shuffle(deck)

        idx_player_started = random.randint(0, 3)

        self.state = GameState(
                        cnt_player=4,
                        phase=GamePhase.RUNNING,
                        cnt_round=1,
                        bool_game_finished=False,
                        bool_card_exchanged=False,
                        idx_player_started=idx_player_started,
                        idx_player_active=idx_player_started,
                        list_player=players,
                        list_card_draw=deck,
                        list_card_discard=[],
                        card_active=None,
                        board_positions=[None] * 96  # Initialize board positions
                    )

        # Deal initial cards (6 cards in first round)
        self.deal_cards()

        #print("Game initialized. Cards have been dealt.")


    def reset(self) -> None:
        """ Reset the game to its initial state """
        self.initialize_game()

    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        if not isinstance(state, GameState):
            raise ValueError("Invalid state object provided.")
        self.state = state

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        if not self.state:
            raise ValueError("Game state is not set.")
        return self.state

    def print_state(self) -> None:
        """ Print the current game state """
        if self.state is None:
            raise ValueError("Game state is not set.")
        print(f"Game Phase: {self.state.phase}")
        print(f"Round: {self.state.cnt_round}")
        print(f"Active Player: {self.state.list_player[self.state.idx_player_active].name}")
        for player_idx, player in enumerate(self.state.list_player):
            print(f"\nPlayer {player_idx + 1}: {player.name}")

            # Check for empty or invalid card lists
            if not player.list_card:
                print("Warning: No cards in player's hand.")
            else:
                print(f"Cards: {[f'{card.rank} of {card.suit}' for card in player.list_card]}")

            # Ensure marbles list is valid
            if not player.list_marble:
                print("Warning: No marbles for the player.")
            else:
                print(f'''Marbles: {[f'Position: {m.pos}, Safe: {m.is_save}' for m in player.list_marble]}''')


    def draw_board(self) -> None:
        """ Draw the board with kennels as the starting positions and safe spaces as the final destinations """
        if self.state is None:
            raise ValueError("Game state is not set.")

        board = ["." for _ in range(self.BOARD_SIZE)]

        for player_idx, player in enumerate(self.state.list_player):
            for marble in player.list_marble:
                if marble.pos in self.SAFE_SPACES[player_idx]:
                    board[marble.pos] = f"S{player_idx+1}"
                elif marble.pos in self.KENNEL_POSITIONS[player_idx]:
                    board[marble.pos] = f"K{player_idx+1}"
                else:
                    board[marble.pos] = f"M{player_idx+1}"

        print("Board:")
        for i in range(0, self.BOARD_SIZE, 12):
            print(" ".join(board[i:i+12]))

    def _get_card_value(self, card: Card) -> List[int]:
        """Map card rank to its movement values using CARD_VALUES and handle numeric ranks."""
        # Check if the card is in the predefined CARD_VALUES dictionary
        if card.rank in self.CARD_VALUES:
            return self.CARD_VALUES[card.rank]
        # Dynamically handle numeric ranks (excluding 4 and 7, as they are special cases)
        if card.rank.isdigit():
            return [int(card.rank)]
        # Default to [0] for invalid cards
        return [0]

    def _calculate_new_position(self, marble: Marble, move_value: int, player_idx: int) -> Optional[int]:
        """
        Calculate the new position of a marble, considering:
        - Safe space entry rules for each player
        - Blocking due to marbles
        - Blockage at starting positions when occupied by a marble of the corresponding player.
        Returns None if the move is invalid.
        """

        def _is_safe_space_blocked(new_pos: Optional[int],
                                safe_spaces: list,
                                blocked_positions: set, marbles: list) -> bool:
            """Check if the target safe space is blocked or overtaking occurs."""
            if new_pos in blocked_positions:
                return True
            for other_marble in marbles:
                if other_marble.pos in safe_spaces and current_pos < other_marble.pos <= new_pos:
                    return True
            return False

        def _is_start_blocked(temp_pos: int, current_pos: int, starting_points: dict) -> bool:
            """Check if crossing any player's starting position is blocked."""
            for player_idx_loop, start_pos in starting_points.items():
                if current_pos < start_pos <= temp_pos and self.state:
                    marbles_at_start = self.state.list_player[player_idx_loop].list_marble
                    if any(marble.pos == start_pos and marble.is_save for marble in marbles_at_start):
                        return True
            return False

        safe_spaces = self.SAFE_SPACES[player_idx]
        start_pos = self.START_POSITIONS[player_idx]
        current_pos = marble.pos
        temp_pos = (current_pos + move_value) % 64  # Board size for the main track

        blocked_positions = {m["position"] for m in self.get_all_marbles()}

        if not self.state:
            raise ValueError("Game state is not set.")

        player_marbles = self.state.list_player[player_idx].list_marble

        # Case 1: Movement within safe space
        if current_pos in safe_spaces:
            new_pos = current_pos + move_value
            if (new_pos <= safe_spaces[-1] and not
                _is_safe_space_blocked(new_pos, safe_spaces, blocked_positions, player_marbles)):
                return new_pos
            return None

        # Case 2: General movement on the track
        if _is_start_blocked(temp_pos, current_pos, self.START_POSITIONS):
            return None

        # Case 3: Entering the safe space
        if current_pos <= start_pos <= temp_pos and not marble.is_save:
            steps_into_safe_space = temp_pos - start_pos
            if steps_into_safe_space < len(safe_spaces):
                target_safe_space = safe_spaces[steps_into_safe_space]
                if not _is_safe_space_blocked(target_safe_space, safe_spaces, blocked_positions, player_marbles):
                    return target_safe_space
            return None

        # Default case: Valid position on the main track
        return temp_pos if temp_pos <= self.BOARD_SIZE else None





    def validate_total_cards(self) -> None:
        """Ensure the total number of cards remains consistent."""
        if not self.state:
            raise ValueError("Game state is not set.")

        draw_count = len(self.state.list_card_draw)
        discard_count = len(self.state.list_card_discard)
        player_card_count = sum(len(player.list_card) for player in self.state.list_player)

        total_cards = draw_count + discard_count + player_card_count

        print(f'''Debug: Draw pile count: {draw_count},
            Discard pile count: {discard_count},
            Player cards: {player_card_count}''')
        print(f'''Debug: Total cards: {total_cards},
            Expected: {len(GameState.LIST_CARD)}''')

        if total_cards != len(GameState.LIST_CARD):
            raise ValueError(f"Total cards mismatch: {total_cards} != {len(GameState.LIST_CARD)}")

    def get_all_marbles(self) -> List[dict]:
        """Retrieve a list of all marbles with their positions, is_save status, and player index."""
        if not self.state:
            raise ValueError("Game state is not set.")

        all_marbles = []
        for player_idx, player in enumerate(self.state.list_player):  # Include the player's index
            for marble in player.list_marble:
                all_marbles.append({
                    "player": player.name,
                    "player_idx": player_idx,  # Add the player index here
                    "position": marble.pos,
                    "is_save": marble.is_save
                })
        return all_marbles

    def _handle_seven_card(self, card: Card, active_marbles: List[Marble]) -> List[Action]:
        """Generate all possible split actions for the `7` card."""

        if not self.state:
            raise ValueError("Game state is not set.")

        player_idx = self.state.idx_player_active
        kennels = self.KENNEL_POSITIONS

        # Filter out marbles in the kennel
        marbles_outside_kennel = [
            marble for marble in active_marbles if marble.pos not in kennels[player_idx]
        ]

        if not marbles_outside_kennel:
            return []  # No valid moves if all marbles are in the kennel

        def dfs(remaining: int,
                moves: List[int],
                marble_indices: List[int],
                results: List[List[tuple[int, int]]]) -> None:
            """Recursive helper to generate splits."""
            if remaining == 0:
                # Check if all moves in the split are valid and use exactly 7 points
                if sum(moves) == 7:  # Ensure the full 7 points are used
                    valid_split = True
                    for i, steps in enumerate(moves):
                        if steps > 0:  # Check only marbles with non-zero moves
                            marble = marbles_outside_kennel[marble_indices[i]]
                            pos_to: Optional[int] = self._calculate_new_position(marble, steps, player_idx)
                            if pos_to is None:
                                valid_split = False  # Invalidate the entire split if one move fails
                                break

                    # If valid, append the current split result
                    if valid_split:
                        results.append([(marble_indices[i], moves[i]) for i in range(len(moves)) if moves[i] > 0])
                return

            for i, _ in enumerate(moves):
                # Tentatively add 1 step to the current marble's move
                moves[i] += 1

                # Validate the move using `_calculate_new_position`
                temp_pos_to = self._calculate_new_position(marbles_outside_kennel[marble_indices[i]],
                                                        moves[i],
                                                        player_idx)
                if temp_pos_to is not None:
                    dfs(remaining - 1, moves, marble_indices, results)

                # Backtrack (remove the step)
                moves[i] -= 1

        # Generate all valid splits
        marble_indices = list(range(len(marbles_outside_kennel)))
        results: List[List[tuple[int, int]]] = []  # Type annotation fix
        dfs(7, [0] * len(marbles_outside_kennel), marble_indices, results)

        # Convert valid splits into actions
        actions_list = []
        for split in results:
            for marble_idx, steps in split:
                marble = marbles_outside_kennel[marble_idx]
                pos_to = self._calculate_new_position(marble, steps, player_idx)
                if pos_to is not None:
                    actions_list.append(Action(
                        card=card,
                        pos_from=marble.pos,
                        pos_to=pos_to,
                        card_swap=None
                    ))
        return actions_list


    # def get_list_action(self) -> List[Action]:
    #     """Get list of possible actions for active player"""
    #     if not self.state:
    #         return []

    #     actions_list = []
    #     active_player = self.state.list_player[self.state.idx_player_active]
    #     current_cards = active_player.list_card  # cards of current player


    #     # Card exchange logic during the setup phase
    #     if self.state.bool_card_exchanged is False:
    #         # Generate actions_list for the active player to exchange a card
    #         for card in active_player.list_card:
    #             # pos_from and pos_to not applicable
    #             actions_list.append(Action(card=card, pos_from=None, pos_to=None, card_swap=None))
    #         return actions_list


    #     active_marbles = active_player.list_marble  # marbels of current player
    #     all_marbles = self.get_all_marbles() #marbel information of all players

    #     # Safe Spaces, Kennel and Startposition for all players
    #     kennels = self.KENNEL_POSITIONS
    #     safe_spaces = self.SAFE_SPACES
    #     start_positions = self.START_POSITIONS

    #     player_idx = self.state.idx_player_active
    #     player_kennel = kennels[player_idx]
    #     player_start_position = start_positions[player_idx]

    #     # checks, if and how many marbels are in the kennel
    #     marbles_in_kennel = [marble for marble in active_marbles if marble.pos in player_kennel]
    #     num_in_kennel = len(marbles_in_kennel)

    #     # Iterate through cards and determine possible actions_list
    #     for card in current_cards:
    #         card_values = self._get_card_value(card)  # Get the list of possible values for the card

    #         # Check for starting moves & Ensure the starting position is free of the active player's own marbles
    #         if num_in_kennel > 0 and not any(marble.pos == player_start_position for marble in active_marbles):
    #             # Only `A`, `K`, `JKR` can perform starting moves
    #             if card.rank in self.STARTING_CARDS:
    #                 actions_list.append(Action(
    #                     card=card,
    #                     pos_from=marbles_in_kennel[0].pos,  # Take one marble from the kennel
    #                     pos_to=player_start_position,       # Move to the starting position
    #                     card_swap=None
    #                 ))

    #         # Handle `7` or 'JKR' as 7: split moves
    #             if card.rank in ('7', 'JKR'):
    #                 actions_list.extend(self._handle_seven_card(card, active_marbles))
    #                 continue

    #         # Check for other moves (only for marbles outside the kennel)
    #         for marble in active_marbles:
    #             if marble.pos in player_kennel:  # Skip marbles in the kennel
    #                 continue

    #             # Handle MARBEL SWAPPING with `J` or `JKR`: exchange with opponent's marble
    #             if card.rank in ('7', 'JKR'):
    #                 if marble.is_save is False:  # Active player's marble must not be in save state
    #                     for target in all_marbles:
    #                         # Skip if the target marble belongs to the active player
    #                         if target["player_idx"] == self.state.idx_player_active:
    #                             continue

    #                         # Check if the opponent's marble is ineligible
    #                         target_position = target["position"]

    #                         # Exclude marbles in safe spaces, kennels, start positions, or marked as safe
    #                         if (target_position in safe_spaces[target["player_idx"]] or
    #                             target_position in kennels[target["player_idx"]] or
    #                             target_position == start_positions[target["player_idx"]] or
    #                             target["is_save"]):  # Opponent's marble marked as safe
    #                             continue

    #                         # Add a valid swap action
    #                         actions_list.append(Action(
    #                             card=card,
    #                             pos_from=marble.pos,        # Active player's marble position
    #                             pos_to=target_position,    # Opponent marble position
    #                             card_swap=None
    #                         ))


    #             # all cases with cards
    #             # Iterate over all possible values of the card, #check if we can move this far!!
    #             for card_value in card_values:
    #                 pos_to = self._calculate_new_position(marble, card_value, self.state.idx_player_active)
    #                 if pos_to is None:
    #                     continue
    #                 actions_list.append(Action(
    #                     card=card,
    #                     pos_from=marble.pos,
    #                     pos_to=pos_to,
    #                     card_swap=None
    #                 ))

    #     return actions_list
    def get_list_action(self) -> List[Action]:
        """Generate a list of possible actions for the active player based on the current game state."""
        if not self.state:
            return []

        active_player = self.state.list_player[self.state.idx_player_active]
        current_cards = active_player.list_card  # Cards of the current player
        actions_list = []

        # If card exchange phase not completed, generate actions for exchanging cards
        if self._is_card_exchange_phase():
            return self._get_exchange_actions(active_player)

        # After exchange phase, normal gameplay actions:
        all_marbles = self.get_all_marbles()
        player_idx = self.state.idx_player_active
        player_kennel = self.KENNEL_POSITIONS[player_idx]
        player_start_position = self.START_POSITIONS[player_idx]

        # Determine how many marbles are in kennel
        marbles_in_kennel = [m for m in active_player.list_marble if m.pos in player_kennel]
        num_in_kennel = len(marbles_in_kennel)

        # Generate actions for each card
        for card in current_cards:
            card_values = self._get_card_value(card)

            # If there are marbles in the kennel, try starting moves (A, K, JKR)
            if num_in_kennel > 0:
                actions_list.extend(
                    self._get_starting_actions(card, marbles_in_kennel, active_player, player_start_position)
                )

                # If card is '7' or 'JKR' (which can act like 7), handle the special "split move"
                if card.rank in ('7', 'JKR'):
                    actions_list.extend(self._handle_seven_card(card, active_player.list_marble))
                    # After handling special moves for '7' or 'JKR', continue to next card
                    continue

            # For marbles outside the kennel, handle swaps and normal moves
            actions_list.extend(
                self._get_swap_actions(card, active_player.list_marble, all_marbles)
            )
            actions_list.extend(
                self._get_normal_move_actions(card, card_values, active_player.list_marble, player_idx)
            )

        return actions_list

    def _is_card_exchange_phase(self) -> bool:
        """Check if the card exchange phase is still ongoing."""
        assert self.state is not None
        return self.state.bool_card_exchanged is False

    def _get_exchange_actions(self, active_player: PlayerState) -> List[Action]:
        """Generate actions that represent exchanging a card during the initial phase."""
        return [
            Action(card=card, pos_from=None, pos_to=None, card_swap=None)
            for card in active_player.list_card
        ]

    def _get_starting_actions(self, card: Card , marbles_in_kennel: List,
                            active_player: PlayerState, player_start_position: int) -> List[Action]:
        """Generate starting move actions if conditions allow bringing a marble out of kennel."""
        actions = []
        # Only start if start position is free of the player's own marbles and card allows starting moves
        if (card.rank in self.STARTING_CARDS and
            not any(marble.pos == player_start_position for marble in active_player.list_marble)):
            actions.append(
                Action(
                    card=card,
                    pos_from=marbles_in_kennel[0].pos,
                    pos_to=player_start_position,
                    card_swap=None
                )
            )
        return actions

    def _get_swap_actions(self, card: Card, active_marbles: List, all_marbles: List[dict]) -> List[Action]:
        """Handle marble swapping with 'J' or 'JKR' acting as 'J'."""
        actions:list = []
        if card.rank not in ('7', 'JKR'):
            # Swapping only happens with '7' or 'JKR' acting as 'J'
            return actions

        # Active player's marble must not be safe and must be outside kennel
        for marble in active_marbles:
            if marble.is_save or self._is_in_kennel(marble):
                continue

            for target in all_marbles:
                assert self.state is not None
                if target["player_idx"] == self.state.idx_player_active:
                    continue
                if not self._can_swap_with_target(target):
                    continue
                # Valid swap action
                actions.append(
                    Action(
                        card=card,
                        pos_from=marble.pos,
                        pos_to=target["position"],
                        card_swap=None
                    )
                )
        return actions

    def _get_normal_move_actions(self, card: Card, card_values: List[int],
                                active_marbles: List, player_idx: int) -> List[Action]:
        """Handle normal moves based on the card values for marbles outside the kennel."""
        actions = []
        for marble in active_marbles:
            if self._is_in_kennel(marble):
                continue
            for card_value in card_values:
                pos_to = self._calculate_new_position(marble, card_value, player_idx)
                if pos_to is not None:
                    actions.append(
                        Action(
                            card=card,
                            pos_from=marble.pos,
                            pos_to=pos_to,
                            card_swap=None
                        )
                    )
        return actions

    def _is_in_kennel(self, marble: Marble) -> bool:
        """Check if a given marble is currently in the kennel."""
        assert self.state is not None
        player_idx = self.state.idx_player_active
        player_kennel = self.KENNEL_POSITIONS[player_idx]
        return marble.pos in player_kennel

    def _can_swap_with_target(self, target_marble_info: dict) -> bool:
        """Check if we can swap with the given target marble (opponent's marble)."""
        target_pos = target_marble_info["position"]
        t_player_idx = target_marble_info["player_idx"]
        if target_marble_info["is_save"]:
            return False
        if (target_pos in self.SAFE_SPACES[t_player_idx] or
            target_pos in self.KENNEL_POSITIONS[t_player_idx] or
            target_pos == self.START_POSITIONS[t_player_idx]):
            return False
        return True

    def apply_action(self, action: Optional[Action]) -> None:
        # pylint: disable=redefined-outer-name
        if not self.state:
            raise ValueError("Game state is not set.")

        # Attempt a reshuffle if the draw pile is empty and discard is not empty
        # This ensures that if we run out of cards, we reshuffle before proceeding.
        if not self.state.list_card_draw and self.state.list_card_discard:
            self.reshuffle_discard_into_draw()

        active_player = self.state.list_player[self.state.idx_player_active]

        # Handle the case where no action is provided (skip turn)
        if action is None:
            print("No action provided. Advancing the active player.")
            possible_actions = self.get_list_action()
            if not possible_actions:
                # No moves possible: fold scenario
                self.state.list_card_discard.extend(active_player.list_card)
                active_player.list_card.clear()
            else:
                # Moves are available, but player passed turn: do not discard/clear hand
                pass

            self.state.idx_player_active = (self.state.idx_player_active + 1) % len(self.state.list_player)

            # If all players are out of cards, advance to the next round
            if all(len(player.list_card) == 0 for player in self.state.list_player):
                self.next_round()
            return

        # Card exchange phase
        if not self.state.bool_card_exchanged:
            self._handle_card_exchange(action, active_player)
            return

        # Check if all players are out of cards
        if all(len(player.list_card) == 0 for player in self.state.list_player):
            self.next_round()
            return

        # Log the action being applied
        print(f"Player {active_player.name} plays {action.card.rank} of {action.card.suit} "
        f"moving marble from {action.pos_from} to {action.pos_to}.")

        # Remove the played card from the player's hand
        active_player.list_card.remove(action.card)

        # Add the played card to the discard pile
        self.state.list_card_discard.append(action.card)

        # Handle special cards
        if action.card.rank == 'J':
            self._handle_jack(action)
        elif action.card.rank == 'JKR':
            self._handle_joker(action)
        # elif action.card.rank == '7':
        #   self._handle_seven_card(action.card, active_player.list_marble)
        else:
            self._handle_normal_move(action, active_player)

        # Check for collision with other players' marbles
        self._check_collisions(action)

        # Advance to the next active player
        self.state.idx_player_active = (self.state.idx_player_active + 1) % len(self.state.list_player)

    def _handle_jack(self, move_action: Action) -> None:
        """Handle the Jack card action (swap marbles)."""

        # Ensure the game state is not None
        if self.state is None:
            raise ValueError("Game state is not set.")

        # Ensure pos_from and pos_to are not None
        if move_action.pos_from is None or move_action.pos_to is None:
            raise ValueError("Both pos_from and pos_to must be specified for the Jack action.")

        # Find the marble to swap from the active player
        marble_from: Optional[Marble] = None
        active_player_index = self.state.idx_player_active
        active_player = self.state.list_player[active_player_index]

        for marble in active_player.list_marble:
            if marble.pos == move_action.pos_from:
                marble_from = marble
                break

        # Find the marble to swap from the opponent
        marble_to: Optional[Marble] = None
        for player in self.state.list_player:
            if player != active_player:
                for marble in player.list_marble:
                    if marble.pos == move_action.pos_to:
                        marble_to = marble
                        break
                if marble_to:
                    break

        # Swap the positions of the marbles if both marbles were found
        if marble_from and marble_to:
            marble_from.pos, marble_to.pos = marble_to.pos, marble_from.pos
            print(f"Swapped marbles: {marble_from.pos} with {marble_to.pos}")
        else:
            raise ValueError("Could not find marbles to swap for the Jack action.")



    def _handle_joker(self, move_action: Action) -> None:
        """Handle the Joker card action (wild card)."""
        if self.state is None:
            raise ValueError("Game state is not set.")

        if move_action.pos_from is not None and move_action.pos_to is not None:
            idx_active = self.state.idx_player_active
            active_player = self.state.list_player[idx_active]

            for marble in active_player.list_marble:
                if marble.pos == move_action.pos_from:
                    marble.pos = move_action.pos_to
                    marble.is_save = marble.pos in self.SAFE_SPACES[idx_active]
                    break


    def _handle_normal_move(self, move_action: Action, active_player: PlayerState) -> None:
        """Handle a normal move action (non-special card)."""
        if self.state is None:
            raise ValueError("Game state is not set.")

        # Provide a default value if pos_to is None (e.g., -1)
        pos_to = move_action.pos_to if move_action.pos_to is not None else -1

        idx_active: int = self.state.idx_player_active

        if move_action.pos_from in self.KENNEL_POSITIONS[idx_active] and pos_to in self.START_POSITIONS:
            for marble in active_player.list_marble:
                if marble.pos == move_action.pos_from:
                    marble.pos = pos_to  # Assign the (default or valid) pos_to
                    marble.is_save = True  # Mark the marble as safe after leaving the kennel
                    print(f"Marble moved from kennel to start position: {marble.pos}.")
                    break
        else:
            for marble in active_player.list_marble:
                if marble.pos == move_action.pos_from:
                    marble.pos = pos_to  # Assign the (default or valid) pos_to
                    marble.is_save = marble.pos in self.SAFE_SPACES[idx_active]
                    if marble.is_save:
                        print(f"Marble moved to a safe space at position {marble.pos}.")
                    break
            else:
                raise ValueError(f"No marble found at position {move_action.pos_from} for Player {active_player.name}.")

    def _handle_card_exchange(self, move_action: Action, active_player: PlayerState) -> None:
        """Handle the card exchange phase."""
        if self.state is None:
            raise ValueError("Game state is not set.")

        idx_active = self.state.idx_player_active
        idx_partner = (idx_active + 2) % self.state.cnt_player
        partner = self.state.list_player[idx_partner]

        if move_action.card not in active_player.list_card:
            raise ValueError(f"Card {move_action.card} not found in active player's hand.")

        active_player.list_card.remove(move_action.card)
        partner.list_card.append(move_action.card)

        # Advance to the next active player
        self.state.idx_player_active = (idx_active + 1) % self.state.cnt_player

        if self.state.idx_player_active == self.state.idx_player_started:
            self.state.bool_card_exchanged = True
            print("All players have completed their card exchanges.")


    def _check_collisions(self, move_action: Action) -> None:
        """Check for collisions with other players' marbles."""
        if self.state is None:
            raise ValueError("Game state is not set.")

        idx_active = self.state.idx_player_active

        for other_idx, other_player in enumerate(self.state.list_player):
            if other_idx == idx_active:
                continue  # Skip the active player

            for other_marble in other_player.list_marble:
                if other_marble.pos == move_action.pos_to:  # Collision detected
                    print(f"Collision! Player {other_player.name}'s marble at position {other_marble.pos} "
                        "is sent back to the kennel.")

                    for pos in self.KENNEL_POSITIONS[other_idx]:
                        if all(marble.pos != pos for player in self.state.list_player for marble in player.list_marble):
                            other_marble.pos = pos
                            other_marble.is_save = False
                            break


    def get_cards_per_round(self) -> int:
        """Determine the number of cards to be dealt based on the round."""
        if not self.state:
            raise ValueError("Game state is not set.")

        # Round numbers repeat in cycles of 5: 6, 5, 4, 3, 2
        return 6 - ((self.state.cnt_round - 1) % 5)

    def update_starting_player(self) -> None:
        """Update the starting player index for the next round (anti-clockwise)."""
        if not self.state:
            raise ValueError("Game state is not set.")
        self.state.idx_player_started = (self.state.idx_player_started - 1) % self.state.cnt_player

    def reshuffle_discard_into_draw(self) -> None:
        """
        Shuffle the discard pile back into the draw pile when the draw pile is empty.
        Ensures no cards are lost or duplicated in the process.
        If more than 110 cards are detected, reset the entire deck.
        """
        if not self.state:
            raise ValueError("Game state is not set.")

        if not self.state.list_card_discard:
            raise ValueError("Cannot reshuffle: Discard pile is empty.")

        print("Debug: Reshuffling the discard pile into the draw pile.")

        # Add all cards from the discard pile to the draw pile
        self.state.list_card_draw.extend(self.state.list_card_discard)

        # Clear the discard pile
        self.state.list_card_discard.clear()

        # Shuffle the draw pile to randomize
        random.shuffle(self.state.list_card_draw)
        print(f"Debug: Reshuffle complete. Draw pile count: {len(self.state.list_card_draw)}.")

        # Validate total card count
        draw_count = len(self.state.list_card_draw)
        discard_count = len(self.state.list_card_discard)
        player_card_count = sum(len(player.list_card) for player in self.state.list_player)
        total_cards = draw_count + discard_count + player_card_count

        # If more than 110 cards are detected, reset the card deck
        if total_cards > 110:
            print("Warning: More than 110 cards detected. Resetting the card deck.")

            # Clear all cards from draw pile, discard pile, and players' hands
            self.state.list_card_draw.clear()
            self.state.list_card_discard.clear()
            for player in self.state.list_player:
                player.list_card.clear()

            # Re-initialize the deck with the original full set of cards
            # Assuming GameState.LIST_CARD contains the original full deck
            self.state.list_card_draw.extend(GameState.LIST_CARD)
            random.shuffle(self.state.list_card_draw)

            print("Deck has been reset to the original full set of cards.")

    def deal_cards(self) -> None:
        """Deal cards to each player for the current round."""
        if not self.state:
            raise ValueError("Game state is not set.")

        num_cards = self.get_cards_per_round()
        total_needed = num_cards * (len(self.state.list_player))

        # Reshuffle if necessary
        while len(self.state.list_card_draw) < total_needed:
            if not self.state.list_card_discard:
                raise ValueError("Not enough cards to reshuffle and deal.")
            self.reshuffle_discard_into_draw()

        # Shuffle the draw pile
        random.shuffle(self.state.list_card_draw)

        # Deal cards one by one to each player
        for _ in range(num_cards):
            for _, player in enumerate(self.state.list_player):
                # Ensure enough cards are available in the draw pile
                if not self.state.list_card_draw:
                    if not self.state.list_card_discard:
                        raise ValueError("Not enough cards to reshuffle and deal.")
                    self.reshuffle_discard_into_draw()

                # Give one card to the current player
                card = self.state.list_card_draw.pop()
                player.list_card.append(card)


    def validate_game_state(self) -> None:
        """Validate the game state for consistency."""
        if not self.state:
            raise ValueError("Game state is not set.")

        # Ensure the number of cards matches the round logic
        expected_cards = self.get_cards_per_round()
        for player in self.state.list_player:
            if len(player.list_card) > expected_cards:
                raise ValueError(f"Player {player.name} has more cards than allowed in round {self.state.cnt_round}.")

        # Ensure the deck and discard piles are consistent
        total_cards = len(self.state.list_card_draw) + len(self.state.list_card_discard)
        for player in self.state.list_player:
            total_cards += len(player.list_card)
        if total_cards != len(GameState.LIST_CARD):
            raise ValueError("Total number of cards in the game is inconsistent.")


    def next_round(self) -> None:
        """Advance to the next round."""
        if not self.state:
            raise ValueError("Game state is not set.")

        print(f"Advancing to round {self.state.cnt_round + 1}.")
        self.state.cnt_round += 1

        # Update the starting player for the next round
        self.update_starting_player()

        # Clear player cards to prepare for new distribution
        for player in self.state.list_player:
            player.list_card = []

        # Deal cards for the new round
        self.deal_cards()

        #Update Card exchange to not done
        self.state.bool_card_exchanged = False

        print(f'''\nRound {self.state.cnt_round} begins.
            Player {self.state.list_player[self.state.idx_player_started].name} starts.''')


    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        if not self.state:
            raise ValueError("Game state is not set.")
        masked_players = []
        for i, player in enumerate(self.state.list_player):
            if i == idx_player:
                masked_players.append(player)
            else:
                masked_players.append(PlayerState(name=player.name, list_card=[], list_marble=player.list_marble))
        return GameState(
            cnt_player=self.state.cnt_player,
            phase=self.state.phase,
            cnt_round=self.state.cnt_round,
            bool_game_finished=self.state.bool_game_finished,
            bool_card_exchanged=self.state.bool_card_exchanged,
            idx_player_started=self.state.idx_player_started,
            idx_player_active=self.state.idx_player_active,
            list_player=masked_players,
            list_card_draw=self.state.list_card_draw,
            list_card_discard=self.state.list_card_discard,
            card_active=self.state.card_active,
            board_positions=self.state.board_positions
        )


class RandomPlayer(Player):
    """A player that selects actions randomly."""

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """
        Given masked game state and possible actions, select the next action randomly.
        """
        if actions:
            return random.choice(actions)
        return None

    def on_game_start(self) -> None:
        """Called at the start of the game."""
        print(f"{self.__class__.__name__} has started the game!")

    def on_game_end(self, result: str) -> None:
        """
        Called at the end of the game.

        Args:
            result (str): Result of the game (e.g., 'win', 'lose', 'draw').
        """
        print(f"{self.__class__.__name__} finished the game with result: {result}")

if __name__ == '__main__':

    game = Dog()

    random_player = RandomPlayer()

    # Ensure the game state is initialized before proceeding
    if game.state is None:
        print("Error: Game state is not initialized. Exiting...")

    else:
        game.draw_board()  # Draw the initial board

        game.validate_total_cards()

        while game.state.phase != GamePhase.FINISHED:
            game.print_state()

            # Get the list of possible actions for the active player
            game_actions = game.get_list_action()
            # Display possible game_actions
            print("\nPossible Actions:")
            for idx, action in enumerate(game_actions):
                print(f"{idx}: Play {action.card.rank} of {action.card.suit} from {action.pos_from} to {action.pos_to}")

            # Select an action (random in this example)
            selected_action = random_player.select_action(game.get_state(), game_actions)


            # Apply the selected action
            game.apply_action(selected_action)
            game.draw_board()  # Update the board after each action

            #debuging for deck management to see how many cards are in different piles
            game.validate_total_cards()

            # Optionally exit after a certain number of rounds (for testing)
            if game.state.cnt_round > 15:  # Example limit
                print(f"Ending game for testing after {game.state.cnt_round} rounds.")
                break
