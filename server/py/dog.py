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

    def _calc_steps(self, pos_from: int, pos_to: int, player_idx: int) -> Optional[int]:
        assert self.state is not None
        final_start = self.PLAYER_BOARD_SEGMENTS[player_idx]['final_start']
        start = self.PLAYER_BOARD_SEGMENTS[player_idx]['start']
        queue_start = self.PLAYER_BOARD_SEGMENTS[player_idx]['queue_start']
        result: Optional[int] = None
        if queue_start <= pos_from <= queue_start + 3 and pos_to == start:
            result = 1
        elif pos_from >= final_start:
            if pos_to < final_start or pos_to < pos_from:
                result = None
            else:
                result = pos_to - pos_from
        elif pos_to >= final_start:
            steps_finish = self._count_steps_to_finish(pos_from, start, final_start)
            diff = pos_to - final_start
            if diff < 0 or diff > 3:
                result = None
            else:
                result = steps_finish + diff
        else:
            if self.state.card_active and self.state.card_active.rank == '4':
                d = (pos_to - pos_from) % self.MAIN_PATH_LENGTH
                d2 = (pos_from - pos_to) % self.MAIN_PATH_LENGTH
                if d2 == 4:
                    result = -4
                elif d == 4:
                    result = 4
                else:
                    result = None
            else:
                dist = (pos_to - pos_from) % self.MAIN_PATH_LENGTH
                result = dist if dist != 0 else None
        return result

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

    def _get_safe_marble_actions_for_jack(self, safe_marbles: List[Marble], card: Card) -> List[Action]:
        actions: List[Action] = []
        done_pairs = set()
        for i, marble_i in enumerate(safe_marbles):
            for marble_j in safe_marbles[i + 1:]:
                if ((marble_i.pos, marble_j.pos) not in done_pairs and
                        (marble_j.pos, marble_i.pos) not in done_pairs):
                    actions.append(Action(card=Card(suit=card.suit, rank=card.rank),
                                          pos_from=marble_i.pos, pos_to=marble_j.pos))
                    actions.append(Action(card=Card(suit=card.suit, rank=card.rank),
                                          pos_from=marble_j.pos, pos_to=marble_i.pos))
                    done_pairs.add((marble_i.pos, marble_j.pos))
                    done_pairs.add((marble_j.pos, marble_i.pos))
        return actions

    def _get_jack_actions(self, card: Card) -> List[Action]:
        assert self.state is not None
        controlled = self._controlled_player_indices()
        my_marbles = [
            m
            for i in controlled
            for m in self.state.list_player[i].list_marble
            if m.pos < self.MAIN_PATH_LENGTH
        ]
        opponent_marbles: List[int] = []
        for p_idx, p in enumerate(self.state.list_player):
            if p_idx not in controlled:
                opponent_marbles.extend(
                    mm.pos
                    for mm in p.list_marble
                    if mm.pos < self.MAIN_PATH_LENGTH and not (
                            mm.pos == self.PLAYER_BOARD_SEGMENTS[p_idx]['start'] and mm.is_save
                    )
                )
        actions: List[Action] = [
            Action(card=Card(suit=card.suit, rank=card.rank), pos_from=mm.pos, pos_to=o_pos)
            for mm in my_marbles
            for o_pos in opponent_marbles
        ]
        actions += [
            Action(card=Card(suit=card.suit, rank=card.rank), pos_from=o_pos, pos_to=mm.pos)
            for mm in my_marbles
            for o_pos in opponent_marbles
        ]
        safe_marbles = [
            m
            for i in controlled
            for m in self.state.list_player[i].list_marble
            if m.pos < self.MAIN_PATH_LENGTH and m.is_save
        ]
        if not actions and len(safe_marbles) >= 2:
            actions.extend(self._get_safe_marble_actions_for_jack(safe_marbles, card))
        return actions

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

    def _calc_pos_to(self, pos_from: int, dist: int, player_idx: int, rank: str) -> Optional[int]:
        assert self.state is not None
        start = self.PLAYER_BOARD_SEGMENTS[player_idx]['start']
        final_start = self.PLAYER_BOARD_SEGMENTS[player_idx]['final_start']
        if pos_from >= self.MAIN_PATH_LENGTH and rank not in ['A', 'K', 'JKR']:
            return None
        pos_new: Optional[int] = None
        if rank == '4' and dist < 0:
            pos_test = (pos_from + dist) % self.MAIN_PATH_LENGTH
            pos_new = None if pos_test >= self.MAIN_PATH_LENGTH else pos_test
        elif pos_from < self.MAIN_PATH_LENGTH:
            steps_to_finish = self._count_steps_to_finish(pos_from, start, final_start)
            if 0 < dist <= steps_to_finish:
                diff = dist - steps_to_finish
                pos_test = final_start + diff
                pos_new = None if pos_test >= final_start + 4 else pos_test
            else:
                pos_new = (pos_from + dist) % self.MAIN_PATH_LENGTH
        else:
            pos_test = pos_from + dist
            pos_new = None if (pos_test < final_start or pos_test >= final_start + 4) else pos_test
        return pos_new

    def _count_steps_to_finish(self, pos_from: int, start: int, final_start: int) -> int:
        if final_start < self.MAIN_PATH_LENGTH:
            pf = pos_from
            if pf < start:
                pf += self.MAIN_PATH_LENGTH
            return (final_start - pf) % self.MAIN_PATH_LENGTH
        pf = pos_from
        if pf < start:
            dist_to_loop_end = self.MAIN_PATH_LENGTH - pf
            dist_finish = final_start - self.MAIN_PATH_LENGTH
            return dist_to_loop_end + dist_finish
        dist_main = self.MAIN_PATH_LENGTH - pf
        dist_finish = final_start - self.MAIN_PATH_LENGTH
        return dist_main + dist_finish

    def _get_actions_for_seven_card(self) -> List[Action]:
        assert self.state is not None
        if self.temp_seven_moves is None:
            return []
        used_steps = sum(self.temp_seven_moves) if self.temp_seven_moves else 0
        if used_steps == 7:
            return []
        left = 7 - used_steps
        controlled_indices = self._controlled_player_indices()
        marbles = [m for i in controlled_indices for m in self.state.list_player[i].list_marble]
        final_start = self.PLAYER_BOARD_SEGMENTS[self.state.idx_player_active]['final_start']
        in_finish = any(mb.pos is not None and mb.pos >= final_start for mb in marbles)
        move_distance = [left] if in_finish else [x for x in self.SEVEN_OPTIONS if x <= left]
        assert self.state.card_active is not None
        all_actions = self._get_standard_actions(self.state.card_active, move_distance)
        if in_finish:
            assert self.temp_seven_state is not None
            originally = {(p_i, idx): m.pos for p_i, p in enumerate(self.temp_seven_state.list_player)
                          for idx, m in enumerate(p.list_marble)}
            now = {(p_i, idx): m.pos for p_i, p in enumerate(self.state.list_player)
                   for idx, m in enumerate(p.list_marble)}
            moved_marbles = [key for key in now if now[key] != originally[key]]
            filtered_actions = [
                act for act in all_actions if any(
                    mm.pos == act.pos_from and (pp_i, idx) in moved_marbles
                    for pp_i, pl in enumerate(self.state.list_player)
                    for idx, mm in enumerate(pl.list_marble)
                )
            ]
            return self._unique_sorted_actions(filtered_actions)
        return self._unique_sorted_actions(all_actions)

    def _get_actions_for_joker(self, c: Card, start_actions: List[Action]) -> List[Action]:
        assert self.state is not None
        possible_actions: List[Action] = []
        all_ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A', 'J', 'K', 'Q']
        list_suit = ['♠', '♥', '♦', '♣']
        if self.state.cnt_round == 0 and self.state.bool_card_exchanged:
            if start_actions:
                possible_actions.extend(start_actions)
                for suitx in list_suit:
                    possible_actions.append(Action(card=Card(suit='', rank='JKR'), pos_from=None, pos_to=None,
                                                   card_swap=Card(suit=suitx, rank='A')))
                    possible_actions.append(Action(card=Card(suit='', rank='JKR'), pos_from=None, pos_to=None,
                                                   card_swap=Card(suit=suitx, rank='K')))
            else:
                for suitx in list_suit:
                    for r in all_ranks:
                        possible_actions.append(Action(card=Card(suit='', rank='JKR'),
                                                       pos_from=None, pos_to=None,
                                                       card_swap=Card(suit=suitx, rank=r)))
        else:
            possible_actions.extend(start_actions)
            for r in all_ranks:
                possible_actions.append(Action(card=Card(suit=c.suit, rank=c.rank),
                                               pos_from=None, pos_to=None,
                                               card_swap=Card(suit='♥', rank=r)))
            possible_actions.extend(self._get_standard_actions(Card(suit=c.suit, rank=c.rank), self.JOKER_OPTIONS))
        return possible_actions

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

    def is_valid_move(self, pos_from: int, pos_to: int) -> bool:
        assert self.state is not None
        player_idx = self.state.idx_player_active
        final_start = self.PLAYER_BOARD_SEGMENTS[player_idx]['final_start']
        start_pos = self.PLAYER_BOARD_SEGMENTS[player_idx]['start']
        result = True
        if pos_from >= self.MAIN_PATH_LENGTH:
            if pos_to != start_pos or not self._can_start(start_pos):
                result = False
        elif pos_to >= final_start + 4:
            result = False
        elif not self._path_clear(pos_from, pos_to, player_idx):
            result = False
        else:
            for p_i, p in enumerate(self.state.list_player):
                player_final_start = self.PLAYER_BOARD_SEGMENTS[p_i]['final_start']
                if pos_to >= player_final_start and any(m.pos == pos_to for m in p.list_marble):
                    result = False
                    break
        return result

    def _can_start(self, start_pos: int) -> bool:
        assert self.state is not None
        player_idx = self.state.idx_player_active
        for p_i, p in enumerate(self.state.list_player):
            for m in p.list_marble:
                if m.pos == start_pos and m.is_save:
                    if p_i == player_idx:
                        return False
        return True

    def _blocked_on_main_path(self, p: int) -> bool:
        assert self.state is not None
        starts = {0, 16, 32, 48}
        for pl_st in self.state.list_player:
            for mm in pl_st.list_marble:
                if mm.pos == p and mm.is_save and (p in starts or p < self.MAIN_PATH_LENGTH):
                    return True
        return False

    def _move_through_main_path(self, start_pos: int, steps: int, direction: int = 1) -> bool:
        assert self.state is not None
        cur = start_pos
        for _ in range(steps):
            cur = (cur + direction) % self.MAIN_PATH_LENGTH
            if self._blocked_on_main_path(cur):
                return False
        return True

    def _move_through_final_area(self, fs: int, steps: int) -> bool:
        assert self.state is not None
        for step in range(steps):
            np = fs + step
            for pl_st in self.state.list_player:
                for mm in pl_st.list_marble:
                    if mm.pos == np:
                        return False
        return True

    def _path_clear(self, pos_from: int, pos_to: int, player_idx: int) -> bool:
        assert self.state is not None
        if pos_from >= self.MAIN_PATH_LENGTH and pos_to < self.MAIN_PATH_LENGTH:
            return False
        fs = self.PLAYER_BOARD_SEGMENTS[player_idx]['final_start']
        st = self.PLAYER_BOARD_SEGMENTS[player_idx]['start']
        plen = self.MAIN_PATH_LENGTH if pos_from < fs else 64
        dist = (pos_to - pos_from) % plen
        direction = 1
        c = self.state.card_active
        if c and c.rank == '4':
            bd = (pos_from - pos_to) % self.MAIN_PATH_LENGTH
            fd = (pos_to - pos_from) % self.MAIN_PATH_LENGTH
            if bd == 4:
                direction = -1
                dist = 4
            elif fd == 4:
                dist = 4
        if pos_to < fs:
            return self._move_through_main_path(pos_from, dist, direction)
        stf = self._count_steps_to_finish(pos_from, st, fs)
        if dist <= stf:
            return self._move_through_main_path(pos_from, dist, 1)
        if not self._move_through_main_path(pos_from, stf, 1):
            return False
        diff = dist - stf
        return self._move_through_final_area(fs, diff)

    def apply_action(self, action: Optional[Action]) -> None:
        assert self.state is not None
        player = self.state.list_player[self.state.idx_player_active]
        if action is None:
            self._handle_no_action(player)
            return
        if action.pos_from == -1 and action.pos_to == -1 and action.card is not None and action.card_swap is None:
            self._handle_card_exchange(player, action)
            return
        if action.card and action.card.rank == 'JKR' and action.card_swap:
            self._handle_joker_swap(player, action)
            return
        found_card = self._find_player_card(player, action.card)
        if found_card and found_card.rank == '7':
            self._handle_card_7(player, found_card, action)
        elif found_card and found_card.rank == 'JKR':
            self._handle_card_joker(player, found_card, action)
        elif found_card and found_card.rank == 'J':
            self._handle_card_j(player, found_card, action)
        elif found_card:
            self._handle_card_other(player, found_card, action)
        else:
            self._handle_active_card_move(player, action)
        self.check_game_status()

    def check_game_status(self) -> None:
        assert self.state is not None
        for player in self.state.list_player:
            player_idx = self.state.list_player.index(player)
            final_start = self.PLAYER_BOARD_SEGMENTS[player_idx]['final_start']
            if all(marble.pos >= final_start and marble.pos < final_start+4 for marble in player.list_marble):
                self.state.phase = GamePhase.FINISHED
                break

    def get_move_distance(self, card: Card) -> Optional[Union[int, List[int]]]:
        if card.rank in self.CARD_MOVEMENTS:
            return self.CARD_MOVEMENTS[card.rank]
        if card.rank == 'A':
            return self.ACE_OPTIONS
        if card.rank == '7':
            return self.SEVEN_OPTIONS
        if card.rank == 'JKR':
            return self.JOKER_OPTIONS
        return None

    def get_player_view(self, idx_player: int) -> GameState:
        return self.state

    def _handle_no_action(self, player: PlayerState) -> None:
        assert self.state is not None
        if not self.get_list_action():
            if player.list_card:
                self.state.list_card_discard.extend(player.list_card)
                player.list_card.clear()
            if (self.state.card_active and self.state.card_active.rank == '7' and
                    self.temp_seven_moves and sum(self.temp_seven_moves) < 7):
                assert self.temp_seven_state is not None
                self.state = self.temp_seven_state
            self._reset_card_active()
        if not (self.state.cnt_round == 0 and not self.state.bool_card_exchanged):
            self.next_turn()
        self.check_game_status()

    def _handle_card_exchange(self, player: PlayerState, action: Action) -> None:
        assert self.state is not None
        if action.pos_from is None and action.pos_to is None and action.card is not None and action.card_swap is None:
            found_card: Optional[Card] = None
            for c in player.list_card:
                if c.suit == action.card.suit and c.rank == action.card.rank:
                    found_card = c
                    break
            if found_card is not None:
                player.list_card.remove(found_card)
                self.exchange_buffer[self.state.idx_player_active] = found_card
            if self.state.cnt_round == 0 and not self.state.bool_card_exchanged:
                all_chosen = all(card is not None for card in self.exchange_buffer)
                if all_chosen:
                    for p_idx in range(self.state.cnt_player):
                        chosen_card = self.exchange_buffer[p_idx]
                        if chosen_card is not None:
                            partner_idx = (p_idx + 2) % self.state.cnt_player
                            self.state.list_player[partner_idx].list_card.append(chosen_card)
                    self.exchange_buffer = [None] * self.state.cnt_player
                    self.state.bool_card_exchanged = True
            self._reset_card_active()
            self.check_game_status()

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
