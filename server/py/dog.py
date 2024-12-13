from typing import List, Optional, ClassVar, Union, Tuple
from enum import Enum
import random
import copy
from pydantic import BaseModel
from server.py.game import Game, Player


class Card(BaseModel):
    suit: str
    rank: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return False
        return (self.suit, self.rank) == (other.suit, other.rank)

    def __str__(self) -> str:
        return f"Card(suit='{self.suit}', rank='{self.rank}')"

    def __repr__(self) -> str:
        return f"Card(suit='{self.suit}', rank='{self.rank}')"

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        suit_order = ['♠', '♥', '♦', '♣', '']
        rank_order = ['2','3','4','5','6','7','8','9','10','J','Q','K','A','JKR']
        return ((suit_order.index(self.suit), rank_order.index(self.rank)) <
                (suit_order.index(other.suit), rank_order.index(other.rank)))


class Marble(BaseModel):
    pos: int
    is_save: bool


class PlayerState(BaseModel):
    name: str
    list_card: List[Card]
    list_marble: List[Marble]


class Action(BaseModel):
    card: Optional[Card] = None
    pos_from: Optional[int] = None
    pos_to: Optional[int] = None
    card_swap: Optional[Card] = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Action):
            return False
        other_action: Action = other
        return (
            self.card == other_action.card and
            self.pos_from == other_action.pos_from and
            self.pos_to == other_action.pos_to and
            self.card_swap == other_action.card_swap
        )

    def __str__(self) -> str:
        card_str = str(self.card) if self.card else "None"
        swap_str = str(self.card_swap) if self.card_swap else "None"
        return f"card={card_str} pos_from={self.pos_from} pos_to={self.pos_to} card_swap={swap_str}"

    def __repr__(self) -> str:
        return (f"Action(card={repr(self.card)}, pos_from={self.pos_from}, "
                f"pos_to={self.pos_to}, card_swap={repr(self.card_swap)})")


class GamePhase(str, Enum):
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'


class GameState(BaseModel):
    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10',
        'J', 'Q', 'K', 'A', 'JKR'
    ]
    LIST_CARD: ClassVar[List[Card]] = [
        Card(suit=s, rank=r)
        for s in ['♠','♥','♦','♣'] for r in ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    ] + [Card(suit='', rank='JKR'), Card(suit='', rank='JKR'), Card(suit='', rank='JKR')]

    LIST_CARD = LIST_CARD * 2
    cnt_player: int
    phase: GamePhase
    cnt_round: int
    bool_card_exchanged: bool
    idx_player_started: int
    idx_player_active: int
    list_player: List[PlayerState]
    list_card_draw: List[Card]
    list_card_discard: List[Card]
    card_active: Optional[Card]


class RandomPlayer(Player):
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        if actions:
            return random.choice(actions)
        return None

    def do_nothing(self) -> None:
        pass


