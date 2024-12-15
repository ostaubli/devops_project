"""
Dog game implementation module.
This module contains the core game logic and data structures for the Dog card game.
"""

# runcmd: cd ../.. & venv\Scripts\python server/py/dog_template.py
import random
from typing import List, Optional, Dict, Any, Set, Union
from server.py.game import Game
from server.py.dog_game_state import Card, Marble, PlayerState, Action, GameState, GamePhase
from server.py.dog_player import RandomPlayer

class Dog(Game):
    """
    Dog board game implementation.

    Constants define board layout, card values, and game rules.
    """

    # Constants
    BOARD_SIZE = 96
    MAIN_TRACK = 64
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
                        board_positions=[None] * self.BOARD_SIZE  # Initialize board positions
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
        assert  self.state
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

        start_positions: Dict[int, int] = self.START_POSITIONS
        safe_spaces: Dict[int, List[int]] = self.SAFE_SPACES
        kennel_positions: Dict[int, List[int]] = self.KENNEL_POSITIONS
        # Create a list of all marbles for checking occupancy
        all_marbles: List[Dict[str, Any]] = self._get_all_marbles()
        # Define helper functions
        def is_blocked_start_position(pos: int) -> bool:
            # A start position is blocked if there's a marble with is_save=True on it
            return any(m["position"] == pos and m["is_save"] for m in all_marbles)

        # Current position of the marble
        current_pos = marble.pos

        # Rule 1: Marble in the kennel cannot move
        if current_pos in kennel_positions[player_idx]:
            return None

        # calculate new tentantive position
        main_track = self.MAIN_TRACK
        tentative_pos = (current_pos + move_value) % main_track

        # Collect all marble positions for quick lookup
        positions_occupied: Set[int] = {m["position"] for m in all_marbles}

        #create a list of all passing fields
        if current_pos <= tentative_pos:
            positions_to_check = list(range(current_pos + 1, tentative_pos + 1))
        else:
            positions_to_check = list(range(current_pos + 1, main_track)) + list(range(0, tentative_pos + 1))

        # Rule 2: check if starting position is inbetween
        start_positions_values = set(start_positions.values())
        for pos in positions_to_check:
            if pos in start_positions_values:
                # We have encountered a start position, check if blocked
                if is_blocked_start_position(pos):
                    # If the position is blocked and this is not our final destination, we're trying to jump over it
                    # If we end exactly on a blocked start position, also invalid
                    return None

        #Rule 3: move within save space
        player_safe_spaces = safe_spaces[player_idx]
        if current_pos in player_safe_spaces:
            # Find the current index of the marble in the safe_spaces list
            current_index = player_safe_spaces.index(current_pos)
            target_index = current_index + move_value

            # Check if target_index is within the bounds of the safe_spaces
            if target_index < 0 or target_index >= len(player_safe_spaces):
                # Overshoot beyond safe space boundaries
                return None

            # Extract positions we must pass through (including the final one)
            if target_index > current_index:
                path_positions = player_safe_spaces[current_index + 1:target_index + 1]
            else:
                path_positions = player_safe_spaces[target_index:current_index]

            # Check each position in the path for blocking marbles
            for pos in path_positions:
                if pos in positions_occupied:
                    # We hit a marble in the path or final position -> cannot overjump or land on it
                    return None

            # If no block, we can safely move the marble to the target position
            return player_safe_spaces[target_index]

        # Rule 4: move to the save spaces
        player_start_pos = start_positions[player_idx]
        if not marble.is_save and (player_start_pos + 1) in positions_to_check:
            if player_start_pos >= current_pos:
                steps_to_start = player_start_pos - current_pos
            else:
                steps_to_start = (main_track - current_pos) + player_start_pos

            steps_into_safe_space = move_value - steps_to_start
            if steps_into_safe_space < 0 or steps_into_safe_space > len(player_safe_spaces):
                # Either we don't actually step into safe spaces or we overshoot them
                return None

            # The path in safe spaces is from player_safe_spaces[0] up to final_safe_pos
            if steps_into_safe_space > 0:
                path_positions = player_safe_spaces[:steps_into_safe_space]
            else:
                path_positions = []

            # Check each position in the safe space path for blocking marbles
            for pos in path_positions:
                if pos in positions_occupied:
                    # If a marble is found on the path (including final position), we cannot jump over or land on it
                    return None

            final_safe_pos = player_safe_spaces[steps_into_safe_space - 1] if steps_into_safe_space > 0 else None
            return final_safe_pos

        return tentative_pos if 0 <= tentative_pos <= self.BOARD_SIZE else None

    def validate_total_cards(self) -> None:
        """Ensure the total number of cards remains consistent."""
        assert self.state

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
        assert self.state

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

        def dfs(remaining: int, moves: List[int], marble_indices: List[int], results: List[List[tuple[int, int]]]) -> None:
            """Recursive helper to generate splits."""
            if remaining == 0:
                # Ensure the split uses exactly 7 points and all moves are valid
                if sum(moves) == 7:
                    valid_split = True
                    for i, steps in enumerate(moves):
                        if steps > 0:  # Only check marbles that moved
                            marble = marbles_outside_kennel[marble_indices[i]]
                            pos_to = self._calculate_new_position(marble, steps, player_idx)
                            if pos_to is None:
                                valid_split = False  # Invalidate the split if any move is invalid
                                break
                    if valid_split:
                        results.append([(marble_indices[i], moves[i]) for i in range(len(moves)) if moves[i] > 0])
                return

            for i in range(len(moves)):
                # Add 1 step to the current marble's move
                moves[i] += 1
                pos_to = self._calculate_new_position(marbles_outside_kennel[marble_indices[i]], moves[i], player_idx)

                if pos_to is not None:
                    dfs(remaining - 1, moves, marble_indices, results)

                # Backtrack (remove the step)
                moves[i] -= 1

        # Generate all valid splits
        marble_indices = list(range(len(marbles_outside_kennel)))
        results: List[List[tuple[int, int]]] = []  # Store splits as (marble index, steps)
        dfs(7, [0] * len(marbles_outside_kennel), marble_indices, results)

        # Convert valid splits into grouped actions
        grouped_actions_list = []
        for split in results:
            split_actions = []
            for marble_idx, steps in split:
                marble = marbles_outside_kennel[marble_idx]
                pos_to = self._calculate_new_position(marble, steps, player_idx)
                if pos_to is not None:

                    new_action = Action(
                        card=card,
                        pos_from=marble.pos,
                        pos_to=pos_to,
                        card_swap=None
                    )
                    # Append only if the action is unique
                    if new_action not in split_actions:
                        split_actions.append(new_action)
        
            grouped_actions_list.append(split_actions)

        return grouped_actions_list

    def _exchange_jkr(self) -> List[Action]:
        actions_list_jkr: List['Action'] = []
        #all ranks and sueit we can exchange for the jkr
        suits = GameState.LIST_SUIT
        ranks = GameState.LIST_RANK
        if 'JKR' in ranks:
            ranks.remove('JKR')

        jkr_card = Card(suit='', rank='JKR')

        #initalize player information to check moves (or which cards we can exchange to)
        assert self.state
        active_player_idx = self.state.idx_player_active
        active_player = self.state.list_player[active_player_idx]
        active_marbles:list[Marble] = active_player.list_marble  # marbels of current player
        all_marbles = self._get_all_marbles() #marbel information of all players
        active_marbles_positions = {m.pos for m in active_marbles} # Helper sets for quick lookups
        kennels = self.KENNEL_POSITIONS
        start_positions = self.START_POSITIONS
        player_idx = self.state.idx_player_active
        player_kennel = kennels[player_idx]
        player_start_position = start_positions[player_idx]
        marbles_in_kennel = [marble for marble in active_marbles if marble.pos in player_kennel]
        num_in_kennel = len(marbles_in_kennel)

        def can_do_starting_move(card_rank: str) -> bool:
            """
            Check if a starting move is possible with the given card rank.
            Conditions:
            - There is at least one marble in the kennel.
            - The start position is not occupied by the active player's own marble.
            - The card rank is one of the starting cards.
            """
            if num_in_kennel == 0 or player_start_position in active_marbles_positions: return False

            return card_rank in self.STARTING_CARDS

        for rank in ranks:
            for suit in suits:
                card = Card(suit=suit, rank=rank)
                card_values = self._get_card_value(card)  # Get the list of possible values for the card

                # Check starting moves
                if can_do_starting_move(card.rank):
                    actions_list_jkr.append(
                        Action(card=jkr_card,
                            pos_from=None,
                            pos_to=None,
                            card_swap=card)
                    )
                # Handle `7` or 'JKR' as 7: split moves
                if card.rank == '7':
                    seven_actions = self._handle_seven_card(card, active_marbles)
                    if len(seven_actions) > 0:
                        actions_list_jkr.append(
                            Action(card=jkr_card,
                                pos_from=None,
                                pos_to=None,
                                card_swap=card)
                        )
                    else:
                        # If no actions are possible with '7', skip processing moves for this card.
                        continue

                # Handle MARBLE SWAPPING with `J`: exchange with opponent's marble
                for marble_a in all_marbles:
                    if marble_a["position"] > 63:
                        continue
                    if (marble_a["player_idx"] != active_player_idx
                            and marble_a["is_save"]):
                        continue

                    for marble_b in all_marbles:
                        if marble_b is marble_a:
                            continue
                        if marble_b["position"] > 63:
                            continue
                        if (marble_b["player_idx"] != active_player_idx
                                and marble_b["is_save"]):
                            continue

                        # Check that one of these marbles belongs to the active player and the other doesn't
                        belongs_to_active_a = marble_a["player_idx"] == active_player_idx
                        belongs_to_active_b = marble_b["player_idx"] == active_player_idx
                        if belongs_to_active_a == belongs_to_active_b:
                            # Either both belong to the active player or both don't,
                            # in either case, no valid swap.
                            continue

                        # Add swap action
                        actions_list_jkr.append(Action(
                            card=jkr_card,
                            pos_from=None,
                            pos_to=None,
                            card_swap=card
                        ))

                # all cases with normal cards
                # Iterate over all possible values of the card and check if we can move this far!!
                for marble in active_marbles:
                    if marble.pos not in player_kennel:
                        for card_value in card_values:
                            new_pos: Optional[int] = self._calculate_new_position(marble,
                                                                card_value, self.state.idx_player_active)
                            if new_pos is not None:
                                actions_list_jkr.append(Action(
                                card=jkr_card,
                                pos_from=None,
                                pos_to=None,
                                card_swap=card
                                ))

        return actions_list_jkr

    def get_list_action(self) -> Union[List[Action], List[List[Action]]]:
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
                    self._get_starting_actions(card, marbles_in_kennel, active_player, player_start_position))

            # If card is '7' or 'JKR' (which can act like 7), handle the special "split move"
            if card.rank == '7'and self.state.card_active is None:
                seven_actions = self._handle_seven_card(card, active_player.list_marble)
                if seven_actions:
                    actions_list.append(Action(
                        card=card,
                        pos_from=None,
                        pos_to=None,  
                        card_swap=None
                        ))
                continue

                # After handling special moves for '7' or 'JKR', continue to next card
                # falls actions = True -> card = 7 
                # from / to = None
                # card swap = 7
                # continue

            if card.rank == '7'and self.state.card_active is not None:
                # actions_list.extend(action for sublist in self._handle_seven_card(card, active_player.list_marble) for action in sublist)
                # actions_list.extend(action for sublist in self._handle_seven_card(card, active_player.list_marble) for action in sublist)
                actions_list = self._handle_seven_card(card, active_player.list_marble)
                # After handling special moves for '7' or 'JKR', continue to next card
                # falls actions = True -> card = 7 
                # from / to = None
                # card swap = 7
                continue

            if card.rank == 'JKR':
                actions_list.extend(self._exchange_jkr())
                # After handling special moves for 'j', continue to next card
                continue

            if card.rank == 'J':
                opponent_swap_actions = []
                self_swap_actions = []

                # Collect valid opponent swap actions (only unsafe marbles)
                for marble in all_marbles:
                    if marble["player_idx"] == self.state.idx_player_active or marble["position"] > 63:
                        continue  # Skip own marbles and marbles in the kennel

                    if marble["is_save"]:
                        continue  # Skip safe opponent marbles

                    # For each opponent marble, check for valid target marbles (belong to the active player)
                    for target in all_marbles:
                        if target["player_idx"] != self.state.idx_player_active or target["position"] > 63:
                            continue  # Only consider active player's marbles on the board

                        if marble["player_idx"] == target["player_idx"]:
                            continue  # Skip swaps with marbles of the same player

                        # Add both directions for swaps: (marble <-> target) and (target <-> marble)
                        opponent_swap_actions.append(Action(
                            card=card,
                            pos_from=marble["position"],
                            pos_to=target["position"],
                            card_swap=None
                        ))
                        opponent_swap_actions.append(Action(
                            card=card,
                            pos_from=target["position"],
                            pos_to=marble["position"],
                            card_swap=None
                        ))

                # Collect self-swap actions as a fallback (only if no opponent swaps were found)
                if not opponent_swap_actions:
                    for marble in all_marbles:
                        if marble["player_idx"] != self.state.idx_player_active or marble["position"] > 63:
                            continue  # Skip opponent marbles and marbles in the kennel

                        for target in all_marbles:
                            if target["player_idx"] != self.state.idx_player_active or marble is target or target["position"] > 63:
                                continue  # Skip the same marble and marbles in the kennel

                            # Add valid self-swap action
                            self_swap_actions.append(Action(
                                card=card,
                                pos_from=marble["position"],
                                pos_to=target["position"],
                                card_swap=None
                            ))

                # Prioritize opponent swaps, fallback to self-swaps if none are available
                actions_list.extend(opponent_swap_actions if opponent_swap_actions else self_swap_actions)



                continue

            # For marbles outside the kennel, handle swaps and normal moves
            actions_list.extend(
                self._get_normal_move_actions(card, card_values, active_player.list_marble, player_idx))

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
            for card in active_player.list_card]

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
                ))
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
            print(f"{active_player.name} exchanges {action.card.rank} with {action.card_swap.rank}.")
            active_player.list_card.append(action.card_swap)
            active_player.list_card.remove(action.card)
            # check for further code row: self.state
            return

        # Handle special cards
        if action.card.rank == 'J':
            self._handle_jack(action)
        #elif action.card.rank == 'JKR':
            #self._handle_joker(action)

        # elif action.card.rank == '7':
            # Handle SEVEN card
            # grouped_actions = self.get_list_action()
            # splits_completed = self._handle_seven_card_logic(grouped_actions)

            # if splits_completed:
                # Remove the SEVEN card from player's hand
            # return
        if action.card.rank == '7': 
            if self.state.card_active is None:
                self.state.card_active = action.card

            self.state.card_active = action.card
            print(f"Handling '7' card with active card: {self.state.card_active}")
            self._handle_overtaking(action)
            self._check_collisions(action)
            self._handle_normal_move(action, active_player)

        else:
            self._handle_normal_move(action, active_player)

        # Log the action being applied
        print(f"Player {active_player.name} plays {action.card.rank} of {action.card.suit} "
        f"moving marble from {action.pos_from} to {action.pos_to}.")

        # Check for collision with other players' marbles
        self._check_collisions(action)

        # Remove the played card from the player's hand
        active_player.list_card.remove(action.card)

        # Add the played card to the discard pile
        self.state.list_card_discard.append(action.card)

        # Advance to the next active player
        self.state.idx_player_active = (self.state.idx_player_active + 1) % len(self.state.list_player)
        # Check if the game is finished or if a player needs to help their teammate
        self._check_game_finished()

    def _handle_seven_card_logic(self, grouped_actions: List['Action']) -> None:
        """
        Process a SEVEN card by applying valid split actions.
        
        Args:
            grouped_actions (List[Action]): A list of Action instances representing split actions.
        
        Returns:
            bool: True if the split actions were processed successfully, False otherwise.
        """

        try:
            flattened_actions = [
                action
                for sublist in grouped_actions
                for action in (sublist if isinstance(sublist, list) else [sublist])
            ]

            for split_action in flattened_actions:
                # Move the marble according to pos_from and pos_to
                print(f"Applying action: {split_action}")
                self.state.card_active = split_action.card 
                self.apply_action(split_action)
                print(f"SEVEN card: marble moved from {split_action.pos_from} to {split_action.pos_to}.")
            
            print("Card active state reset to None.")
            active_player = self.state.list_player[self.state.idx_player_active]
            active_player.list_card.remove(split_action.card)
            self.state.list_card_discard.append(split_action.card)
            #remove the card_active
            self.state.card_active = None
            # Advance to the next active player
            self.state.idx_player_active = (self.state.idx_player_active + 1) % len(self.state.list_player)
            # Check if the game is finished or if a player needs to help their teammate
            self._check_game_finished()

        except Exception as e:
            print(f"Error processing split actions: {e}")

    def _check_game_finished(self) -> None:
        """Check if the game has finished or a player should help their teammate."""
        assert self.state

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
                    print(f"Player {active_player.name} plays {kennel_action.card.rank} "+
                        f"of {kennel_action.card.suit} moving marble from {kennel_action.pos_from} "+
                        f"to {kennel_action.pos_to}.")

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
                print(
                    f"Moving active player's marble from {mm_action.pos_from}"
                    f" to {mm_action.pos_to}."
                )
                
                # Check if pos_to is not None before assignment
                if mm_action.pos_to is None:
                    raise ValueError(
                        "mm_action.pos_to cannot be None when moving a marble."
                    )
                
                marble.pos = mm_action.pos_to
                marble.is_save = marble.pos in self.SAFE_SPACES[self.state.idx_player_active]
                if marble.is_save:
                    pass
                    # print(f"Marble moved to a safe space at position {marble.pos}.")
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
            print(f"Swapped marbles: Marble at {move_action.pos_from} with "+
                f"marble at {move_action.pos_to}.")
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
        assert self.state

        # Provide a default value if pos_to is None (e.g., -1)
        pos_to = move_action.pos_to if move_action.pos_to is not None else -1

        idx_active: int = self.state.idx_player_active
        kennel_idx_active: list = self.KENNEL_POSITIONS[idx_active]

        if move_action.pos_from in kennel_idx_active and pos_to in self.START_POSITIONS:
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
            # else:
                # raise ValueError(f"No marble found at position {move_action.pos_from} for Player {active_player.name}.")

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
        assert self.state

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


    def _handle_overtaking(self, move_action: Action) -> None:
        """Handle overtaking logic for SEVEN card."""
        assert self.state   # Ensure the game state is set  

        # Collect all positions between `pos_from` and `pos_to`
        overtaken_positions = []
        if move_action.pos_from < move_action.pos_to:
            overtaken_positions = range(move_action.pos_from + 1, move_action.pos_to + 1)
        else:
            overtaken_positions = list(range(move_action.pos_from + 1, 64)) + list(range(0, move_action.pos_to + 1))

        # Exclude any invalid overtaken positions (e.g., own start or safe spaces)
        excluded_positions = set(self.START_POSITIONS.values())
        excluded_positions.update(self.SAFE_SPACES[self.state.idx_player_active])

        # Filter overtaken positions and exclude `pos_to`
        overtaken_positions = [
            pos for pos in overtaken_positions if pos not in excluded_positions and pos != move_action.pos_to
        ]

        # Iterate through all players to identify overtaken marbles
        for player_idx, player in enumerate(self.state.list_player):
            print(f"Processing Player {player_idx + 1}: {player.name}")
            for marble in player.list_marble:
                if marble.pos in overtaken_positions:

                    # Log overtaking event
                    print(f"Overtaking detected! Marble at position {marble.pos} is sent back to the kennel.")
                    kennel_positions = self.KENNEL_POSITIONS[player_idx]
                    print(f"Player {player_idx}'s kennel positions: {kennel_positions}")
                    # Send the overtaken marble back to the kennel
                    for pos in self.KENNEL_POSITIONS[player_idx]:
                        if all(
                            m.pos != pos for p in self.state.list_player for m in p.list_marble
                        ):
                            marble.pos = pos
                            marble.is_save = False
                            print(f"Marble moved to kennel position {pos} for Player {player_idx}.")
                            print("Visualizing marble positions after modification:")
                            for player_idx, player in enumerate(self.state.list_player):
                                print(f"Player {player_idx + 1}: {player.name}")
                                marble_positions = [marble.pos for marble in player.list_marble]
                                print(f"  Marble positions: {marble_positions}")


    def get_cards_per_round(self) -> int:
        """Determine the number of cards to be dealt based on the round."""
        assert self.state
        # Round numbers repeat in cycles of 5: 6, 5, 4, 3, 2
        return 6 - ((self.state.cnt_round - 1) % 5)

    def update_starting_player(self) -> None:
        """Update the starting player index for the next round (anti-clockwise)."""
        assert self.state, "Game state is not set."
        self.state.idx_player_started = (self.state.idx_player_started - 1) % self.state.cnt_player

    def reshuffle_discard_into_draw(self) -> None:
        """
        Shuffle the discard pile back into the draw pile when the draw pile is empty.
        Ensures no cards are lost or duplicated in the process.
        If more than 110 cards are detected, reset the entire deck.
        """
        assert self.state, "Game state is not set."

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

            # print("Deck has been reset to the original full set of cards.")

    def deal_cards(self) -> None:
        """Deal cards to each player for the current round."""
        assert self.state

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
                    assert self.state.list_card_discard
                    self.reshuffle_discard_into_draw()

                # Give one card to the current player
                card = self.state.list_card_draw.pop()
                player.list_card.append(card)


    def validate_game_state(self) -> None:
        """Validate the game state for consistency."""
        assert self.state

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
        assert self.state

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
        assert self.state
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

if __name__ == '__main__':

    game = Dog()
    random_player = RandomPlayer()
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
            print(game_actions)
            # Select an action (random in this example)
            selected_action = random_player.select_action(state=game.state, actions=game_actions)
            print(f"selected action: {selected_action}")
            if selected_action is List: 
                game._handle_seven_card_logic(selected_action)
            else:
                # Apply the selected action
                game.apply_action(selected_action)
            game.draw_board()  # Update the board after each action
            #debuging for deck management to see how many cards are in different piles
            game.validate_total_cards()
            # Optionally exit after a certain number of rounds (for testing)
            if game.state.cnt_round > 3:  # Example limit
                print(f"Ending game for testing after {game.state.cnt_round} rounds.")
                break