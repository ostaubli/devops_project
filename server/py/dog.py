# pylint: disable=too-many-lines,too-many-public-methods,too-many-branches

from typing import List, Optional, ClassVar, Dict
from enum import Enum
import random
from pydantic import BaseModel
from server.py.game import Game, Player


class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank


class Marble(BaseModel):
    pos: int       # position on board (0 to 95)
    is_save: bool  # true if marble was moved out of kennel and was not yet moved


class PlayerState(BaseModel):
    name: str                  # name of player
    list_card: List[Card]      # list of cards
    list_marble: List[Marble]  # list of marbles


class Action(BaseModel):
    card: Card                 # card to play
    pos_from: Optional[int]    # position to move the marble from
    pos_to: Optional[int]      # position to move the marble to
    card_swap: Optional[Card] = None  # optional card to swap ()


class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class GameState(BaseModel):

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

class Dog(Game):

    # Define ranks of cards that have only basic moves
    _BASIC_RANKS: List[str] = ['2', '3', '5', '6', '8', '9', '10', 'Q']

    # Convert strings of card names to their actual values
    _RANK_TO_VALUE: Dict[str, int] = {'2': 2, '3': 3, '5': 5, '6': 6, '8': 8, '9': 9, '10': 10, 'Q': 12}

    # Add starting ranks to indicate starting cards in get list action
    _STARTING_RANKS: List[str] = ['JKR', 'K', 'A']

    # Define last finish position for is_movable_marble
    _LAST_FINISH_POSITION = [71, 79, 87, 95]

    # Define kennel positions for initialisation
    KENNEL_POSITIONS = {
        0: 64,  # Player 1's kennel positions
        1: 72,  # Player 2's kennel positions
        2: 80,  # Player 3's kennel positions
        3: 88  # Player 4's kennel positions
    }

    CIRCULAR_PATH_LENGTH = 64

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """
        self.board = self._initialize_board()  # Initialize the board
        self.state: Optional[GameState] = None
        self.steps_for_7_remaining = 7
        self.action_marble_reset_positions: Dict[int, int] = {}
        self.setup_game()  # Set up the initial game state

    def setup_game(self) -> None:
        """
        Set up the initial game configuration including players, deck, and board positions.
        Each player (index: 0 to 3) begins with four marbles (index: 0 to 3),
        all starting at predefined positions (pos).
        """

        # Create player states with empty hands and marbles at their starting positions
        players = [
            PlayerState(
                name=f"Player {player_idx + 1}",
                list_card=[],
                list_marble=[
                    Marble(
                        pos=self.KENNEL_POSITIONS[player_idx],  # Single position used for all marbles
                        is_save=True
                    )
                    for _ in range(4)  # Create 4 marbles
                ]
            )
            for player_idx in range(4)
        ]

        # Prepare and shuffle the deck
        deck = list(GameState.LIST_CARD)  # Copy card list
        random.shuffle(deck)

        # Initialize the game state
        self.state = GameState(
            cnt_player=4,
            phase=GamePhase.RUNNING,
            cnt_round=1,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=players,
            list_card_draw=deck,
            list_card_discard=[],
            card_active=None  # Empty board positions
        )

        # Distribute the initial hand of cards (6 cards per player in the first round)
        self.deal_cards_for_round(6)

    def _initialize_board(self) -> dict:
        """ Initialize the board representation """
        # Define the circular path and separate home positions for 4 players
        board = {
            "circular_path": list(range(self.CIRCULAR_PATH_LENGTH)),  # 64 positions in a circular path
            "finish_positions": {
                0: [68, 69, 70, 71],  # Blue player's finish positions
                1: [76, 77, 78, 79],  # Yellow player's finish positions
                2: [84, 85, 86, 87],  # Green player's finish positions
                3: [92, 93, 94, 95],  # Red player's finish positions
            },
            "kennel_positions": {
                0: [64],  # Blue player's kennel position
                1: [72],   # Yellow player's kennel position
                2: [80],  # Green player's kennel position
                3: [88],  # Red player's kennel position
            },
            "start_positions": {
                0: [0],  # Blue player's starting position
                1: [16],  # Yellow player's starting position
                2: [32],  # Green player's starting position
                3: [48],  # Red player's starting position
            },
        }
        return board

    def handle_round(self) -> None:
        """
        - Deal cards based on the current round number.
        - Allow teammates to exchange one card.
        - Set the starting player (anti-clockwise from the dealer).
        """
        if self.state is None:
            raise ValueError("Game state is not initialized")

        cards_to_deal = self.get_card_distribution()
        print(f"Starting Round {self.state.cnt_round} - Dealing {cards_to_deal} cards.")
        self.deal_cards_for_round(cards_to_deal)
        if self.check_for_win():
            return
        teammate_pairs = [(0, 2), (1, 3)]  # Example pairing
        for p1, p2 in teammate_pairs:
            self.exchange_cards(p1, p2)
            if self.check_for_win():  # Check after exchanges
                return
        self.set_starting_player()
        if self.check_for_win():
            return

    def get_card_distribution(self) -> int:
        """
        Determine the number of cards to deal based on the current round.
        """
        if self.state is None:
            raise ValueError("Game state is not initialized.")
        card_distribution = [6, 5, 4, 3, 2]  # Adjust as per your game rules
        round_index = (self.state.cnt_round - 1) % len(card_distribution)
        return card_distribution[round_index]

    def deal_cards_for_round(self, cards_to_deal: int) -> None:
        """
        Deal a specific number of cards to each player.
        Reshuffle the discard pile if the draw pile runs out of cards.
        """
        # Ensure state is initialized
        if self.state is None:
            raise ValueError("Game state is not initialized")

        for player in self.state.list_player:
            # Ensure there are enough cards in the draw pile
            if len(self.state.list_card_draw) < cards_to_deal:
                self.reshuffle_discard_pile()
            player.list_card = self.state.list_card_draw[:cards_to_deal] # slices first cards to the player list_card
            self.state.list_card_draw = self.state.list_card_draw[cards_to_deal:] # removes the dealt cards

    def reshuffle_discard_pile(self) -> None:
        """Reshuffle the discard pile into the draw pile."""
        if self.state is None:
            raise ValueError("Game state is not initialized")

        if not self.state.list_card_discard:
            raise ValueError("No cards left to reshuffle!")
        self.state.list_card_draw = (self.state.list_card_draw +
                                     random.sample(self.state.list_card_discard, len(self.state.list_card_discard)))
        self.state.list_card_discard.clear()
        print("Reshuffled the discard pile into the draw pile.")

    def exchange_cards(self, player1_index: int, player2_index: int) -> None:
        """
        Allow teammates to exchange one card each without revealing it.
        """
        if self.state is None:
            raise ValueError("Game state is not initialized.")

        player1 = self.state.list_player[player1_index]
        player2 = self.state.list_player[player2_index]

        # Example: Exchange the first card in their hands
        card_from_p1 = player1.list_card.pop(0)
        card_from_p2 = player2.list_card.pop(0)

        player1.list_card.append(card_from_p2)
        player2.list_card.append(card_from_p1)

        print(f"Player {player1_index} and Player {player2_index} exchanged one card.")

    def fold_cards(self) -> None:
        """
        Handles the case when a player has no actions to perform and must fold their cards.
        """
        if self.state is None:
            raise ValueError("Game state is not initialized.")

        active_player = self.get_active_player()

        # Move all the player's cards to the discard pile
        self.state.list_card_discard.extend(active_player.list_card)
        active_player.list_card.clear()  # Remove all cards from the player's hand

        print(f"{active_player.name} has folded their cards.")

        # Proceed to the next player's turn
        self.proceed_to_next_player()

    def set_starting_player(self) -> None:
        """
        Set the starting player for the current round.
        The starting player is the one to the right of the dealer.
        """
        if self.state is None:
            raise ValueError("Game state is not initialized.")

        if not isinstance(self.state.idx_player_active, int) or not isinstance(self.state.cnt_player, int):
            raise ValueError("Game state is missing required attributes 'idx_player_active' or 'cnt_player'.")

        if self.state.cnt_player <= 0:
            raise ValueError("The number of players (cnt_player) must be greater than zero.")

        self.state.idx_player_active = (self.state.idx_player_active - 1) % self.state.cnt_player
        print(f"Player {self.state.idx_player_active} will start this round.")

        self.state.idx_player_active = (self.state.idx_player_active - 1) % self.state.cnt_player
        print(f"Player {self.state.idx_player_active} will start this round.")

    def send_home(self, marble: Marble) -> None:
        """Send the marble at the given position back to the kennel, if not in finish area."""
        owner = self.get_owner(marble)
        if not owner:
            raise ValueError("Cannot send a homeless marble home :( (no player owns this marble)")
        kennel_position = self.get_player_kennel_positions(owner)
        marble.pos = kennel_position
        marble.is_save = True

    def get_player_kennel_positions(self, player: PlayerState) -> int:
        kennel_positions = self.KENNEL_POSITIONS.get(self.get_player_index(player))
        if not isinstance(kennel_positions, int):
            raise ValueError(f"Invalid kennel position for player {player.name}. Expected a single integer.")
        return kennel_positions

    def position_is_occupied(self, pos: int) -> bool:
        """Checks whether a position on the board is occupied by another marble."""
        if self.state is None or self.state.list_player is None:
            raise ValueError("Game state or player list is not initialized.")

        for player in self.state.list_player:
            for marble in player.list_marble:
                if marble.pos == pos:
                    return True
        return False

    def find_marbles_between(self, pos_from: int, pos_to: int) -> List[Marble]:
        """Find all marbles between any two positions on the board"""
        if self.state is None or self.state.list_player is None:
            raise ValueError("Game state or player list is not initialized.")

        found_marbles = []
        positions_to_check = []

        # Find all positions we need to look at
        if pos_from <= pos_to:
            positions_to_check = list(range(pos_from, pos_to+1))
        else: # The range goes over 0 point of the board
            positions_to_check = list(range(0, pos_to+1))
            positions_to_check.extend(list(range(pos_from, self.CIRCULAR_PATH_LENGTH)))

        # Check if any marbles lie on a found position
        for player in self.state.list_player:
            for marble in player.list_marble:
                if marble.pos in positions_to_check:
                    found_marbles.append(marble)

        return found_marbles

    def find_marble_at_position(self, position: int) -> Optional[Marble]:
        if self.state is None or self.state.list_player is None:
            raise ValueError("Game state or player list is not initialized.")

        for player in self.state.list_player:
            for marble in player.list_marble:
                if marble.pos == position:
                    return marble
        return None

    def get_steps_between(self, pos_from: int, pos_to: int) -> int:
        # Try to find which player's finishing track pos_to belongs to
        player = None
        for p, finish_list in self.board["finish_positions"].items():
            if pos_to in finish_list:
                player = p
                break

        # If pos_to is not a finishing position for any player,
        # it's on the circular track, so we do the old calculation.
        if player is None:
            if pos_from <= pos_to:
                return pos_to - pos_from
            return pos_to + (self.CIRCULAR_PATH_LENGTH - pos_from)

        # If we found a player (pos_to is a finishing position)
        start_position = self.board["start_positions"][player][0]

        # Steps from pos_from to start_position on the circular path
        steps_to_start: int
        if pos_from <= start_position:
            steps_to_start = start_position - pos_from
        else:
            steps_to_start = (self.CIRCULAR_PATH_LENGTH - pos_from) + start_position

        # Determine how many steps into the finishing track pos_to is
        finish_positions = self.board["finish_positions"][player]
        finish_index = finish_positions.index(pos_to)
        steps_in_finishing: int = finish_index + 1  # first finish pos = 1 step beyond start pos

        return steps_to_start + steps_in_finishing

    def move_to_finish(self, marble: Marble, player_index: int, steps: int) -> bool:
        """
        Attempt to move a marble into the finish area.
        """
        if self.state is None or self.state.list_player is None:
            raise ValueError("Game state is not properly initialized.")

        finish_positions = self.board["finish_positions"][player_index]
        start_pos = self.board["start_positions"][player_index][0]

        # Check if the marble has passed the start at least twice
        if marble.pos <= start_pos and marble.is_save:
            print(f"Marble at position {marble.pos} has not passed the start twice.")
            return False

        # Case 1: Marble is already in the finish area
        if marble.pos in finish_positions:
            current_index = finish_positions.index(marble.pos)
            target_index = current_index + steps

            # Check if the target index exceeds the finish area boundary
            if target_index >= len(finish_positions):
                print(f"Marble at position {marble.pos} cannot move beyond the finish area.")
                return False

            # Move the marble within the finish area
            marble.pos = finish_positions[target_index]
            print(f"Marble moved within finish area to position {marble.pos}.")
            return True

        # Case 2: Marble is on the circular path, calculate target position
        target_pos = (marble.pos + steps) % self.CIRCULAR_PATH_LENGTH

        # Check if the marble can enter the finish area
        if target_pos in finish_positions:
            # Place in the first available finish spot
            for pos in finish_positions:
                if all(m.pos != pos for p in self.state.list_player for m in p.list_marble):
                    marble.pos = pos
                    print(f"Marble moved to finish area at position {marble.pos}.")
                    return True

        # Case 3: Regular movement on the circular path
        marble.pos = target_pos
        print(f"Marble moved to position {marble.pos}.")
        return False

    def check_for_win(self) -> bool:
        """
        Check if any player or team has all their marbles in the finish area.
        If so, set the game phase to FINISHED and return True.
        """
        if self.state is None:
            raise ValueError("Game state is not initialized.")

        for player_index, player in enumerate(self.state.list_player):
            finish_positions = self.board["finish_positions"][player_index]
            if all(marble.pos in finish_positions for marble in player.list_marble):
                self.state.phase = GamePhase.FINISHED
                print(f"Player {player.name} has won the game!")
                return True

        # Check for teams (if applicable)
        # Example: Player 0 & 2 are a team, Player 1 & 3 are a team
        teams = [(0, 2), (1, 3)]
        for team in teams:
            if all(
                    all(marble.pos in self.board["finish_positions"][player_index] for marble in
                        self.state.list_player[player_index].list_marble)
                    for player_index in team
            ):
                self.state.phase = GamePhase.FINISHED
                print(f"Team ({team[0]}, {team[1]}) has won the game!")
                return True
        return False

    def is_in_player_finish_area(self, pos: int, player_index: int) -> bool:
        """
        Check if a marble is in the finish area for the given player.
        Finish areas are unique to each player.
        This checks if pos is one of the explicitly listed finish positions for the given player.
        It returns True if pos is found in that list, and False otherwise.
        """
        if self.state is None or self.state.list_player is None:
            raise ValueError("Game state is not properly initialized.")
        return pos in self.board["finish_positions"][player_index]

    def is_in_any_finish_area(self, pos: int) -> bool:
        if self.state is None or self.state.list_player is None:
            raise ValueError("Game state is not properly initialized.")
        for player_index, player in enumerate(self.state.list_player):
            if self.is_in_player_finish_area(pos, player_index):
                return True
        return False

    def is_protected_marble(self, marble: Marble) -> bool:
        """
        Check if a marble is protected (e.g., at the start or in the finish).
        """
        if self.state is None or self.state.list_player is None:
            raise ValueError("Game state is not properly initialized.")
        # Find the player who owns the marble
        for player_index, player in enumerate(self.state.list_player):
            if marble in player.list_marble:
                # Check if the marble is in the start or finish area
                return ((marble.pos in self.board["start_positions"].get(player_index, [])) or
                        self.is_in_player_finish_area(marble.pos, player_index))
        return False

    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        self.state = state

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        if self.state is None:
            raise ValueError("Game state is not initialized.")
        return self.state

    def print_state(self) -> None:
        """ Print the current game state """
        if self.state is None:
            raise ValueError("Game state is not initialized.")
        print(f"Round: {self.state.cnt_round}, Phase: {self.state.phase}")
        for idx, player in enumerate(self.state.list_player):
            print(f"{player.name}: Cards: {player.list_card}, Marbles: {player.list_marble}")

    def deal_cards(self) -> None:
        # TODO: check deal cards?
        """ Deal cards to all players. """
        if self.state is None:
            raise ValueError("Game state is not initialized.")
        for player in self.state.list_player:
            player.list_card = self.state.list_card_draw[:6]
            self.state.list_card_draw = self.state.list_card_draw[6:]

    ## Helper methods to get actions for all basic cards (move = value)
    def get_actions_for_basic_card(self, card: Card, marbles: List[Marble]) -> List[Action]:
        possible_actions = []
        if card.rank in self._BASIC_RANKS:
            for marble in marbles:
                if self.is_movable(marble):
                    pos_from = marble.pos
                    steps = self._RANK_TO_VALUE[card.rank]
                    pos_to = (pos_from + steps) % self.CIRCULAR_PATH_LENGTH

                    # Use the new helper function to check if path is blocked
                    if not self.is_path_blocked_by_safe_marble(pos_from, pos_to):
                        possible_actions.append(Action(card=card, pos_from=pos_from, pos_to=pos_to, card_swap=None))
        return possible_actions

    def is_path_blocked_by_safe_marble(self, pos_from: int, pos_to: int) -> bool:
        # Find marbles between pos_from and pos_to
        found_marbles = self.find_marbles_between(pos_from, pos_to)

        # If you want to exclude the marble at pos_from (the one currently moving), do so:
        found_marbles = [m for m in found_marbles if m.pos != pos_from]

        # Check if any safe marble is present
        return any(m.is_save for m in found_marbles)

    def get_list_action(self) -> List[Action]:
        """
        Get a list of possible actions for the active player.
        """
        if self.state is None:
            raise ValueError("Game state is not initialized.")

        found_actions = []
        player = self.get_active_player()

        # Check whether card exchange still needs to be done and return card exchange actions in this case
        if self.cards_need_to_be_exchanged():
            return self.get_card_exchange_actions(player)

        # First check the cases where a card is still active
        active_card = self.state.card_active
        if active_card:
            if active_card.rank == '7':
                return self.get_actions_for_active_7(active_card, player)
            return self.get_actions_for_card(active_card, player)

        # Determine if there is at least one marble on the board that can be moved
        movable_marbles = any(self.is_movable(marble) for marble in player.list_marble)

        # Check if the player has a starting card
        starting_cards = [card for card in player.list_card if card.rank in self._STARTING_RANKS]
        starting_card_available = len(starting_cards) > 0

        # If no movable marbles and no starting card, return empty
        if not movable_marbles and not starting_card_available:
            return []
        # If no movable marbles and only starting cards, return starting actions
        if not movable_marbles and starting_card_available:
            # Make sure the returned actions are unique
            unique_start_actions = []
            for action in self.get_actions_for_starting_cards(starting_cards, player):
                if action not in unique_start_actions:
                    unique_start_actions.append(action)
            return unique_start_actions


        # Check possible card plays based on player cards and current game state
        for card in player.list_card:
            # Append actions for the given card
            found_actions.extend(self.get_actions_for_card(card, player))

        # Remove duplicate actions
        unique_actions = []
        for action in found_actions:
            if action not in unique_actions:
                unique_actions.append(action)

        return unique_actions

    def cards_need_to_be_exchanged(self) -> bool:
        assert self.state is not None
        return self.state.bool_card_exchanged is False

    def get_card_exchange_actions(self, current_player: PlayerState) -> List[Action]:
        """Generates card exchange actions at beginning of a round"""
        return [
            Action(card=card, pos_from=None, pos_to=None, card_swap=None)
            for card in current_player.list_card]

    def get_actions_for_card(self, card: Card, player: PlayerState) -> List[Action]:
        found_actions = []
        if card.rank in self._BASIC_RANKS:
            found_actions.extend(self.get_actions_for_basic_card(card, player.list_marble))
        elif card.rank == 'JKR':  # Joker can be played as any card
            found_actions.extend(self.get_actions_for_jkr())
        elif card.rank == '4':
            found_actions.extend(self.get_actions_for_4(card, player))
        elif card.rank == '7':  # Special case for card "7"
            found_actions.extend(self.get_actions_for_7(card, player))
        elif card.rank == 'J':
            found_actions.extend(self.get_actions_jake(card, player))
        elif card.rank == 'K':
            found_actions.extend(self.get_actions_for_king(card, player))
        elif card.rank == 'A':
            found_actions.extend(self.get_actions_for_ace(card, player))
        return found_actions

    def get_actions_for_starting_cards(self, starting_cards: List[Card], player: PlayerState) -> List[Action]:
        starting_actions = []
        start_position = self.board["start_positions"][self.get_player_index(player)]
        for marble in player.list_marble:
            # Use the helper function to check if placing on start_pos is possible
            if self.can_place_marble_on_start(player, start_position):
                # If it is possible, append actions for each starting card
                for card in starting_cards:
                    if card.rank == 'JKR':
                        for suit in GameState.LIST_SUIT:
                            starting_actions.extend([
                                Action(card=Card(suit='', rank='JKR'), pos_from=None, pos_to=None,
                                       card_swap=Card(suit=suit, rank='A')),
                                Action(card=Card(suit='', rank='JKR'), pos_from=None, pos_to=None,
                                       card_swap=Card(suit=suit, rank='K')),
                            ])
                    starting_actions.append(Action(
                        card=card,
                        pos_from=marble.pos,
                        pos_to=start_position[0],
                        card_swap=None
                    ))
            # If can_place_marble_on_start returns False,
            # it means the start position is blocked by the player's own marble,
            # so we do not add any actions for this marble.
        return starting_actions


    def get_actions_for_4(self, card: Card, player: PlayerState) -> List[Action]:
        """
        Generate all possible moves for the card '4', where the player can move a marble
        4 steps forward or 4 steps backward.
        """
        actions = []  # List to store possible actions

        # Iterate through all marbles of the player
        for marble in player.list_marble:
            if self.is_movable(marble):  # Only consider marbles that are out of the kennel
                # Calculate positions for forward and backward moves
                target_pos_forward = (marble.pos + 4) % len(self.board["circular_path"])
                target_pos_backward = (marble.pos - 4) % len(self.board["circular_path"])

                # Forward move action
                actions.append(Action(
                    card=card,
                    pos_from=marble.pos,
                    pos_to=target_pos_forward,
                    card_swap=None
                ))

                # Backward move action
                actions.append(Action(
                    card=card,
                    pos_from=marble.pos,
                    pos_to=target_pos_backward,
                    card_swap=None
                ))

        return actions

    def get_actions_jake(self, card: Card, player: PlayerState) -> List[Action]:
        if self.state is None:
            raise ValueError("Game state is not initialized.")
        actions = []
        player_index = self.get_player_index(player)

        # Get all the marbles on the board
        all_marbles = [
            (marble, marble_owner_index)
            for marble_owner_index, marble_owner in enumerate(self.state.list_player)
            for marble in marble_owner.list_marble
            if marble.pos != self.KENNEL_POSITIONS[marble_owner_index]  # Exclude marbles in kennel
        ]

        # Iterate through the player's marbles to consider swaps
        for marble in player.list_marble:
            if not self.is_movable(marble):
                continue

            for target_marble, target_owner_index in all_marbles:
                if marble.pos == target_marble.pos:
                    continue  # Skip same position swaps

                # Ensure we don't swap with safe marbles
                if target_marble.is_save and target_owner_index != player_index:
                    continue

                # Allow swapping only if there are opponents or empty slots
                if target_owner_index == player_index and len(self.state.list_player) > 1:
                    continue

                # Add swap actions
                actions.append(Action(card=card, pos_from=marble.pos, pos_to=target_marble.pos))
                actions.append(Action(card=card, pos_from=target_marble.pos, pos_to=marble.pos))

        # If no actions found, add self-swapping actions for the player's marbles
        if not actions:
            for i, marble_1 in enumerate(player.list_marble):
                if not self.is_movable(marble_1):
                    continue
                for j, marble_2 in enumerate(player.list_marble):
                    if i != j and self.is_movable(marble_2):
                        actions.append(Action(card=card, pos_from=marble_1.pos, pos_to=marble_2.pos))

        return actions

    def get_position_marble(self, marble: Marble) -> int:
        """ Get the position of a marble on the board """
        if not isinstance(marble.pos, int):
            raise ValueError(f"Invalid marble position: {marble.pos}")
        return marble.pos  # Access marble's position directly


    def undo_active_card_moves(self) -> None:
        for marble_index, position in self.action_marble_reset_positions.items():
            marble = self.get_marble(marble_index)
            if marble is None:
                raise ValueError(f"No marble found for index: {marble_index}")
            marble.pos = position
        self.action_marble_reset_positions = {}

    def get_actions_for_active_7(self, active_card: Card, player: PlayerState) -> List[Action]:
        if self.steps_for_7_remaining <= 0:
            return []
        return self.get_actions_for_7(active_card, player, True)

    def get_actions_for_7(self, card: Card, player: PlayerState, already_active: bool = False) -> List[Action]:
        remaining_steps = self.steps_for_7_remaining if already_active else 7
        found_actions = []
        for marble in player.list_marble:
            if not self.is_movable(marble):
                continue
            for steps in range(1, remaining_steps + 1):
                target_position = (marble.pos + steps) % self.CIRCULAR_PATH_LENGTH
                target_marble = self.find_marble_at_position(target_position)

                # Skip illegal actions where a save marble is already at the position
                # (break because overtaking also illegal)
                if target_marble and target_marble.is_save:
                    break

                found_actions.append(Action(card=card, pos_from=marble.pos, pos_to=target_position, card_swap=None))
        return found_actions

    def get_actions_for_king(self, card: Card, player: PlayerState) -> List[Action]:
        """
        Generate all possible moves for the card 'King', where the player can move a marble
        13 steps forward or bring a marble out of the kennel to the start position.
        """
        actions = []
        start_position = self.board["start_positions"][self.get_player_index(player)]  # Player's start position
        kennel_positions = self.board["kennel_positions"][self.get_player_index(player)]  # Player's kennel positions

        # Option 1: Move a marble 13 steps forward
        for marble in player.list_marble:
            if self.is_movable(marble):  # Only consider marbles that are out of the kennel
                target_pos_forward = (marble.pos + 13) % len(self.board["circular_path"])
                actions.append(Action(
                    card=card,
                    pos_from=marble.pos,
                    pos_to=target_pos_forward,
                    card_swap=None
                ))

        # Option 2: Bring a marble out of the kennel
        actions.extend(self.move_marble_out_of_kennel_actions(player, card, kennel_positions, start_position))

        return actions

    def get_actions_for_ace(self, card: Card, player: PlayerState) -> List[Action]:
        """
        Generate all possible moves for the card 'Ace', where the player can:
        - Move a marble 1 step forward.
        - Move a marble 11 steps forward.
        - Bring a marble out of the kennel to the start position.
        """
        actions = []  # List to store possible actions
        start_position = self.board["start_positions"][self.get_player_index(player)]  # Player's start position
        kennel_positions = self.board["kennel_positions"][self.get_player_index(player)]  # Player's kennel positions

        # Option 1: Move a marble 1 step forward
        for marble in player.list_marble:
            if self.is_movable(marble):  # Only consider marbles that are out of the kennel
                target_pos_forward = (marble.pos + 1) % len(self.board["circular_path"])
                actions.append(Action(
                    card=card,
                    pos_from=marble.pos,
                    pos_to=target_pos_forward,
                    card_swap=None
                ))

        # Option 2: Move a marble 11 steps forward
        for marble in player.list_marble:
            if self.is_movable(marble):  # Only consider marbles that are out of the kennel
                target_pos_forward = (marble.pos + 11) % len(self.board["circular_path"])
                actions.append(Action(
                    card=card,
                    pos_from=marble.pos,
                    pos_to=target_pos_forward,
                    card_swap=None
                ))

        # Option 3: Bring a marble out of the kennel
        actions.extend(self.move_marble_out_of_kennel_actions(player, card, kennel_positions, start_position))

        return actions

    def move_marble_out_of_kennel_actions(self, player: PlayerState, card: Card, kennel_positions: List[int],
                                          start_positions: List[int]) -> List[Action]:
        """
        Given a player and a set of kennel and start positions, return a list of actions
        that move the player's marbles out of the kennel if possible.
        """
        out_of_kennel_actions = []
        start_pos = start_positions[0]  # Assuming there's only one start position

        for marble in player.list_marble:
            if marble.pos in kennel_positions:
                # The marble is in the kennel, check if we can move it onto the start position
                if self.can_place_marble_on_start(player, start_pos):
                    out_of_kennel_actions.append(Action(
                        card=card,
                        pos_from=marble.pos,
                        pos_to=start_pos,
                        card_swap=None
                    ))
                # If we cannot place it (position occupied by same player's marble), we just skip
        return out_of_kennel_actions

    def can_place_marble_on_start(self, player: PlayerState, start_pos: int) -> bool:
        """
        Check if a marble can be placed on start_pos for the given player.
        Conditions:
        - If unoccupied, return True.
        - If occupied by player's own marble, return False.
        - If occupied by another player's marble, send that marble home and return True.
        """
        if not self.position_is_occupied(start_pos):
            # Position is free
            return True

        occupant_marble = self.find_marble_at_position(start_pos)
        if occupant_marble is None:
            raise ValueError(f"No marble found at position {start_pos}.")
        occupant_owner = self.get_owner(occupant_marble)
        if occupant_owner == player: # Same player's marble is already there, cannot move here
            return False
        self.send_home(occupant_marble) # Another player's marble occupies the spot, send it home
        return True

    def get_actions_for_jkr(self) -> List[Action]:
        jkr_actions = []  # List to store possible actions
        jkr_ranks = [rank for rank in GameState.LIST_RANK if rank != 'JKR']

        for rank in jkr_ranks:
            for suit in GameState.LIST_SUIT:
                jkr_actions.extend([
                    Action(
                        card=Card(suit='', rank='JKR'),
                        pos_from=None,
                        pos_to=None,
                        card_swap=Card(suit=suit, rank=rank))
                    ])

        return jkr_actions

    def apply_action(self, action: Action) -> None:
        """Apply the given action to the game."""
        if self.state is None:
            raise ValueError("Game state is not initialized.")

        if action is None:
            self.state.card_active = None
            self.undo_active_card_moves()
            self.proceed_to_next_player()
            if self.check_for_win():  # Check for win after folding
                return
            return

        player = self.get_active_player()
        card_finished = True

        # Card exchange phase
        if not self.state.bool_card_exchanged:
            self.apply_card_exchange_action(action, player)
            return

        # Apply move of basic cards
        if action.card.rank in self._BASIC_RANKS or action.card.rank == '4':
            if action.pos_from is None or action.pos_to is None:
                raise ValueError("Invalid action: pos_from or pos_to is None.")
            marble = self.find_marble_at_position(action.pos_from)
            if marble is None:
                raise ValueError(f"No marble found at position {action.pos_from}")
            self.apply_simple_move(marble, action.pos_to, player)
            if self.check_for_win():  # Check if the game is won after moving a marble
                return

        elif action.card.rank in ['A', 'K']:  # Handles both Ace and King
            if action.pos_to is None:
                raise ValueError("Invalid action: pos_to is None.")
            self.send_home_if_occupied(action.pos_to)
            for start_pos, kennel_positions in self.board["kennel_positions"].items():
                if action.pos_from in kennel_positions:  # Marble is in the kennel
                    for marble in player.list_marble:
                        if marble.pos == action.pos_from:
                            # Move marble from kennel to corresponding start position
                            marble.pos = self.board["start_positions"][start_pos][0]
                            marble.is_save = True
                            print(f"{player.name}'s marble moved out of the kennel to position {marble.pos}.")
                            if self.check_for_win():
                                return
                            return
            if action.pos_from is None:
                raise ValueError("Invalid action: pos_from is None.")
            for marble in player.list_marble:
                if marble.pos == action.pos_from and self.is_movable(marble):
                    marble.pos = action.pos_to
                    steps = action.pos_to - action.pos_from
                    print(f"{player.name}'s marble moved {steps} steps forward to position {action.pos_to}.")
                    if self.check_for_win():
                        return
                    return

        elif action.card.rank == 'J':  # Jake action
            # Swap marbles
            print(f"Handling Jake action: {action}")
            if action.pos_from is None or action.pos_to is None:
                raise ValueError("Invalid action: pos_from or pos_to is None.")
            marble_from = self.find_marble_at_position(action.pos_from)
            marble_to = self.find_marble_at_position(action.pos_to)

            if marble_from and marble_to:
                # Swap positions of the two marbles
                marble_from.pos, marble_to.pos = marble_to.pos, marble_from.pos
                print(f"Swapped marbles: {marble_from} at {marble_from.pos}, {marble_to} at {marble_to.pos}.")
                if self.check_for_win():  # Check if the game is won after swapping marbles
                    return

        elif action.card.rank == 'JKR':  # Joker: use as any card
            card_finished = self.apply_jkr_action(action)
            player.list_card.remove(action.card)
            if self.check_for_win():
                return

        elif action.card.rank == '7':
            card_finished = self.apply_seven_action(action)
            if self.check_for_win():
                return

        if card_finished:
            player.list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)
            if self.check_for_win():  # Check if the game is won after this action
                return
            self.proceed_to_next_player()

    def apply_card_exchange_action(self, move_action: Action, current_player: PlayerState) -> None:
        """Apply the card exchange at the beginning of a round"""
        assert self.state

        active_player_index = self.state.idx_player_active
        partner_index = (active_player_index + 2) % self.state.cnt_player
        partner = self.state.list_player[partner_index]

        if move_action.card not in current_player.list_card:
            raise ValueError(f"Card {move_action.card} not found in active player's hand.")

        current_player.list_card.remove(move_action.card)
        partner.list_card.append(move_action.card)

        # Advance to the next active player
        self.state.idx_player_active = (active_player_index + 1) % self.state.cnt_player

        if self.state.idx_player_active == self.state.idx_player_started:
            self.state.bool_card_exchanged = True
            print("All players have completed their card exchanges.")

    def proceed_to_next_player(self) -> None:
        """
        Proceed to the next player in turn order.
        Updates the active player index and increments the round counter.
        """
        if self.state is None:
            raise ValueError("Game state is not initialized.")
        self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player
        self.state.cnt_round += 1

    def apply_seven_action(self, action: Action) -> bool:
        """
        Apply the action for the card rank '7'.
        This may involve moving multiple marbles.
        :returns True if the card is played completely and false if more steps are needed for 7
        """
        if self.state is None:
            raise ValueError("Game state is not initialized.")

        if self.state.card_active is None:
            # This is the first action of a 7 action set
            self.steps_for_7_remaining= 7
            self.state.card_active = action.card
        elif self.state.card_active.rank != '7':
            raise ValueError(f"An action for rank 7 was applied but there is still an active "
                             f"{self.state.card_active.rank} card")

        current_player = self.get_active_player()
        if action.pos_from is None:
            raise ValueError("Invalid action: pos_from is None")
        marble = self.find_marble_at_position(action.pos_from)

        if marble is None:
            raise ValueError(f"No marble found at position {action.pos_from}")

        if action.pos_from is None or action.pos_to is None:
            raise ValueError("Invalid action: pos_from or pos_to is None")

        steps = self.get_steps_between(action.pos_from, action.pos_to)

        marble_index = self.get_marble_index(marble, current_player)
        if marble_index not in self.action_marble_reset_positions:
            self.action_marble_reset_positions[marble_index] = marble.pos

        # Find marbles between pos_from and pos_to (excluding the starting position but including the end position)
        if action.pos_from + 1 is None:
            raise ValueError("Invalid position: pos_from + 1 results in None")

        overtaken_marbles = self.find_marbles_between(action.pos_from + 1, action.pos_to)

        # For each marble found, if it is not safe, send it home
        for overtaken_marble in overtaken_marbles:
            if overtaken_marble is None:
                continue  # Skip if overtaken_marble is None
            if not overtaken_marble.is_save:
                # Record original position of overtaken marble for rollback if needed
                overtaken_marble_index = self.get_marble_index(overtaken_marble)
                if overtaken_marble_index not in self.action_marble_reset_positions:
                    self.action_marble_reset_positions[overtaken_marble_index] = overtaken_marble.pos

                self.send_home(overtaken_marble)

        self.apply_simple_move(marble, action.pos_to, current_player)
        self.steps_for_7_remaining -= steps

        if self.steps_for_7_remaining <= 0:
            self.state.card_active = None
            return True

        return False

    def apply_jkr_action(self, action: Action) -> bool:
        if self.state is None:
            raise ValueError("Game state is not initialized.")
        if self.state.card_active is None:
            self.state.card_active = action.card_swap
        return False

    def get_active_player(self) -> PlayerState:
        if self.state is None:
            raise ValueError("Game state is not initialized.")
        return self.state.list_player[self.state.idx_player_active]

    def apply_simple_move(self, marble: Marble, target_pos: int, player: Optional[PlayerState] = None) -> None:
        """
        Move the marble to the target position, handling collisions and finishing moves.
        """
        if self.state is None:
            raise ValueError("Game state is not initialized.")
        steps = self.get_steps_between(marble.pos, target_pos)
        if self.move_to_finish(marble, self.state.idx_player_active, steps):
            print(f"{player.name if player else 'someone'}'s marble moved to the finish area.")
        else:
            # Check for collisions before moving the marble and send home if so
            self.send_home_if_occupied(target_pos)
            marble.pos = target_pos
        marble.is_save = False

    def send_home_if_occupied(self, target_pos: int) -> None:
        if target_pos is not None and self.position_is_occupied(target_pos):
            existing_marble = self.find_marble_at_position(target_pos)
            if existing_marble and not self.is_in_any_finish_area(target_pos):
                # Send the existing marble home
                self.send_home(existing_marble)

    def is_in_game(self, marble: Marble) -> bool:
        """ Checks if marble is out of the kennel and not in finish area"""
        return 0 <= marble.pos < self.CIRCULAR_PATH_LENGTH

    def is_movable(self, marble: Marble) -> bool:
        # TODO: Handle special case when marble is at the last finish location
        # TODO: Handle finish in general > if a marble is at a position right in front of the atm marble,
        #  cannot move further?
        """Checks whether the marble can be moved. Returns true if it can be moved."""
        if marble.pos in self._LAST_FINISH_POSITION:
            return False
        return self.is_in_game(marble) or self.is_in_any_finish_area(marble.pos)

    def get_owner(self, marble: Marble) -> Optional[PlayerState]:
        """Get player that owns a marble"""
        if self.state is None:
            raise ValueError("Game state is not initialized.")
        for player in self.state.list_player:
            if marble in player.list_marble:
                return player
        return None

    def get_player_index(self, player: PlayerState) -> int:
        if self.state is None:
            raise ValueError("Game state is not initialized.")
        if player not in self.state.list_player:
            raise ValueError(f"Player {player.name} not found in the game state.")
        return self.state.list_player.index(player)

    def get_player(self, player_index: int) -> Optional[PlayerState]:
        if self.state is None:
            raise ValueError("Game state is not initialized.")
        if player_index < len(self.state.list_player):
            return self.state.list_player[player_index]
        return None

    def get_marble_index(self, marble: Marble, player: Optional[PlayerState] = None) -> int:
        owner = player or self.get_owner(marble)
        if owner is None:
            raise ValueError(f"Marble {marble} does not belong to any player.")
        owner_index = self.get_player_index(owner)
        return owner_index * 4 + owner.list_marble.index(marble)

    def get_marble(self, marble_index: int) -> Optional[Marble]:
        # Find player who owns marble
        player_index = marble_index // 4
        # Find index of marble in player's marbles
        player_marble_index = marble_index % 4
        player = self.get_player(player_index)
        if player is None:
            return None  # Player does not exist
        # Check if the marble index is valid for the player's list
        if player_marble_index < len(player.list_marble):
            return player.list_marble[player_marble_index]
        return None  # Marble index is out of range

    def get_player_view(self, idx_player: int) -> GameState:
        """
        Get the masked state for the active player (e.g., the opponent's cards are face down).
        """
        if self.state is None:
            raise ValueError("Game state is not initialized.")
        # Mask the opponent's cards, only showing the player's own cards
        masked_state = self.state.copy()  # Create a copy of the game state
        for i, player in enumerate(masked_state.list_player):
            if i != idx_player:
                player.list_card = []  # Hide the cards of other players
        return masked_state

class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        return random.choice(actions) if actions else None


if __name__ == '__main__':
    # Initialize game and players
    game = Dog()
    dog_players = [RandomPlayer() for _ in range(4)]

    # Ensure game state is initialized
    if game.state is None:
        raise ValueError("Game state is not initialized.")

    # Game setup
    # game.deal_cards()
    game.print_state()

    # Main game loop
    while game.state.phase != GamePhase.FINISHED:
        # Increment round counter and call round logic
        if game.state is None:
            raise ValueError("Game state is not initialized.")
        game.state.cnt_round += 1
        game.handle_round()

        # Proceed with player actions
        if game.state.list_player is None:
            raise ValueError("List of players is not initialized.")
        for _ in range(len(game.state.list_player)):
            if game.state is None:
                raise ValueError("Game state is not initialized.")
            actions_list = game.get_list_action()
            active_player = dog_players[game.state.idx_player_active]
            selected_action = active_player.select_action(
                game.get_player_view(game.state.idx_player_active),
                actions_list
            )
            if selected_action:
                game.apply_action(selected_action)
            if game.check_for_win():  # Check for win after each action
                break

    print("Game Over")