class Dog(Game):

    PLAYER_BOARD_SEGMENTS = {
        0: {'start': 0, 'queue_start': 64, 'final_start': 68},
        1: {'start': 16, 'queue_start': 72, 'final_start': 76},
        2: {'start': 32, 'queue_start': 80, 'final_start': 84},
        3: {'start': 48, 'queue_start': 88, 'final_start': 92}
    }

    MAIN_PATH_LENGTH = 64
    CARD_MOVEMENTS = {
        '2': 2,
        '3': 3,
        '4': -4,
        '5': 5,
        '6': 6,
        '8': 8,
        '9': 9,
        '10': 10,
        'Q': 12,
        'K': 13,
        'J': None
    }

    ACE_OPTIONS = [1, 11]
    JOKER_OPTIONS = list(range(1, 14))
    SEVEN_OPTIONS = list(range(1, 8))

    def __init__(self, cnt_players: int = 4) -> None:
        self.state: GameState
        self.temp_seven_moves: Optional[List[int]] = None
        self.temp_seven_card: Optional[Card] = None
        self.temp_joker_card: Optional[Card] = None
        self.temp_seven_state: Optional[GameState] = None
        self.turns_in_current_round: int = 0
        self.exchange_buffer: List[Optional[Card]] = [None] * cnt_players
        self._initialize_game(cnt_players)

    def _reset_card_active(self) -> None:
        self.state.card_active = None
        self.temp_seven_moves = None
        self.temp_seven_card = None
        self.temp_joker_card = None
        self.temp_seven_state = None

    def _find_player_card(self, player: PlayerState, card: Optional[Card]) -> Optional[Card]:
        if card is None:
            return None
        for c in player.list_card:
            if c.suit == card.suit and c.rank == card.rank:
                return c
        return None

    def _find_marble_by_pos(self, pos: int) -> Tuple[Optional[Marble], Optional[int]]:
        assert self.state is not None
        for p_idx, p in enumerate(self.state.list_player):
            for m in p.list_marble:
                if m.pos == pos:
                    return m, p_idx
        return None, None

    def _handle_jack_action(self, action: Action) -> None:
        assert self.state is not None
        pos_from = action.pos_from if action.pos_from is not None else -1
        pos_to = action.pos_to if action.pos_to is not None else -1
        fm, _fp = self._find_marble_by_pos(pos_from)
        tm, _tp = self._find_marble_by_pos(pos_to)
        if fm and tm:
            pos_tmp = fm.pos
            fm.pos = tm.pos
            tm.pos = pos_tmp

    def _initialize_game(self, cnt_players: int) -> None:
        """Initialize the game to its starting state"""
        if cnt_players not in [4]:
            raise ValueError("The game must be played with 4 players.")

        self.state = GameState(
            cnt_player=cnt_players,
            phase=GamePhase.SETUP,
            cnt_round=1,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=[],
            list_card_draw=[],
            list_card_discard=[],
            card_active=None
        )

        # Initialize card deck (two packs of Bridge-cards)
        self.state.list_card_draw = GameState.LIST_CARD.copy()   # Two packs of cards
        random.shuffle(self.state.list_card_draw)  # Shuffle the deck

        # Set up players
        for idx in range(self.state.cnt_player):
            list_card = [self.state.list_card_draw.pop() for _ in range(6)]  # Draw 6 cards for each player
            list_marble = [Marble(pos=None, is_save=False) for _ in range(4)]  # All marbles start in kennel
            player_state = PlayerState(name=f"Player {idx + 1}", list_card=list_card, list_marble=list_marble)
            self.state.list_player.append(player_state)

        # Randomly select the player who starts
        self.state.idx_player_started = random.randint(0, self.state.cnt_player - 1)
        self.state.idx_player_active = self.state.idx_player_started

        # Update the game phase after setup
        self.state.phase = GamePhase.RUNNING
        self.state.bool_card_exchanged = False  # Reset card exchange flag at the beginning

    def reset(self) -> None:
        """Setzt das Spiel in den Ausgangszustand zurück"""
        self._initialize_game(self.state.cnt_player)

    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        self.state = state

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        return self.state

    def print_state(self) -> None:
        """ Print the current game state """
        pass

    def setup_next_round(self) -> None:
        """ Setup the next round with decreasing number of cards """
        cards_in_round = [6, 5, 4, 3, 2]  # Anzahl der Karten für jede Runde (beginnend mit Runde 1)
        current_cards_count = cards_in_round[(self.state.cnt_round - 1) % len(cards_in_round)]
        # Deal cards to each player
        for player in self.state.list_player:
            player.list_card = [self.state.list_card_draw.pop() for _ in range(current_cards_count) if
                                self.state.list_card_draw]
        # TODO:: Test re-shuffle if stock out of cards (list_card_draw)

    def next_turn(self) -> None:
        """ Advance the turn to the next player """
        self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player
        # If all players have played, increase the round count
        if self.state.idx_player_active == self.state.idx_player_started:
            self.state.cnt_round += 1
            # self.exchange_cards() # TODO:: Exchange cards between players
            self.setup_next_round()  # Setup the next round with updated card counts


    def get_list_action(self) -> List[Action]:
        """ Get a list of possible actions for the active player """
        pass

    def apply_action(self, action: Action) -> None:
        """ Apply the given action to the game """
        if action is None:
            # print("No valid action provided. Skipping turn.")
            self.next_turn()
            return
        player = self.state.list_player[self.state.idx_player_active]
        # Remove the card from the player's hand
        player.list_card.remove(action.card)
        self.state.list_card_discard.append(action.card)
        # TODO:: Move the marble if applicable
        # Advance to the next player
        self.next_turn()

    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        pass

    def swap_cards(self, player1_idx: int, player2_idx: int, card1: Card, card2: Card) -> None:
        # Hole die Spielerobjekte
        player1 = self.state.list_player[player1_idx]
        player2 = self.state.list_player[player2_idx]

        # Überprüfe, ob Spieler 1 die angegebene Karte hat
        if card1 not in player1.list_card:
            raise ValueError(f"Player {player1_idx} does not have the card {card1}.")

        # Überprüfe, ob Spieler 2 die angegebene Karte hat
        if card2 not in player2.list_card:
            raise ValueError(f"Player {player2_idx} does not have the card {card2}.")

        # Entferne die Karte von Spieler 1 und füge sie zu Spieler 2 hinzu
        player1.list_card.remove(card1)
        player2.list_card.append(card1)

        # Entferne die Karte von Spieler 2 und füge sie zu Spieler 1 hinzu
        player2.list_card.remove(card2)
        player1.list_card.append(card2)

class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == '__main__':

    game = Dog()

    # Get the initial state of the game and print it
    initial_state = game.get_state()
    print("Initial Game State:")
    print(initial_state)

    # Simulate setting up the next rounds to see how the card distribution changes
    for round_num in range(1, 4):
        game.setup_next_round()
        print(f"\nGame State after setting up round {round_num + 1}:")
        print(game.get_state())

    # Simulate a few turns to see how the game progresses
    print("\nStarting turns simulation:")
    for turn in range(6):
        # Example of getting available actions (currently, not implemented)
        actions = game.get_list_action()
        if actions:
            # Apply a random action (using RandomPlayer logic as an example)
            action = random.choice(actions)
            game.apply_action(action)
        else:
            # If no valid actions, skip the turn
            game.next_turn()

        # Print the game state after each turn
        print(f"\nGame State after turn {turn + 1}:")
        print(game.get_state())

    # Reset the game and print the reset state
    game.reset()
    print("\nGame State after resetting:")
    print(game.get_state())