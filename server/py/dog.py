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
    list_card_draw: List[Card]      # list of cards to draw
    list_card_discard: List[Card]   # list of cards discarded
    card_active: Optional[Card]        # active card (for 7 and JKR with sequence of actions)

class Dog(Game):
    # Constants
    STARTING_CARDS = {'A', 'K', 'JKR'}
    MOVEMENT_CARDS = {'2', '3', '4', '5', '6', '8', '9', '10', 'Q', 'K', 'A', 'JKR'}
    INVALID_POSITIONS = {'kennel', 'finish'}

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """
        self.state: Optional[GameState] = None
        self.initialize_game()  # Ensure the game state is initialized

    def initialize_game(self) -> None:
        """
        Initialize the game state with players, deck, and board positions.

        Each player (i: range 0-3) has 4 marbles (j: range 0-3), initialized from unique positions (pos).
        """

        players = [PlayerState(name=f"Player {i+1}", list_card=[], list_marble=[Marble(pos=i*24 + j, is_save=True) for j in range(4)]) for i in range(4)]
        deck = GameState.LIST_CARD.copy()
        random.shuffle(deck)
        board_positions = [None] * 96  # Initialize board positions

        # Deal initial cards (6 cards in first round)
        for player in players:
            player.list_card = [deck.pop() for _ in range(6)]

        self.state = GameState(
            cnt_player=4,
            phase=GamePhase.RUNNING,
            cnt_round=1,
            bool_game_finished=False,
            bool_card_exchanged=False,
            idx_player_started=random.randint(0, 3),
            idx_player_active=random.randint(0, 3),
            list_player=players,
            list_card_draw=deck,
            list_card_discard=[],
            card_active=None,
            board_positions=board_positions
        )

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
    
    def _get_card_value(self, card: Card) -> int:
        """Map card rank to its movement value."""
        if card.rank == 'A':
            return 1
        elif card.rank == 'Q':
            return 12
        elif card.rank == 'K':
            return 13
        elif card.rank.isdigit():
            return int(card.rank)
        elif card.rank == 'JKR':
            return 1
        elif card.rank == '4':
            return -4
        elif card.rank == '7':
            return 7
        return 0

    def _calculate_new_position(self, current_pos: int, move_value: int, forward: bool = True) -> int:
        """Calculate the new position of a marble on the board."""
        board_size = 96  # Total board positions
        if forward:
            return (current_pos + move_value) % board_size
        else:
            return (current_pos - move_value) % board_size

    def _generate_split_moves(self, total: int, current_pos: int) -> List[Action]:
        """Generate all possible split moves for a SEVEN card."""
        splits = []
        for i in range(1, total):
            first_move = self._calculate_new_position(current_pos, i, forward=True)
            second_move = self._calculate_new_position(first_move, total - i, forward=True)
            
            # Ensure `pos_to` is an integer
            splits.append(Action(
                card=Card(suit="", rank="7"),
                pos_from=current_pos,
                pos_to=int(second_move),  # Ensure integer
                card_swap=None
            ))
        return splits

    def get_list_action(self) -> List[Action]:
        """Get list of possible actions for active player"""
        if not self.state:
            return []

        actions = []
        active_player = self.state.list_player[self.state.idx_player_active]

        # Check if in first round (cnt_round = 0)
        if self.state.cnt_round == 0:
            # Only allow moves with start cards (A, K, JKR)
            for card in active_player.list_card:
                if card.rank in ['A', 'K', 'JKR']:
                    # Add action to move from kennel to start
                    actions.append(Action(
                        card=card,
                        pos_from=64,  # Kennel position
                        pos_to=0,     # Start position
                        card_swap=None
                    ))
            return actions

        # Regular game moves
        for card in active_player.list_card:
            if card.rank in self.MOVEMENT_CARDS:
                move_value = self._get_card_value(card)
                for marble in active_player.list_marble:
                    if marble.pos not in self.INVALID_POSITIONS:
                        pos_to = self._calculate_new_position(marble.pos, move_value)
                        actions.append(Action(
                            card=card,
                            pos_from=marble.pos,
                            pos_to=pos_to,
                            card_swap=None
                        ))

            # Handle specific rules for SEVEN (split moves)
            if card.rank == '7':
                # Generate all possible split combinations
                for marble in active_player.list_marble:
                    if marble.pos not in self.INVALID_POSITIONS:
                        splits = self._generate_split_moves(7, marble.pos)
                        for split_action in splits:
                            actions.append(split_action)

        return actions
 
    def apply_action(self, action: Action) -> None:
        """ Apply the given action to the game """
        if not self.state:
            raise ValueError("Game state is not set.")
        print(f"Player {self.state.list_player[self.state.idx_player_active].name} plays {action.card.rank} of {action.card.suit}")
        self.state.list_player[self.state.idx_player_active].list_card.remove(action.card)
        self.state.list_card_discard.append(action.card)

        # Update marble position and check if it is in the safe space
        safe_spaces = {
            0: [92, 93, 94, 95],  # Player 1's safe spaces
            1: [68, 69, 70, 71],  # Player 2's safe spaces
            2: [44, 45, 46, 47],  # Player 3's safe spaces
            3: [20, 21, 22, 23]   # Player 4's safe spaces
        }
        for marble in self.state.list_player[self.state.idx_player_active].list_marble:
            if marble.pos == action.pos_from:
                marble.pos = action.pos_to
                if marble.pos in safe_spaces[self.state.idx_player_active]:
                    marble.is_save = True
                else:
                    marble.is_save = False

        self.state.idx_player_active = (self.state.idx_player_active + 1) % len(self.state.list_player)

        # Check if the round is complete (all players have played)
        if self.state.idx_player_active == self.state.idx_player_started:
            self.state.cnt_round += 1  # Increment the round number

    def draw_card(self) -> None:
        """ Draw a card for the active player """
        if not self.state:
            raise ValueError("Game state is not set.")
        if not self.state.list_card_draw:
            print("No more cards to draw. The game is finished.")
            self.state.phase = GamePhase.FINISHED
            return
        card = self.state.list_card_draw.pop()
        self.state.list_player[self.state.idx_player_active].list_card.append(card)

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
    game.initialize_game()
    game.draw_board()  # Draw the board

    while game.state.phase != GamePhase.FINISHED:
        game.print_state()
        game.draw_card()  # Draw a card for the active player
        actions = game.get_list_action()

        # Display possible actions
        print("\nPossible Actions:")
        for idx, action in enumerate(actions):
            print(f"{idx}: Play {action.card.rank} of {action.card.suit}")

        # Randomly select an action for the active player
        selected_action = random.choice(actions)
        game.apply_action(selected_action)
        game.draw_board()  # Update the board after each action
