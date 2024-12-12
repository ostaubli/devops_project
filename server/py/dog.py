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
    name: str                  # name of playerhandle_collision
    list_card: List[Card]      # list of cards
    list_marble: List[Marble]  # list of marbles


class Action(BaseModel):
    """Represents the action information"""
    card: Card                 # card to play
    pos_from: Optional[int | None]    # position to move the marble from
    pos_to: Optional[int | None]      # position to move the marble to
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
        '4': [-4, 4],
        '7': [7]
    }

    TEAM_MAPPING = {
    0: 2,  # Player 0 helps Player 2
    1: 3,  # Player 1 helps Player 3
    2: 0,  # Player 2 helps Player 0
    3: 1   # Player 3 helps Player 1
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
        if card.rank.isdigit() and card.rank.isdigit() != 7:
            return [int(card.rank)]
        # Default to [0] for invalid cards
        return [0]

    def _calculate_new_position(self, marble: Marble, move_value: int, player_idx: int) -> Optional[int]:
        """
        Calculate the new position of a marble, considering:
        - Safe space entry rules for each player
        - Blocking due to marbles on starting points
        - not moving out of kennel
        Returns None if the move is invalid.
        """

        if self.state is None:
            raise ValueError("Game state is not set.")

        # Define helper functions
        def is_blocked_start_position(pos: int) -> bool:
            # A start position is blocked if there's a marble with is_save=True on it
            return any(m["position"] == pos and m["is_save"] for m in all_marbles)

        start_positions = self.START_POSITIONS
        safe_spaces = self.SAFE_SPACES
        kennel_positions = self.KENNEL_POSITIONS

        # Current position of the marble
        current_pos = marble.pos

        # Create a list of all marbles for checking occupancy
        all_marbles = self._get_all_marbles()

        # Rule 1: Marble in the kennel cannot move
        if current_pos in kennel_positions[player_idx]:
            return None

        # calculate new tentantive position
        tentative_pos = (current_pos + move_value) % 64

        #create a list of all passing fields
        if current_pos <= tentative_pos:
            positions_to_check = list(range(current_pos + 1, tentative_pos + 1))
        else:
            positions_to_check = list(range(current_pos + 1, 64)) + list(range(0, tentative_pos + 1))

        # Rule 2: check if starting position is inbetween
        for pos in positions_to_check:
            if pos in list(start_positions.values()):
                # We have encountered a start position, check if blocked
                if is_blocked_start_position(pos):
                    # If the position is blocked and this is not our final destination, we're trying to jump over it
                    if pos != tentative_pos:
                        return None
                    # If we end exactly on a blocked start position, also invalid
                    return None

        #Rule 3: move within save space
        if current_pos in safe_spaces[player_idx]:
            # Find the current index of the marble in the safe_spaces list
            player_safe_spaces = safe_spaces[player_idx]
            current_index = player_safe_spaces.index(current_pos)
            target_index = current_index + move_value

            # Check if target_index is within the bounds of the safe_spaces
            if target_index < 0 or target_index >= len(player_safe_spaces):
                # Overshoot beyond safe space boundaries
                return None
            # Extract positions we must pass through (including the final one)
            path_positions = (player_safe_spaces[current_index+1:target_index+1]
                            if target_index > current_index
                            else player_safe_spaces[target_index:current_index])

            # Gather all marble positions for quick lookup
            positions_occupied = {m["position"] for m in all_marbles}

            # Check each position in the path for blocking marbles
            for pos in path_positions:
                if pos in positions_occupied:
                    # We hit a marble in the path or final position -> cannot overjump or land on it
                    return None

            # If no block, we can safely move the marble to the target position
            return player_safe_spaces[target_index]

        # Rule 4: move to the save spaces
        if start_positions[player_idx] == 0:
            if current_pos != 0:
                current_pos = current_pos - 64
        if current_pos <= start_positions[player_idx] <= tentative_pos and not marble.is_save:
            steps_into_safe_space = tentative_pos - start_positions[player_idx]

            player_safe_spaces = safe_spaces[player_idx]
            if steps_into_safe_space < 0 or steps_into_safe_space > len(player_safe_spaces):
                # Either we don't actually step into safe spaces or we overshoot them
                return None

            # Determine the final safe space position
            final_safe_pos = player_safe_spaces[steps_into_safe_space - 1]

            # Collect all marble positions for quick lookup
            positions_occupied = {m["position"] for m in all_marbles}

            # The path in safe spaces is from player_safe_spaces[0] up to final_safe_pos if steps_into_safe_space > 0
            # For example, if steps_into_safe_space == 2, we are moving into player_safe_spaces[1]
            path_positions = player_safe_spaces[:steps_into_safe_space]

            # Check each position in the safe space path for blocking marbles
            for pos in path_positions:
                if pos in positions_occupied:
                    # If a marble is found on the path (including final position), we cannot jump over or land on it
                    return None

            # If no block found, we can safely move the marble to the final safe space position
            return final_safe_pos


        return tentative_pos if 0 <= tentative_pos <= self.BOARD_SIZE else None



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

    def _get_all_marbles(self) -> List[dict]:
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

    def _handle_seven_card(self, card: Card, active_marbles: List[Marble]) -> List[List[Action]]:
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

        # Convert valid splits into grouped actions
        grouped_actions_list = []
        for split in results:
            split_actions = []
            for marble_idx, steps in split:
                marble = marbles_outside_kennel[marble_idx]
                pos_to = self._calculate_new_position(marble, steps, player_idx)
                if pos_to is not None:
                    split_actions.append(Action(
                        card=card,
                        pos_from=marble.pos,
                        pos_to=pos_to,
                        card_swap=None
                    ))
            grouped_actions_list.append(split_actions)

        return grouped_actions_list


    def _exchange_jkr(self) -> List[Action]:

        #all possible jkr exchanges
        actions_list_jkr = []

        #all ranks we can exchange for the jkr
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['♠', '♥', '♦', '♣']
        #joker card
        jkr = Card(suit='', rank='JKR')

        #initalize player information to check moves (or which cards we can exchange to)
        assert self.state
        active_player = self.state.list_player[self.state.idx_player_active]
        active_marbles:list[Marble] = active_player.list_marble  # marbels of current player
        all_marbles = self._get_all_marbles() #marbel information of all players
        kennels = self.KENNEL_POSITIONS
        start_positions = self.START_POSITIONS
        player_idx = self.state.idx_player_active
        player_kennel = kennels[player_idx]
        player_start_position = start_positions[player_idx]
        marbles_in_kennel = [marble for marble in active_marbles if marble.pos in player_kennel]
        num_in_kennel = len(marbles_in_kennel)

        for rank in ranks:
            for suit in suits:
                card = Card(suit=suit, rank=rank)
                card_values = self._get_card_value(card)  # Get the list of possible values for the card

                # Check for starting moves & Ensure the starting position is free of the active player's own marbles
                if num_in_kennel > 0 and not any(marble.pos == player_start_position for marble in active_marbles):
                    # Only `A`, `K`, `JKR` can perform starting moves
                    if card.rank in self.STARTING_CARDS:
                        actions_list_jkr.append(Action(
                            card=jkr,
                            pos_from=None,
                            pos_to=None,
                            card_swap=card
                        ))

                # Handle `7` or 'JKR' as 7: split moves
                if card.rank == '7':
                    if len(self._handle_seven_card(card, active_marbles)) > 0:
                        actions_list_jkr.append(Action(
                            card=jkr,
                            pos_from=None,
                            pos_to=None,
                            card_swap=card
                        ))
                    else:
                        continue

                # Handle MARBLE SWAPPING with `J`: exchange with opponent's marble
                if card.rank == 'J':
                    for marble in all_marbles:
                        if marble["position"] > 63:
                            continue  # Skip this marble

                        if marble["player_idx"] != self.state.idx_player_active and marble["is_save"] is True:
                            continue

                        for target in all_marbles:
                            # Skip if the same marble is being compared
                            if marble is target:
                                continue

                            if target["position"] > 63:
                                continue  # Skip this marble

                            if target["player_idx"] != self.state.idx_player_active and target["is_save"] is True:
                                continue

                            if self.state.idx_player_active not in (marble['player_idx'], target['player_idx']):
                                continue

                            # prevent swapping on the same player
                            if (marble["player_idx"] is self.state.idx_player_active and
                                target["player_idx"] is self.state.idx_player_active):
                                continue

                            # Add swap action
                            actions_list_jkr.append(Action(
                                card=jkr,
                                pos_from=None,
                                pos_to=None,
                                card_swap=card
                            ))

                    # all cases with cards
                    # Iterate over all possible values of the card, #check if we can move this far!!
                for marble in active_marbles:
                    if marble.pos not in player_kennel:
                        for card_value in card_values:
                            pos_to = self._calculate_new_position(marble, card_value, self.state.idx_player_active)
                            if pos_to is not None:
                                actions_list_jkr.append(Action(
                                card=jkr,
                                pos_from=None,
                                pos_to=None,
                                card_swap=card
                                ))

        return actions_list_jkr

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

        if self.state.card_active is not None:
            current_cards = [self.state.card_active]


        # After exchange phase, normal gameplay actions:
        all_marbles = self._get_all_marbles()
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
            if card.rank == '7':
                actions_list.extend(action for sublist in
                                    self._handle_seven_card(card, active_player.list_marble) for action in sublist)
                # After handling special moves for '7' or 'JKR', continue to next card
                continue

            if card.rank == 'JKR':
                actions_list.extend(self._exchange_jkr())
                # After handling special moves for 'j', continue to next card
                continue

            if card.rank == 'J':
                for marble in all_marbles:
                    if marble["position"] > 63:
                        continue  # Skip this marble

                    if marble["player_idx"] != self.state.idx_player_active and marble["is_save"] is True:
                        continue

                    for target in all_marbles:
                        # Skip if the same marble is being compared
                        if marble is target:
                            continue

                        if target["position"] > 63:
                            continue  # Skip this marble

                        if target["player_idx"] != self.state.idx_player_active and target["is_save"] is True:
                            continue

                        if self.state.idx_player_active not in (marble['player_idx'], target['player_idx']):
                            continue

                        # prevent swapping on the same player
                        if (marble["player_idx"] is self.state.idx_player_active and
                            target["player_idx"] is self.state.idx_player_active):
                            continue

                        # Add swap action
                        actions_list.append(Action(
                            card=card,
                            pos_from=marble["position"],
                            pos_to=target["position"],
                            card_swap=None
                        ))
                continue

            # For marbles outside the kennel, handle swaps and normal moves
            actions_list.extend(
                self._get_normal_move_actions(card, card_values, active_player.list_marble, player_idx)
            )

        unique_action_list = []
        for item in actions_list:
            if item not in unique_action_list:
                unique_action_list.append(item)

        return unique_action_list

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

        #check if only a joker was swapped
        if action.card.rank == 'JKR' and action.card_swap is not None:
            print(f"{active_player.name} exchanges {action.card.rank} wit {action.card_swap.rank}.")
            active_player.list_card.append(action.card_swap)
            active_player.list_card.remove(action.card)
            self.state.card_active = action.card_swap
            return

        # Log the action being applied
        print(f"Player {active_player.name} plays {action.card.rank} of {action.card.suit} "
        f"moving marble from {action.pos_from} to {action.pos_to}.")

        # Handle special cards
        if action.card.rank == 'J':
            self._handle_jack(action)
        elif action.card.rank == '7':
            grouped_actions: List[Action] = self.get_list_action()

            splits_completed: bool = self._handle_seven_card_logic(grouped_actions)

            # Finalize SEVEN card action only if all splits are completed
            if splits_completed: #and action.card in active_player.list_card:
                active_player.list_card.remove(action.card)  # Remove card from hand
                self.state.list_card_discard.append(action.card)  # Add to discard pile
                # Advance player
                self.state.idx_player_active = (self.state.idx_player_active + 1) % len(self.state.list_player)
            return
        else:
            self._handle_normal_move(action, active_player)

        # Check for collision with other players' marbles
        self._check_collisions(action)

        # Remove the played card from the player's hand
        active_player.list_card.remove(action.card)

        # Add the played card to the discard pile
        self.state.list_card_discard.append(action.card)

        #remove the card_active
        self.state.card_active = None

        # Advance to the next active player
        self.state.idx_player_active = (self.state.idx_player_active + 1) % len(self.state.list_player)
        # Check if the game is finished or if a player needs to help their teammate
        self._check_game_finished()

    def _handle_seven_card_logic(self, grouped_actions: List[Action]) -> bool:
        """Process a SEVEN card by applying valid split actions."""
        remaining_steps = 7  # Steps left to process

        if not grouped_actions:
            print("No valid split actions provided for SEVEN card.")
            return False

        for split_actions in grouped_actions:
            print(f"Processing a split with {len(split_actions)} actions.")
            for split_action in split_actions:
                assert self.state
                steps_used = abs(split_action.pos_to - split_action.pos_from)

                # Check for SAFE_SPACES inside-out logic
                if split_action.pos_to in self.SAFE_SPACES[self.state.idx_player_active]:
                    safe_space_index = self.SAFE_SPACES[self.state.idx_player_active].index(split_action.pos_to)
                    expected_safe_space = self.SAFE_SPACES[self.state.idx_player_active][:safe_space_index]
                    if any(
                        pos not in expected_safe_space
                        for pos in self.SAFE_SPACES[self.state.idx_player_active][:safe_space_index]
                    ):
                        print(f"Invalid SAFE_SPACE move: {split_action.pos_to} violates inside-out rule.")
                        continue

                print(f'''Processing SEVEN card action:
                    {split_action.pos_from} -> {split_action.pos_to} with {steps_used} steps.''')
                try:
                    self._handle_seven_marble_movement(split_action)
                    print(f'''SEVEN card: marble successfully moved
                        from {split_action.pos_from} to {split_action.pos_to}.''')

                    # Validate that the active player's marble was moved to the expected position
                    active_player = self.state.list_player[self.state.idx_player_active]
                    marble_found = any(marble.pos == split_action.pos_to for marble in active_player.list_marble)
                    if not marble_found:
                        raise AssertionError(
                            f'''Active player's marble was not found
                            at the expected position {split_action.pos_to} after the move. '''
                            f'''Current marble positions:
                            {[marble.pos for marble in active_player.list_marble]}'''
                        )

                    print(f"Validation Passed: Active player's marble is now at position {split_action.pos_to}.")

                except ValueError as e:
                    print(f"Error processing action {split_action.pos_from} -> {split_action.pos_to}: {e}")
                    return False

                # Deduct steps used from remaining steps
                remaining_steps -= steps_used

                if remaining_steps <= 0:
                    print("All steps for SEVEN card have been processed.")
                    return True

        print("SEVEN card logic complete but not all steps were used.")
        return False

    def _check_game_finished(self) -> None:
        """Check if the game has finished or a player should help their teammate."""
        if not self.state:
            raise ValueError("Game state is not set.")

        for player_idx, player in enumerate(self.state.list_player):
            safe_spaces = self.SAFE_SPACES[player_idx]

            # Check if all marbles are in the safe spaces
            if all(marble.pos in safe_spaces for marble in player.list_marble):
                teammate_idx = self.TEAM_MAPPING[player_idx]
                teammate = self.state.list_player[teammate_idx]

                # Check if the teammate has also finished
                teammate_safe_spaces = self.SAFE_SPACES[teammate_idx]
                if all(marble.pos in teammate_safe_spaces for marble in teammate.list_marble):
                    print(f"Team {player_idx} and {teammate_idx} have won the game!")
                    self.state.phase = GamePhase.FINISHED
                    return

                # Player now helps their teammate
                print(f"Player {player.name} has finished and will help teammate {teammate.name}.")
                self.state.idx_player_active = teammate_idx
                return


    def _handle_kennel_to_start_action(self, kennel_action: Action) -> bool:
        """
        Handle moving a marble from the kennel to the start position.

        Args:
            kennel_action (Action): The kennel_action to apply.

        Returns:
            bool: True if the kennel_action was handled, False otherwise.
        """
        assert self.state
        active_player = self.state.list_player[self.state.idx_player_active]

        # Check if the kennel_action involves moving a marble from the kennel to the start
        if (
            kennel_action.pos_to is not None and
            kennel_action.pos_from in self.KENNEL_POSITIONS[self.state.idx_player_active] and
            kennel_action.pos_to in self.START_POSITIONS
        ):
            for marble in active_player.list_marble:
                if marble.pos == kennel_action.pos_from:
                    # Update marble position and mark as safe
                    marble.pos = kennel_action.pos_to
                    marble.is_save = True
                    print(f"Marble moved from kennel to start position: {marble.pos}.")

                    # Log the kennel_action
                    print(f"Player {active_player.name} plays {kennel_action.card.rank} of {kennel_action.card.suit} "
                        f"moving marble from {kennel_action.pos_from} to {kennel_action.pos_to}.")

                    return True  # Action handled successfully
        return False  # Action does not involve moving from kennel to start


    def _handle_marble_movement_and_collision(self, mm_action: Action) -> None:
        """Handle marble movement and collision resolution."""

        # Move the active player's marble
        moved = False
        assert self.state
        active_player = self.state.list_player[self.state.idx_player_active]

        for marble in active_player.list_marble:
            if marble.pos == mm_action.pos_from:
                print(f"Moving active player's marble from {mm_action.pos_from} to {mm_action.pos_to}.")
                marble.pos = mm_action.pos_to
                marble.is_save = marble.pos in self.SAFE_SPACES[self.state.idx_player_active]
                if marble.is_save:
                    print(f"Marble moved to a safe space at position {marble.pos}.")
                moved = True
                break
        if not moved:
            raise ValueError(
                f"No active player's marble found at position {mm_action.pos_from}. "
                f"Active player's marbles: {[m.pos for m in active_player.list_marble]}"
            )

        # Handle collisions with other players' marbles
        self._handle_collision(mm_action.pos_to)

    def _handle_collision(self, pos_to: int | None) -> None:
        """Handle collision resolution for a given position."""
        assert self.state
        for other_idx, other_player in enumerate(self.state.list_player):
            if other_idx == self.state.idx_player_active:
                continue  # Skip active player's marbles

            for other_marble in other_player.list_marble:
                if other_marble.pos == pos_to:  # Collision detected
                    print(f"Collision detected! Opponent's marble at position {other_marble.pos} "
                        f"is sent back to the kennel by Player {self.state.idx_player_active}.")

                    # Send the opponent's marble back to the kennel
                    for pos in self.KENNEL_POSITIONS.get(other_idx, []):
                        if all(marble.pos != pos for player in self.state.list_player for marble in player.list_marble):
                            other_marble.pos = pos
                            other_marble.is_save = False
                            print(f"Opponent's marble moved to kennel position {pos}.")
                            break

    def _handle_jack(self, move_action: Action) -> None:
        """Handle the Jack card action (swap marbles)."""

        # Ensure the game state is not None
        if self.state is None:
            raise ValueError("Game state is not set.")

        # Ensure pos_from and pos_to are not None
        if move_action.pos_from is None or move_action.pos_to is None:
            raise ValueError("Both pos_from and pos_to must be specified for the Jack action.")

        # Get the marble at pos_from
        marble_from = next(
            (marble for player in self.state.list_player for marble
            in player.list_marble if marble.pos == move_action.pos_from),
            None
        )

        # Get the marble at pos_to
        marble_to = next(
            (marble for player in self.state.list_player for marble
            in player.list_marble if marble.pos == move_action.pos_to),
            None
        )

        # Swap their positions
        if marble_from and marble_to:
            marble_from.pos, marble_to.pos = marble_to.pos, marble_from.pos
            print(f"Swapped marbles: Marble at {move_action.pos_from} with marble at {move_action.pos_to}.")
        else:
            raise ValueError("Could not find one or both marbles to swap for the Jack action.")

        # Find the marble to swap from the active player
        #marble_from: Optional[Marble] = None
        #active_player_index = self.state.idx_player_active
        #active_player = self.state.list_player[active_player_index]

        #for marble in active_player.list_marble:
            #if marble.pos == move_action.pos_from:
                #marble_from = marble
                #break

        # Find the marble to swap from the opponent
        #marble_to: Optional[Marble] = None
        #for player in self.state.list_player:
            #if player != active_player:
                #for marble in player.list_marble:
                    #if marble.pos == move_action.pos_to:
                        #marble_to = marble
                        #break
                #if marble_to:
                    #break

        # Swap the positions of the marbles if both marbles were found
        #if marble_from and marble_to:
            #marble_from.pos, marble_to.pos = marble_to.pos, marble_from.pos
            #print(f"Swapped marbles: {marble_from.pos} with {marble_to.pos}")
        #else:
            #raise ValueError("Could not find marbles to swap for the Jack action.")



    #def _handle_joker(self, move_action: Action) -> None:
        #"""Handle the Joker card action (wild card)."""
        #if self.state is None:
            #raise ValueError("Game state is not set.")

        #if move_action.pos_from is not None and move_action.pos_to is not None:
            #idx_active = self.state.idx_player_active
            #active_player = self.state.list_player[idx_active]

            #for marble in active_player.list_marble:
                #if marble.pos == move_action.pos_from:
                    #marble.pos = move_action.pos_to
                    #marble.is_save = marble.pos in self.SAFE_SPACES[idx_active]
                    #break


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


    def _handle_seven_marble_movement(self, seven_action: Action) -> None:
        """Handle marble movement and collision resolution for SEVEN card seven_actions."""
        assert self.state
        active_player = self.state.list_player[self.state.idx_player_active]

        # Move the active player's marble
        for marble in active_player.list_marble:
            if marble.pos == seven_action.pos_from:
                print(f'''Processing split seven_action:
                    Moving marble from {seven_action.pos_from} to {seven_action.pos_to}.''')
                marble.pos = seven_action.pos_to
                marble.is_save = marble.pos in self.SAFE_SPACES[self.state.idx_player_active]
                if marble.is_save:
                    print(f"Marble moved to a safe space at position {marble.pos}.")
                break
        else:
            raise ValueError(
                f"No active player's marble found at position {seven_action.pos_from} for split seven_action. "
                f"Active player's marbles: {[m.pos for m in active_player.list_marble]}"
            )

        # Handle collisions (including own marbles)
        self._handle_collision(seven_action.pos_to)

        # Handle overtaking logic specifically for SEVEN
        self._handle_overtaking(seven_action.pos_from, seven_action.pos_to)


    def _handle_overtaking(self, pos_from: int, pos_to: int) -> None:
        """Handle overtaking logic for SEVEN card."""
        excluded_positions: set = set()

        # Add all start positions from all players
        excluded_positions.update(self.START_POSITIONS.values())

        # Filter overtaken positions to exclude all invalid positions
        overtaken_positions = [
            pos for pos in range(pos_from + 1, pos_to + 1)
            if pos not in excluded_positions and 0 < pos <= 63
        ]
        assert self.state
        for player_idx, player in enumerate(self.state.list_player):
            for marble in player.list_marble:
                if marble.pos in overtaken_positions:
                    original_pos = marble.pos
                    if player_idx == self.state.idx_player_active:
                        print(f"Overtaking detected! Own marble at position {original_pos} is sent back to the kennel.")
                    else:
                        print(f'''Overtaking detected! Opponent's marble
                            at position {original_pos} is sent back to the kennel.''')

                    # Send the overtaken marble back to the kennel
                    for pos in self.KENNEL_POSITIONS.get(player_idx, []):
                        if all(marble.pos != pos for player in self.state.list_player for marble in player.list_marble):
                            marble.pos = pos
                            marble.is_save = False
                            print(f"Marble moved to kennel position {pos} for Player {player_idx}.")
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
