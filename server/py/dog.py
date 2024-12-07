from server.py.game import Game, Player
from typing import List, Optional, ClassVar
from pydantic import BaseModel
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
    card_swap: Optional[Card]  # optional card to swap ()


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

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """

        self.board = self._initialize_board()  # Initialize the board
        self.state = GameState(
            cnt_player=4,
            phase=GamePhase.SETUP,
            cnt_round=0,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=[
                PlayerState(name=f"Player {i + 1}", list_card=[],
                            list_marble=[Marble(pos=-1, is_save=False) for _ in range(4)])
                for i in range(4)
            ],
            list_card_draw=random.sample(GameState.LIST_CARD, len(GameState.LIST_CARD)),
            list_card_discard=[],
            card_active=None,
        )

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

    def send_home(self, pos: int) -> None:
        """Send the marble at the given position back to the kennel, if not in finish area."""
        for i, player in enumerate(self.state.list_player):
            for marble in player.list_marble:
                if marble.pos == pos:
                    # Check if the marble is in the finish area
                    if self.is_in_finish_area(marble, i):
                        print(f"{player.name}'s marble at position {pos} is in the finish and cannot be sent home.")
                        return

                    # Send marble back to the kennel
                    marble.pos = -1  # Reset marble position to kennel
                    marble.is_save = False
                    print(f"{player.name}'s marble at position {pos} sent back to the kennel.")
                    return  # Only one marble occupies a position, so stop after handling
        print(f"No marble found at position {pos} to send home.")

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

    def is_in_finish_area(self, marble: Marble, player_index: int) -> bool:
        """
        Check if a marble is in the finish area for the given player.
        Finish areas are unique to each player.
        """
        finish_start = 80 + player_index * 4  # Example: Finish starts at position 80 for Player 1
        finish_end = finish_start + 3  # Each player has 4 finish positions
        return finish_start <= int(marble.pos) <= finish_end

    def is_protected_marble(self, marble: Marble) -> bool:
        """
        Check if a marble is protected (e.g., at the start or in the finish).
        """
        # Find the player who owns the marble
        for player_index, player in enumerate(self.state.list_player):
            if marble in player.list_marble:
                # Check if the marble is in the start or finish area
                return (marble.pos in self.board["start_positions"].get(player_index, [])) or self.is_in_finish_area(
                    marble, player_index)
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


    def get_list_action(self) -> List[Action]:
        """
        Get a list of possible actions for the active player.
        """
        actions = []
        player = self.state.list_player[self.state.idx_player_active]

        # Check possible card plays based on player cards and current game state
        for card in player.list_card:
            if card.rank == 'JKR':  # Joker can be played as any card
                actions.append(Action(card=card, pos_from=None, pos_to=None, card_swap=None))
            elif card.rank == '7':  # Special case: splitting moves
                splitting_combinations = self.generate_splitting_combinations(player.list_marble, 7)
                for combination in splitting_combinations:
                    actions.append(Action(card=card, pos_from=None, pos_to=None, card_swap=combination))
            else:
                # Regular moves
                for marble in player.list_marble:
                    if marble.is_save:
                        target_pos = (marble.pos + int(card.rank)) % len(self.board["circular_path"])
                        actions.append(Action(card=card, pos_from=marble.pos, pos_to=target_pos, card_swap=None))

        return actions

    def generate_splitting_combinations(self, marbles: List[Marble], points: int) -> List[List[tuple]]:
        """
        Generate all possible ways to split movement points among marbles.
        :param marbles: List of marbles that are out of the kennel.
        :param points: Total points to distribute (e.g., 7 for card '7').
        :return: List of splitting combinations as lists of (marble_index, steps).
        """
        if not marbles:
            return []

        # Get the indices of marbles that can move
        marble_indices = [i for i, marble in enumerate(marbles) if marble.is_save]

        if not marble_indices:
            return []

        # Generate all ways to distribute `points` among the marbles
        possible_distributions = [
            comb for comb in combinations_with_replacement(range(points + 1), len(marble_indices))
            if sum(comb) == points
        ]

        # Map distributions to marble indices and generate permutations for order
        splitting_combinations = []
        for dist in possible_distributions:
            for perm in permutations(dist):
                splitting_combinations.append([(marble_indices[i], steps) for i, steps in enumerate(perm)])

        return splitting_combinations

    def get_actions_for_7(self, player: PlayerState) -> List[Action]:
        """
        Generate all possible moves for the card '7' based on splitting the 7 points across marbles.
        """
        actions = []
        marbles = player.list_marble

        # Generate all possible splitting combinations for marbles
        splitting_combinations = self.generate_splitting_combinations(marbles, 7)

        for combination in splitting_combinations:
            move_actions = []
            valid = True  # To validate the combination
            for marble_idx, steps in combination:
                marble = marbles[marble_idx]

                if not marble.is_save:  # Ensure the marble is out of the kennel
                    valid = False
                    break

                target_pos = (marble.pos + steps) % len(self.board["circular_path"])
                move_actions.append(
                    Action(card=Card(suit='', rank='7'), pos_from=marble.pos, pos_to=target_pos, card_swap=None)
                )

            if valid:
                # Create one Action object per splitting combination
                actions.append(
                    Action(card=Card(suit='', rank='7'), pos_from=None, pos_to=None, card_swap=combination)
                )

        return actions

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

    def apply_action(self, action: Action) -> None:
        """ Apply the given action to the game """
        player = self.state.list_player[self.state.idx_player_active]

        if action.card.rank == 'JKR':  # Joker: use as any card
            # Action can be anything based on the game rules, e.g., swap a card or move a marble
            pass

        elif action.card.rank == 'J':
            # Handle the Jack card: Exchange marbles
            self.get_actions_jack(player)

        elif action.card.rank == '7':
            # For card '7', split movements among marbles
            remaining_points = 7
            marble_moves = action.card_swap  # card_swap field stores the movement details
            if not marble_moves:
                print(f"No splitting moves provided for card 7 by {player.name}.")
                return

            for move in marble_moves:
                # move: (marble_index, steps)
                marble_index, steps = move
                if marble_index < 0 or marble_index >= len(player.list_marble):
                    print(f"Invalid marble index {marble_index} for {player.name}.")
                    continue

                marble = player.list_marble[marble_index]
                if not marble.is_save:
                    print(f"{player.name}'s marble {marble_index} is in the kennel and cannot move.")
                    continue

                if remaining_points >= steps:
                    remaining_points -= steps
                    new_pos = (marble.pos + steps) % len(self.board["circular_path"])
                    self.send_home(new_pos)  # Handle overtaking
                    marble.pos = new_pos
                else:
                    print(f"Not enough points remaining for this move by {player.name}.")
                    break
        else:  # Regular behavior for moving marbles based on card rank
            for marble in player.list_marble:
                if marble.pos == action.pos_from and marble.is_save:
                    if action.pos_to is not None:
                        # Check for collisions before moving the marble
                        self.send_home(action.pos_to)
                    marble.pos = action.pos_to
                    marble.is_save = False

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
