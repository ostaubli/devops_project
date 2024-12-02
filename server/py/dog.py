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
    card_swap: Optional[Card]  # optional card to swap ()


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
    list_card_draw: List[Card]      # list of cards to draw
    list_card_discard: List[Card]   # list of cards discarded
    card_active: Optional[Card]        # active card (for 7 and JKR with sequence of actions)

class Dog(Game):

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """
        self.state: Optional[GameState] = None
        self.initialize_game()  # Ensure the game state is initialized

    def initialize_game(self) -> None:
        """
        Initialize the game state with players, deck, and board positions.

        Each player (i: range 0-3) has 4 marbles (j: range 0-3), initialized from unique positions (pos).
        """
        # Initialize players with empty card hands and marbles in their starting positions
        players = [PlayerState(name=f"Player {i+1}", 
                               list_card=[], 
                               list_marble=[Marble(pos=i*24 + j, is_save=True) for j in range(4)]) for i in range(4)]
       
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

        print("Game initialized. Cards have been dealt.")


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
        for player in self.state.list_player:
            print(f"\nPlayer: {player.name}")
            print(f"Cards: {[f'{card.rank} of {card.suit}' for card in player.list_card]}")
            print(f"Marbles: {[f'Position: {marble.pos}, Safe: {marble.is_save}' for marble in player.list_marble]}")

    def draw_board(self) -> None:
        """ Draw the board with kennels as the starting positions and safe spaces as the final destinations """
        if self.state is None:
            raise ValueError("Game state is not set.")

        board_size = 96
        kennels = {
            0: [0, 1, 2, 3],     # Player 1's starting positions
            1: [24, 25, 26, 27], # Player 2's starting positions
            2: [48, 49, 50, 51], # Player 3's starting positions
            3: [72, 73, 74, 75]  # Player 4's starting positions
        }
        safe_spaces = {
            0: [92, 93, 94, 95],  # Player 1's safe spaces
            1: [68, 69, 70, 71],  # Player 2's safe spaces
            2: [44, 45, 46, 47],  # Player 3's safe spaces
            3: [20, 21, 22, 23]   # Player 4's safe spaces
        }

        board = ["." for _ in range(board_size)]

        for player_idx, player in enumerate(self.state.list_player):
            for marble in player.list_marble:
                if marble.pos in safe_spaces[player_idx]:
                    board[marble.pos] = f"S{player_idx+1}"
                elif marble.pos in kennels[player_idx]:
                    board[marble.pos] = f"K{player_idx+1}"
                else:
                    board[marble.pos] = f"M{player_idx+1}"

        print("Board:")
        for i in range(0, board_size, 12):
            print(" ".join(board[i:i+12]))

    def validate_total_cards(self) -> None:
        """Ensure the total number of cards remains consistent."""
        draw_count = len(self.state.list_card_draw)
        discard_count = len(self.state.list_card_discard)
        player_card_count = sum(len(player.list_card) for player in self.state.list_player)

        total_cards = draw_count + discard_count + player_card_count

        print(f"Debug: Draw pile count: {draw_count}, Discard pile count: {discard_count}, Player cards: {player_card_count}")
        print(f"Debug: Total cards: {total_cards}, Expected: {len(GameState.LIST_CARD)}")

        if total_cards != len(GameState.LIST_CARD):
            raise ValueError(f"Total cards mismatch: {total_cards} != {len(GameState.LIST_CARD)}")

    def get_list_action(self) -> List[Action]:
        """ Get a list of possible actions for the active player """
        if not self.state:
            return []
        actions = []
        active_player = self.state.list_player[self.state.idx_player_active]
        for card in active_player.list_card:
            actions.append(Action(card=card, pos_from=None, pos_to=None, card_swap=None))
        return actions

    def apply_action(self, action: Action) -> None:
        """ Apply the given action to the game """
        if not self.state:
            raise ValueError("Game state is not set.")

        # Handle the case where no action is provided (skip turn)
        if action is None:
            print(f"No action provided. Advancing the active player.")
            self.state.idx_player_active = (self.state.idx_player_active + 1) % len(self.state.list_player)

        else:
            print(f"Player {self.state.list_player[self.state.idx_player_active].name} plays {action.card.rank} of {action.card.suit}")
            
            # Remove the played card from the player's hand
            self.state.list_player[self.state.idx_player_active].list_card.remove(action.card)
            
            # Add the played card to the discard pile
            self.state.list_card_discard.append(action.card)

            # Update marble position if applicable
            safe_spaces = {
                0: [92, 93, 94, 95],  # Player 1's safe spaces
                1: [68, 69, 70, 71],  # Player 2's safe spaces
                2: [44, 45, 46, 47],  # Player 3's safe spaces
                3: [20, 21, 22, 23]   # Player 4's safe spaces
            }
            for marble in self.state.list_player[self.state.idx_player_active].list_marble:
                if marble.pos == action.pos_from:
                    marble.pos = action.pos_to
                    marble.is_save = marble.pos in safe_spaces[self.state.idx_player_active]

        # Advance to the next active player
        self.state.idx_player_active = (self.state.idx_player_active + 1) % len(self.state.list_player)

        # Check if all players are out of cards
        if all(len(player.list_card) == 0 for player in self.state.list_player):
            self.next_round()


    def get_cards_per_round(self) -> int:
        """Determine the number of cards to be dealt based on the round."""
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

    def deal_cards(self) -> None:
        """Deal cards to each player for the current round."""
        if not self.state:
            raise ValueError("Game state is not set.")

        num_cards = self.get_cards_per_round()
        total_needed = num_cards * self.state.cnt_player

        # Reshuffle if necessary
        while len(self.state.list_card_draw) < total_needed:
            if not self.state.list_card_discard:
                raise ValueError("Not enough cards to reshuffle and deal.")
            self.reshuffle_discard_into_draw()

        # Shuffle the draw pile
        random.shuffle(self.state.list_card_draw)

        # Deal cards to players
        starting_player_idx = self.state.idx_player_started
        for i in range(self.state.cnt_player):
            current_player_idx = (starting_player_idx + i) % self.state.cnt_player
            current_player = self.state.list_player[current_player_idx]
            current_player.list_card = [self.state.list_card_draw.pop() for _ in range(num_cards)]


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

        print(f"\nRound {self.state.cnt_round} begins. Player {self.state.list_player[self.state.idx_player_started].name} starts.")


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

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == '__main__':

    game = Dog()
    game.draw_board()  # Draw the initial board

    game.validate_total_cards()

    while game.state.phase != GamePhase.FINISHED:
        game.print_state()

        # Get the list of possible actions for the active player
        actions = game.get_list_action()
        # Display possible actions
        print("\nPossible Actions:")
        for idx, action in enumerate(actions):
            print(f"{idx}: Play {action.card.rank} of {action.card.suit}")

        # Select an action (random in this example)
        selected_action = random.choice(actions) if actions else None

        # Apply the selected action
        game.apply_action(selected_action)
        game.draw_board()  # Update the board after each action

        #debuging for deck management to see how many cards are in different piles
        game.validate_total_cards()

        # Optionally exit after a certain number of rounds (for testing)
        if game.state.cnt_round > 10:  # Example limit
            print(f"Ending game for testing after {game.state.cnt_round} rounds.")
            break