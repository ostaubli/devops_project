from pandas.core.dtypes.inference import is_integer

from server.py.game import Game, Player
from typing import List, Optional, ClassVar, Dict
from pydantic import BaseModel, Field
from enum import Enum
import random
from itertools import combinations_with_replacement, permutations


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

    # Define kennel positions for initialisation
    KENNEL_POSITIONS = {
        0: [64, 65, 66, 67],  # Player 1's kennel positions
        1: [72, 73, 74, 75],  # Player 2's kennel positions
        2: [80, 81, 82, 83],  # Player 3's kennel positions
        3: [88, 89, 90, 91]  # Player 4's kennel positions
    }

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """
        self.board = self._initialize_board()  # Initialize the board
        self.state: Optional[GameState] = None
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
                    Marble(pos=self.KENNEL_POSITIONS[player_idx][marble_idx], is_save=True)
                    for marble_idx in range(4)
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
            bool_game_finished=False,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=players,
            list_card_draw=deck,
            list_card_discard=[],
            card_active=None,
            board_positions=[None] * 96  # Empty board positions
        )

        # Distribute the initial hand of cards (6 cards per player in the first round)
        self.deal_cards_for_round(6)

    def _initialize_board(self) -> dict:
        """ Initialize the board representation """
        # Define the circular path and separate home positions for 4 players
        board = {
            "circular_path": [i for i in range(63)],  # 63 positions in a circular path
            "finish_positions": {
                0: [68, 69, 70, 71],  # Blue player's finish positions
                1: [76, 77, 78, 79],  # Yellow player's finish positions
                2: [84, 85, 86, 87],  # Green player's finish positions
                3: [92, 93, 94, 95],  # Red player's finish positions
            },
            "kennel_positions": {
                0: [64, 65, 66, 67],  # Blue player's kennel position
                1: [72, 73, 74, 75],   # Yellow player's kennel position
                2: [80, 81, 82, 83],  # Green player's kennel position
                3: [88, 89, 90, 91],  # Red player's kennel position
            },
            "start_positions": {
                0: [0],  # Blue player's starting position
                1: [16],  # Yellow player's starting position
                2: [32],  # Green player's starting position
                3: [48],  # Red player's starting position
            },
        }
        return board

    # Round logic
    def handle_round(self) -> None:
        """
        Handle a single round:
        - Deal cards based on the current round number.
        - Allow teammates to exchange one card.
        - Set the starting player (anti-clockwise from the dealer).
        """
        CARD_DISTRIBUTION = [6, 5, 4, 3, 2]  # Number of cards per round
        round_index = (self.state.cnt_round - 1) % len(CARD_DISTRIBUTION)  # Cycle through rounds
        cards_to_deal = CARD_DISTRIBUTION[round_index]

        print(f"Starting Round {self.state.cnt_round} - Dealing {cards_to_deal} cards.")

        # Step 1: Deal cards
        self.deal_cards_for_round(cards_to_deal)

        # Step 2: Teammates exchange cards
        self.exchange_cards(0, 2)  # Example: Player 0 and Player 2 are teammates
        self.exchange_cards(1, 3)  # Example: Player 1 and Player 3 are teammates

        # Step 3: Set starting player
        self.set_starting_player()

    def deal_cards_for_round(self, cards_to_deal: int) -> None:
        """
        Deal a specific number of cards to each player.
        Reshuffle the discard pile if the draw pile runs out of cards.
        """
        for player in self.state.list_player:
            # Ensure there are enough cards in the draw pile
            if len(self.state.list_card_draw) < cards_to_deal:
                self.reshuffle_discard_pile()

            # Deal the cards
            player.list_card = self.state.list_card_draw[:cards_to_deal]
            self.state.list_card_draw = self.state.list_card_draw[cards_to_deal:]

    def reshuffle_discard_pile(self) -> None:
        """Reshuffle the discard pile into the draw pile."""
        if not self.state.list_card_discard:
            raise ValueError("No cards left to reshuffle!")
        self.state.list_card_draw = random.sample(self.state.list_card_discard, len(self.state.list_card_discard))
        self.state.list_card_discard.clear()
        print("Reshuffled the discard pile into the draw pile.")

    def exchange_cards(self, player1_index: int, player2_index: int) -> None:
        """
        Allow teammates to exchange one card each without revealing it.
        """
        player1 = self.state.list_player[player1_index]
        player2 = self.state.list_player[player2_index]

        # Example: Exchange the first card in their hands
        card_from_p1 = player1.list_card.pop(0)
        card_from_p2 = player2.list_card.pop(0)

        player1.list_card.append(card_from_p2)
        player2.list_card.append(card_from_p1)

        print(f"Player {player1_index} and Player {player2_index} exchanged one card.")

    def set_starting_player(self) -> None:
        """
        Set the starting player for the current round.
        The starting player is the one to the right of the dealer.
        """
        self.state.idx_player_active = (self.state.idx_player_active - 1) % self.state.cnt_player
        print(f"Player {self.state.idx_player_active} will start this round.")

    def send_home(self, marble: Marble) -> None:
        """Send the marble at the given position back to the kennel, if not in finish area."""
        marble.pos = -1
        marble.is_save = False

    def position_is_occupied(self, pos: int) -> bool:
        """Checks whether a position on the board is occupied by another marble."""
        for player in self.state.list_player:
            for marble in player.list_marble:
                if marble.pos == pos:
                    return True
        return False

    def overtake_marble(self, target_pos: int) -> None:
        """
        Handle overtaking at a given position. Send any overtaken marbles back to the kennel.
        """
        for player in self.state.list_player:
            for marble in player.list_marble:
                if marble.pos == target_pos:
                    # Check if the marble is protected (e.g., in start or finish)
                    if self.is_protected_marble(marble):
                        continue
                    # Send overtaken marble back to kennel
                    marble.pos = -1  # Back to kennel
                    marble.is_save = False
                    print(f"{player.name}'s marble at position {target_pos} sent back to the kennel.")

    def move_to_finish(self, marble: Marble, player_index: int, steps: int) -> bool:
        """
        Attempt to move a marble into the finish area.
        """
        finish_positions = self.board["finish_positions"][player_index]
        start_pos = self.board["start_positions"][player_index][0]

        # Check if the marble has passed the start at least twice
        if marble.pos <= start_pos and marble.is_save:
            print(f"Marble at position {marble.pos} has not passed the start twice.")
            return False

        # Calculate target position
        target_pos = marble.pos + steps

        # Check if the marble can enter the finish area
        if target_pos in finish_positions:
            # Place in the next available finish spot (inside to outside)
            for pos in finish_positions:
                if all(m.pos != pos for p in self.state.list_player for m in p.list_marble):
                    marble.pos = pos
                    print(f"Marble moved to finish at position {pos}.")
                    return True

        # Otherwise, move normally
        marble.pos = target_pos % len(self.board["circular_path"])
        print(f"Marble moved to position {marble.pos}.")
        return False

    def is_in_player_finish_area(self, pos: int, player_index: int) -> bool:
        """
        Check if a marble is in the finish area for the given player.
        Finish areas are unique to each player.
        """
        finish_start = 80 + player_index * 4  # Example: Finish starts at position 80 for Player 1
        finish_end = finish_start + 3  # Each player has 4 finish positions
        return finish_start <= pos <= finish_end

    def is_in_any_finish_area(self, pos: int) -> bool:
        for player_index, player in enumerate(self.state.list_player):
            if self.is_in_player_finish_area(pos, player_index):
                return True
        return False

    def is_protected_marble(self, marble: Marble) -> bool:
        """
        Check if a marble is protected (e.g., at the start or in the finish).
        """
        # Find the player who owns the marble
        for player_index, player in enumerate(self.state.list_player):
            if marble in player.list_marble:
                # Check if the marble is in the start or finish area
                return (marble.pos in self.board["start_positions"].get(player_index, [])) or self.is_in_player_finish_area(
                    marble.pos, player_index)
        return False

    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        self.state = state

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        return self.state

    def print_state(self) -> None:
        """ Print the current game state """
        print(f"Round: {self.state.cnt_round}, Phase: {self.state.phase}")
        for idx, player in enumerate(self.state.list_player):
            print(f"{player.name}: Cards: {player.list_card}, Marbles: {player.list_marble}")

    def deal_cards(self) -> None:
        """ Deal cards to all players. """
        for player in self.state.list_player:
            player.list_card = self.state.list_card_draw[:6]
            self.state.list_card_draw = self.state.list_card_draw[6:]

    ## Helper methods to get actions for all basic cards (move = value)
    def get_actions_for_basic_card(self, card: Card, marbles: List[Marble]) -> List[Action]:
        possible_actions = []
        if card.rank in self._BASIC_RANKS:
            for marble in marbles:
                if marble.is_save:  # Marble must be out of the kennel
                    new_pos = (marble.pos + self._RANK_TO_VALUE[card.rank]) % 96  # Modular board movement
                    possible_actions.append(Action(card=card, pos_from=marble.pos, pos_to=new_pos, card_swap=None))

        return possible_actions


    def get_list_action(self) -> List[Action]:
        """
        Get a list of possible actions for the active player.
        """
        actions = []
        player = self.state.list_player[self.state.idx_player_active]

        # Check possible card plays based on player cards and current game state
        for card in player.list_card:
            # Append actions for basic cards
            if card.rank in self._BASIC_RANKS:
                actions.extend(self.get_actions_for_basic_card(card, player.list_marble))
            elif card.rank == 'JKR':  # Joker can be played as any card
                pass
            elif card.rank == '4':
                actions.extend(self.get_actions_for_4(player))
            elif card.rank == '7':  # Special case for card "7"
                actions += self.get_actions_for_7(player.list_marble)
            elif card.rank == 'J':
                pass
                # actions.extend(self.get_actions_jack())
            elif card.rank == 'K':
                pass
            elif card.rank == 'A':
                pass
            else:
                # Regular moves
                for marble in player.list_marble:
                    if marble.is_save:
                        target_pos = (marble.pos + int(card.rank)) % len(self.board["circular_path"])
                        actions.append(Action(card=card, pos_from=marble.pos, pos_to=target_pos, card_swap=None))
        return actions

    def get_actions_for_4(self, player: PlayerState) -> List[Action]:
        """
        Generate all possible moves for the card '4', where the player can move a marble
        4 steps forward or 4 steps backward.
        """
        actions = []  # List to store possible actions

        # Iterate through all marbles of the player
        for marble in player.list_marble:
            if marble.is_save:  # Only consider marbles that are out of the kennel
                # Calculate positions for forward and backward moves
                target_pos_forward = (marble.pos + 4) % len(self.board["circular_path"])
                target_pos_backward = (marble.pos - 4) % len(self.board["circular_path"])

                # Forward move action
                actions.append(Action(
                    card=Card(suit='', rank='4'),
                    pos_from=marble.pos,
                    pos_to=target_pos_forward,
                    card_swap=None
                ))

                # Backward move action
                actions.append(Action(
                    card=Card(suit='', rank='4'),
                    pos_from=marble.pos,
                    pos_to=target_pos_backward,
                    card_swap=None
                ))

        return actions

    def get_actions_for_7(self, marbles: List[Marble]) -> List[List[Action]]:
        player = self.state.idx_player_active
        kennel_positions = self.KENNEL_POSITIONS
        marbles_out_of_kennel = [marble for marble in marbles if marble.pos not in kennel_positions[player]]
        if not marbles_out_of_kennel:
            return []

        # Possible ways to split 7 between 4 marbles
        possible_splits_7 = [
            [2, 2, 2, 1], [3, 2, 1, 1], [3, 2, 2],
            [3, 3, 1], [4, 1, 1, 1], [4, 2, 1],
            [4, 3], [5, 2], [6, 1],
        ]

        actions = []
        marble_indices = range(len(marbles_out_of_kennel))

        for split in possible_splits_7:
            if len(split) > len(marbles_out_of_kennel):
                continue  # Skip invalid splits

            # Generate actions for the split
            split_actions = []
            for marble_idx, steps in zip(marble_indices, split):
                marble = marbles_out_of_kennel[marble_idx]
                target_pos = (marble.pos + steps) % len(self.board["circular_path"])
                split_actions.append(
                    Action(
                        card=Card(suit='', rank='7'),
                        pos_from=marble.pos,
                        pos_to=target_pos,
                        card_swap=None
                    )
                )

            actions.append(split_actions)

        return actions

    def apply_seven_action(self, action: Action) -> None:
        """
        Apply the action for the card rank '7'.
        This may involve moving multiple marbles in steps specified in the action.
        """
        if not isinstance(action, list):  # Ensure we have a list of actions for a split 7
            raise ValueError("Action for '7' must be a list of individual actions for each split.")

        for sub_action in action:
            player = self.state.list_player[self.state.idx_player_active]
            marble = next((m for m in player.list_marble if m.pos == sub_action.pos_from), None)

            if marble and marble.is_save:
                # Check for collisions before moving the marble and send it home if so
                if sub_action.pos_to is not None and self.position_is_occupied(
                        sub_action.pos_to) and not self.is_in_any_finish_area(sub_action.pos_to):
                    self.send_home(marble)
                marble.pos = sub_action.pos_to
                marble.is_save = False

    def get_actions_jack(self, player: PlayerState) -> None:
        """
        Handle the playing of a Jack (J) card.
        This method will ensure that the player must exchange a marble with another player.
        """
        marbles_to_swap = [marble for marble in player.list_marble if
                           marble.is_save and not self.is_protected_marble(marble)]

        if len(marbles_to_swap) == 0:
            print(f"{player.name} has no valid marbles to exchange. The Jack card will have no effect.")
            return

        # Choose a marble to swap (we'll simply pick the first available one for simplicity)
        marble_to_swap = marbles_to_swap[0]

        # Now find a valid opponent or teammate to exchange with.
        # For simplicity, we assume the player can swap with any other player who has an "out" marble.
        other_player = None
        for other in self.state.list_player:
            if other != player:
                other_marbles = [marble for marble in other.list_marble if
                                 marble.is_save and not self.is_protected_marble(marble)]
                if other_marbles:
                    other_player = other
                    marble_from_other = other_marbles[0]  # Pick the first available marble
                    break

        if other_player:
            print(f"{player.name} will exchange a marble with {other_player.name}.")
            # Perform the exchange
            marble_to_swap.pos, marble_from_other.pos = marble_from_other.pos, marble_to_swap.pos
            marble_to_swap.is_save, marble_from_other.is_save = marble_from_other.is_save, marble_to_swap.is_save
        else:
            print(f"No valid player found to exchange marbles with. The Jack card will have no effect.")

    def get_actions_for_king(self, player: PlayerState) -> List[Action]:
        """
        Generate all possible moves for the card 'King', where the player can:
        - Move a marble 13 steps forward.
        - Bring a marble out of the kennel to the start position.
        """
        actions = []
        start_position = self.board["start_positions"][player.index]  # Player's start position
        kennel_positions = self.board["kennel_positions"][player.index]  # Player's kennel positions

        # Option 1: Move a marble 13 steps forward
        for marble in player.list_marble:
            if marble.is_save:  # Only consider marbles that are out of the kennel
                target_pos_forward = (marble.pos + 13) % len(self.board["circular_path"])
                actions.append(Action(
                    card=Card(suit='', rank='K'),
                    pos_from=marble.pos,
                    pos_to=target_pos_forward,
                    card_swap=None
                ))

        # Option 2: Bring a marble out of the kennel
        for marble in player.list_marble:
            if not marble.is_save and marble.pos in kennel_positions:  # Marble is in the kennel
                actions.append(Action(
                    card=Card(suit='', rank='K'),
                    pos_from=marble.pos,  # Current kennel position
                    pos_to=start_position,  # Move to player's start position
                    card_swap=None
                ))

        return actions

    def apply_action(self, action: Action) -> None:
        """ Apply the given action to the game """
        if action is None:
            return

        player = self.state.list_player[self.state.idx_player_active]

        # Apply move of basic cards
        if action.card.rank in self._BASIC_RANKS or action.card.rank == '4':
          for marble in player.list_marble:
                if marble.pos == action.pos_from and marble.is_save:
                    steps = action.pos_to - action.pos_from
                    if self.move_to_finish(marble, self.state.idx_player_active, steps):
                        print(f"{player.name}'s marble moved to the finish area.")
                    else:
                        # Check for collisions before moving the marble and send home if so
                        if action.pos_to is not None and self.position_is_occupied(action.pos_to) and not self.is_in_any_finish_area(action.pos_to):
                            self.send_home(marble)
                        marble.pos = action.pos_to
                    marble.is_save = False

        elif action.card.rank == 'J':
            self.get_actions_jack(player)

        elif action.card.rank == 'JKR':  # Joker: use as any card
            # Action can be anything based on the game rules, e.g., swap a card or move a marble
            pass

        elif action.card.rank == '7':
            self.apply_seven_action(action)

            # # For card "7", interpret the sequence of moves from pos_from and pos_to
            #
            # if not action.pos_from or not action.pos_to:
            #     print(f"Invalid action format for card 7 by {player.name}.")
            #
            #     return
            #
            # remaining_points = 7  # Start with 7 points
            #
            # for pos_from, pos_to in zip(action.pos_from, action.pos_to):
            #
            #     if remaining_points <= 0:
            #         break
            #
            #     # Find the marble at the pos_from position
            #
            #     marble = next((m for m in player.list_marble if m.pos == pos_from), None)
            #
            #     if not marble:
            #         print(f"No marble at position {pos_from} for {player.name}.")
            #
            #         continue
            #
            #     steps = (pos_to - pos_from) % len(self.board["circular_path"])
            #
            #     if steps > remaining_points:
            #         print(f"Not enough points remaining for this move by {player.name}.")
            #
            #         break
            #
            #     # Apply the move
            #
            #     self.overtake_marble(pos_to)  # Handle overtaking
            #
            #     marble.pos = pos_to
            #
            #     remaining_points -= steps
            #
            # if remaining_points > 0:
            #     print(f"{player.name} left {remaining_points} points unused for card 7.")

        else:  # Regular behavior for moving marbles based on card rank
            pass

        # Update the cards: if it's a move action, discard the played card
        player.list_card.remove(action.card)
        self.state.list_card_discard.append(action.card)

        # Proceed to the next player after applying the action
        self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player
        self.state.cnt_round += 1

    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the opponent's cards are face down) """
        # Mask the opponent's cards, only showing the player's own cards
        masked_state = self.state.model_copy()
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
    players = [RandomPlayer() for i in range(4)]

    # Game setup
    game.deal_cards()
    game.print_state()

    # Main game loop
    while game.state.phase != GamePhase.FINISHED:
        # Start a new round
        game.state.cnt_round += 1  # Increment the round counter
        game.handle_round()  # Call the round logic

        # Proceed with player actions
        for _ in range(len(game.state.list_player)):
            actions = game.get_list_action()
            active_player = players[game.state.idx_player_active]
            selected_action = active_player.select_action(game.get_player_view(game.state.idx_player_active), actions)
            if selected_action:
                game.apply_action(selected_action)

        # End condition (example: after 10 rounds)
        if game.state.cnt_round > 10:
            game.state.phase = GamePhase.FINISHED

    print("Game Over")
