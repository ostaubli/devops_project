from typing import List, Optional, ClassVar, Union, Tuple # pylint: disable=unused-import
from enum import Enum
import random
import copy # pylint: disable=unused-import
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

    def _initialize_game(self, cnt_players: int) -> None:
        state = GameState(
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
        state.list_card_draw = GameState.LIST_CARD.copy()
        random.shuffle(state.list_card_draw)
        for idx in range(state.cnt_player):
            list_card = [state.list_card_draw.pop() for _ in range(6)]
            queue_start = self.PLAYER_BOARD_SEGMENTS[idx]['queue_start']
            list_marble = [Marble(pos=queue_start+i, is_save=False) for i in range(4)]
            player_state = PlayerState(name=f"Player {idx+1}", list_card=list_card, list_marble=list_marble)
            state.list_player.append(player_state)
        state.idx_player_started = random.randint(0, state.cnt_player - 1)
        state.idx_player_active = state.idx_player_started
        state.phase = GamePhase.RUNNING
        state.bool_card_exchanged = False
        self.state = state
        self.temp_seven_moves = None
        self.temp_seven_card = None
        self.temp_joker_card = None
        self.temp_seven_state = None

    def reset(self) -> None:
        assert self.state is not None
        self._initialize_game(self.state.cnt_player)

    def set_state(self, state: GameState) -> None:
        self.state = state

    def get_state(self) -> GameState:
        return self.state

    def print_state(self) -> None:
        pass

    def setup_next_round(self) -> None:
        assert self.state is not None
        cards_in_round = [6, 5, 4, 3, 2]
        if not self.state.list_card_draw and self.state.list_card_discard:
            self.state.list_card_draw = self.state.list_card_discard.copy()
            self.state.list_card_discard.clear()
            random.shuffle(self.state.list_card_draw)

        current_cards_count = cards_in_round[(self.state.cnt_round - 1) % len(cards_in_round)]
        for player in self.state.list_player:
            while len(player.list_card) < current_cards_count and self.state.list_card_draw:
                player.list_card.append(self.state.list_card_draw.pop())

    def next_turn(self) -> None:
        assert self.state is not None
        self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player
        self.turns_in_current_round += 1
        if self.turns_in_current_round == self.state.cnt_player:
            self.turns_in_current_round = 0
            self.state.cnt_round += 1
            self.setup_next_round()
            self.state.idx_player_started = (self.state.idx_player_started + 1) % self.state.cnt_player

    def _player_finished(self, idx: int) -> bool:
        assert self.state is not None
        final_start = self.PLAYER_BOARD_SEGMENTS[idx]['final_start']
        return all(m.pos >= final_start and m.pos < final_start+4 for m in self.state.list_player[idx].list_marble)

    def _controlled_player_indices(self) -> List[int]:
        assert self.state is not None
        my_idx = self.state.idx_player_active
        if self._player_finished(my_idx):
            return [my_idx, (my_idx+2)%self.state.cnt_player]
        return [my_idx]

    def _get_player_marbles(self) -> List[Marble]:
        assert self.state is not None
        indices = self._controlled_player_indices()
        marbles: List[Marble] = []
        for i in indices:
            marbles.extend(self.state.list_player[i].list_marble)
        return marbles

    def _get_start_actions(self, card: Card) -> List[Action]:
        assert self.state is not None
        actions: List[Action] = []
        startable_ranks = ['A', 'K', 'JKR']
        if card.rank in startable_ranks:
            player_idx = self.state.idx_player_active
            start_pos = self.PLAYER_BOARD_SEGMENTS[player_idx]['start']
            queue_start = self.PLAYER_BOARD_SEGMENTS[player_idx]['queue_start']
            blocked: Optional[bool] = None
            for p_i, p in enumerate(self.state.list_player):
                for m in p.list_marble:
                    if m.pos == start_pos and m.is_save:
                        blocked = p_i == player_idx
                        break
                if blocked is not None:
                    break
            if blocked is None:
                blocked = False
            if not blocked:
                player = self.state.list_player[player_idx]
                kennel_marbles = [m for m in player.list_marble if queue_start <= m.pos <= queue_start + 3]
                kennel_marbles.sort(key=lambda x: x.pos)
                if kennel_marbles:
                    front_marble = kennel_marbles[0]
                    if self.is_valid_move(front_marble.pos, start_pos):
                        actions.append(Action(card=Card(suit=card.suit, rank=card.rank),
                                              pos_from=front_marble.pos, pos_to=start_pos))
        return actions

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

    def _handle_jack_action(self, action: Action) -> None:  # pylint: disable=redefined-outer-name
        assert self.state is not None
        pos_from = action.pos_from if action.pos_from is not None else -1
        pos_to = action.pos_to if action.pos_to is not None else -1
        fm, _fp = self._find_marble_by_pos(pos_from)
        tm, _tp = self._find_marble_by_pos(pos_to)
        if fm and tm:
            pos_tmp = fm.pos
            fm.pos = tm.pos
            tm.pos = pos_tmp

    def _get_standard_actions(self, card: Card, move_distance: Union[int, List[int]]) -> List[Action]:
        assert self.state is not None
        actions: List[Action] = []
        controlled_indices = self._controlled_player_indices()
        marbles: List[Marble] = []
        for i in controlled_indices:
            marbles.extend(self.state.list_player[i].list_marble)
        def try_move(marble: Marble, dist: int) -> None:
            if marble.pos >= self.MAIN_PATH_LENGTH and card.rank not in ['A','K','JKR']:
                return
            pos_to = self._calc_pos_to(marble.pos, dist, self.state.idx_player_active, card.rank)
            if pos_to is not None and self.is_valid_move(marble.pos, pos_to):
                actions.append(Action(card=Card(suit=card.suit, rank=card.rank), pos_from=marble.pos, pos_to=pos_to))
        if isinstance(move_distance, list):
            for distance in move_distance:
                for mb in marbles:
                    try_move(mb, distance)
        else:
            for mb in marbles:
                try_move(mb, move_distance)
        return actions

    def _get_actions_for_card(self, c: Card) -> List[Action]:
        possible_actions: List[Action] = []
        start_actions = self._get_start_actions(Card(suit=c.suit, rank=c.rank))
        if c.rank == 'J':
            possible_actions.extend(self._get_jack_actions(Card(suit=c.suit, rank=c.rank)))
            possible_actions.extend(start_actions)
        elif c.rank == '7':
            possible_actions.extend(start_actions)
            possible_actions.extend(
                self._get_standard_actions(Card(suit=c.suit, rank=c.rank), self.SEVEN_OPTIONS))
        elif c.rank == 'JKR':
            possible_actions.extend(self._get_actions_for_joker(c, start_actions))
        else:
            move_distance = self.get_move_distance(c)
            if move_distance is not None and c.rank not in ['J', '7', 'JKR']:
                possible_actions.extend(start_actions)
                possible_actions.extend(self._get_standard_actions(Card(suit=c.suit, rank=c.rank), move_distance))
        return possible_actions

    def get_list_action(self) -> List[Action]:
        assert self.state is not None
        if self.state.cnt_round == 0 and self.state.card_active is None and not self.state.bool_card_exchanged:
            return self._unique_sorted_actions(
                [Action(card=Card(suit=c.suit, rank=c.rank), pos_from=None, pos_to=None)
                 for c in self.state.list_player[self.state.idx_player_active].list_card]
            )
        if self.state.card_active and self.state.card_active.rank == '7':
            return self._get_actions_for_seven_card()
        card_list = (self.state.list_player[self.state.idx_player_active].list_card
                     if self.state.card_active is None
                     else [self.state.card_active])
        possible_actions: List[Action] = []
        for c in card_list:
            if self.state.card_active is None:
                possible_actions.extend(self._get_actions_for_card(c))
            else:
                if self.state.card_active.rank == '7':
                    continue
                move_distance = self.get_move_distance(self.state.card_active)
                if move_distance is not None and self.state.card_active is not None:
                    possible_actions.extend(self._get_standard_actions(self.state.card_active, move_distance))
        return self._unique_sorted_actions(possible_actions)

    def _unique_sorted_actions(self, actions: List[Action]) -> List[Action]:
        unique_actions: List[Action] = []
        for a in actions:
            if a not in unique_actions:
                unique_actions.append(a)
        unique_actions = sorted(unique_actions, key=lambda x: (
            str(x.card),
            x.pos_from if x.pos_from is not None else -999,
            x.pos_to if x.pos_to is not None else -999,
            str(x.card_swap) if x.card_swap else ''
        ))
        return unique_actions

    def apply_action(self, action: Action) -> None:  # pylint: disable=redefined-outer-name
        """ Apply the given action to the game """
        if action is None:
            # print("No valid action provided. Skipping turn.")
            self.next_turn()
            return

        if action.card is None:
            raise ValueError("Invalid action: No card provided.")

        player = self.state.list_player[self.state.idx_player_active]
        # Remove the card from the player's hand
        player.list_card.remove(action.card)
        self.state.list_card_discard.append(action.card)
        # Advance to the next player
        self.next_turn()

    def check_game_status(self) -> None:
        assert self.state is not None
        for player in self.state.list_player:
            player_idx = self.state.list_player.index(player)
            final_start = self.PLAYER_BOARD_SEGMENTS[player_idx]['final_start']
            if all(marble.pos >= final_start and marble.pos < final_start+4 for marble in player.list_marble):
                self.state.phase = GamePhase.FINISHED
                break

    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        return self.state

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
        ACTIONS = game.get_list_action()
        if ACTIONS:
            # Apply a random action (using RandomPlayer logic as an example)
            action = random.choice(ACTIONS)
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
