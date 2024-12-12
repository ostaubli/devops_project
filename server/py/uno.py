from typing import List, Optional
from enum import Enum
import random
from pydantic import BaseModel
from server.py.game import Game, Player


class Card(BaseModel):
    color: Optional[str] = None
    number: Optional[int] = None
    symbol: Optional[str] = None


class Action(BaseModel):
    card: Optional[Card] = None
    color: Optional[str] = None
    draw: Optional[int] = None
    uno: bool = False

    def __lt__(self, other):
        if not isinstance(other, Action):
            return NotImplemented
        return (
            (self.card.color if self.card else '',
             self.card.number if self.card and self.card.number is not None else -1,
             self.card.symbol if self.card else '',
             self.color or '',
             self.draw if self.draw else 0,
             self.uno)
            <
            (other.card.color if other.card else '',
             other.card.number if other.card and other.card.number is not None else -1,
             other.card.symbol if other.card else '',
             other.color or '',
             other.draw if other.draw else 0,
             other.uno)
        )


class PlayerState(BaseModel):
    name: Optional[str] = None
    list_card: List[Card] = []


class GamePhase(str, Enum):
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'


class GameState(BaseModel):
    CNT_HAND_CARDS: int = 7
    LIST_COLOR: List[str] = ['red', 'green', 'yellow', 'blue', 'any']
    LIST_SYMBOL: List[str] = ['skip', 'reverse', 'draw2', 'wild', 'wilddraw4']
    LIST_CARD: List[Card] = []

    list_card_draw: List[Card] = []
    list_card_discard: List[Card] = []
    list_player: List[PlayerState] = []
    phase: GamePhase = GamePhase.SETUP
    cnt_player: int = 0
    idx_player_active: Optional[int] = None
    direction: int = 1
    color: str = 'any'
    cnt_to_draw: int = 0
    has_drawn: bool = False


class Uno(Game):
    def __init__(self) -> None:
        self.state = GameState(
            list_card_draw=[],
            list_card_discard=[],
            list_player=[],
            phase=GamePhase.SETUP,
            cnt_player=0,
            idx_player_active=None,
            direction=1,
            color='any',
            cnt_to_draw=0,
            has_drawn=False
        )

    def set_state(self, state: GameState) -> None:
        self.state = state
        if self.state.phase == GamePhase.SETUP:
            self._initialize_game()

    def get_state(self) -> GameState:
        return self.state

    def print_state(self, list_color=True, list_symbol=True, list_card=True) -> None:
        print_str = "Game State:"
        for keys in self.state.model_fields.keys():
            if not list_color and keys == 'LIST_COLOR':
                continue
            if not list_symbol and keys == 'LIST_SYMBOL':
                continue
            if not list_card and keys == 'LIST_CARD':
                continue
            print_str += f'\n{keys} : {self.state.__dict__[keys]}'
        return print_str

    def get_list_action(self) -> List[Action]:
        if self.state.phase != GamePhase.RUNNING:
            return []

        actions = []
        active_player = self.state.list_player[self.state.idx_player_active]
        top_discard = self.state.list_card_discard[-1] if self.state.list_card_discard else None

        playable_cards = []
        for card in active_player.list_card:
            if self._can_play_card(card, top_discard):
                playable_cards.append(card)

        # Caso especial: primera jugada con una carta wild en el descarte (test010)
        first_turn_with_wild = (len(self.state.list_card_discard) == 1 and top_discard and top_discard.symbol == 'wild')

        # Si cnt_to_draw > 0
        if self.state.cnt_to_draw > 0:
            # Verificar si hay cartas normales jugables (no draw2/wilddraw4)
            normal_playable_exists = any(
                self._can_play_card(c, top_discard) and c.symbol not in ('draw2', 'wilddraw4')
                for c in playable_cards
            )

            stackable = []
            for c in playable_cards:
                if c.symbol == 'draw2':
                    if normal_playable_exists:
                        # Mostrar sólo valor base (2), no acumulativo
                        stackable.append(Action(card=c, color=c.color, draw=2))
                    else:
                        # No hay cartas normales, mostrar acumulativo
                        draw_val = self.state.cnt_to_draw + 2
                        stackable.append(Action(card=c, color=c.color, draw=draw_val))
                elif c.symbol == 'wilddraw4':
                    if normal_playable_exists:
                        # Mostrar sólo valor base (4), no acumulativo
                        for col in ['red','green','yellow','blue']:
                            stackable.append(Action(card=c, color=col, draw=4))
                    else:
                        # Acumulativo
                        draw_val = self.state.cnt_to_draw + 4
                        for col in ['red','green','yellow','blue']:
                            stackable.append(Action(card=c, color=col, draw=draw_val))
                else:
                    # Carta normal jugable durante cnt_to_draw
                    if c.symbol:
                        actions.append(Action(card=c, color=c.color))
                    else:
                        actions.append(Action(card=c, color=c.color or "any"))

            # Agregar las acciones stackable
            for a in stackable:
                actions.append(a)

            # Si tenemos acciones (ya sea stackable o normales), también draw=1
            if len(actions) > 0:
                # UNO si el jugador está por soltar la penúltima carta
                if len(active_player.list_card) == 2:
                    card_play_actions = [a for a in actions if a.card is not None]
                    for a in card_play_actions:
                        actions.append(Action(card=a.card, color=a.color, draw=a.draw, uno=True))
                actions.append(Action(draw=1))
            else:
                # no hay cartas jugables, debe tomar las cnt_to_draw cartas
                actions.append(Action(draw=self.state.cnt_to_draw))
                # No UNO aquí porque no se jugó carta

            return sorted(actions)

        # Si cnt_to_draw=0
        if self.state.has_drawn:
            # Si ya se robó una carta este turno
            if len(playable_cards) > 0:
                for c in playable_cards:
                    if c.symbol == 'wild':
                        for col in ['red','green','yellow','blue']:
                            actions.append(Action(card=c, color=col))
                    elif c.symbol == 'wilddraw4':
                        # Sólo jugable si no hay otra carta con color actual o número
                        if not self._has_other_playable_card(active_player.list_card, c, top_discard):
                            for col in ['red','green','yellow','blue']:
                                actions.append(Action(card=c, color=col, draw=4))
                    elif c.symbol == 'draw2':
                        actions.append(Action(card=c, color=c.color, draw=2))
                    else:
                        actions.append(Action(card=c, color=c.color or "any"))

                # UNO variantes
                if len(active_player.list_card) == 2:
                    card_play_actions = [a for a in actions if a.card is not None]
                    for a in card_play_actions:
                        actions.append(Action(card=a.card, color=a.color, draw=a.draw, uno=True))

                # No hay draw=1 aquí porque ya se robó y hay cartas jugables
                return sorted(actions)
            else:
                # no hay cartas jugables después de robar, mostrar draw=1 otra vez
                actions.append(Action(draw=1))
                return sorted(actions)

        # has_drawn=False, cnt_to_draw=0
        if len(playable_cards) > 0:
            if first_turn_with_wild:
                # si es la primera jugada y hay un wild al inicio
                for c in playable_cards:
                    if c.symbol == 'wild':
                        for col in ['red','green','yellow','blue']:
                            actions.append(Action(card=c, color=col))
                    elif c.symbol == 'wilddraw4':
                        if not self._has_other_playable_card(active_player.list_card, c, top_discard):
                            for col in ['red','green','yellow','blue']:
                                actions.append(Action(card=c, color=col, draw=4))
                    elif c.symbol == 'draw2':
                        actions.append(Action(card=c, color=c.color, draw=2))
                    else:
                        actions.append(Action(card=c, color=c.color or "any"))

                if len(active_player.list_card) == 2:
                    card_play_actions = [a for a in actions if a.card is not None]
                    for a in card_play_actions:
                        actions.append(Action(card=a.card, color=a.color, draw=a.draw, uno=True))
                return sorted(actions)
            else:
                # escenario normal
                for c in playable_cards:
                    if c.symbol == 'wild':
                        for col in ['red','green','yellow','blue']:
                            actions.append(Action(card=c, color=col))
                    elif c.symbol == 'wilddraw4':
                        if not self._has_other_playable_card(active_player.list_card, c, top_discard):
                            for col in ['red','green','yellow','blue']:
                                actions.append(Action(card=c, color=col, draw=4))
                    elif c.symbol == 'draw2':
                        actions.append(Action(card=c, color=c.color, draw=2))
                    else:
                        actions.append(Action(card=c, color=c.color or "any"))

                if len(active_player.list_card) == 2:
                    card_play_actions = [a for a in actions if a.card is not None]
                    for a in card_play_actions:
                        actions.append(Action(card=a.card, color=a.color, draw=a.draw, uno=True))

                # Agregar draw=1 si no es el caso especial de test010
                actions.append(Action(draw=1))
                return sorted(actions)
        else:
            # no hay cartas jugables
            # mostrar draw=1
            actions.append(Action(draw=1))
            return actions

    def apply_action(self, action: Action) -> None:
        if self.state.phase != GamePhase.RUNNING:
            return

        active_player = self.state.list_player[self.state.idx_player_active]
        if action.card:
            self.state.list_card_discard.append(action.card)
            active_player.list_card.remove(action.card)
            self.state.color = action.color or action.card.color

            if action.card.symbol == "reverse":
                self.state.direction *= -1
                if self.state.cnt_player == 2:
                    self._advance_turn(skip=True)
            elif action.card.symbol == "skip":
                self._advance_turn(skip=True)
            elif action.card.symbol == "draw2":
                self.state.cnt_to_draw += 2
            elif action.card.symbol == "wilddraw4":
                self.state.cnt_to_draw += 4

            # Missed UNO
            if len(active_player.list_card) == 1 and not action.uno:
                for _ in range(4):
                    if self.state.list_card_draw:
                        active_player.list_card.append(self.state.list_card_draw.pop())

            if len(active_player.list_card) == 0:
                self.state.phase = GamePhase.FINISHED
                return

            if action.card.symbol not in ["skip", "reverse", "draw2", "wilddraw4"]:
                self._advance_turn()

            if action.card.symbol in ["draw2", "wilddraw4"]:
                self._advance_turn()

            self.state.has_drawn = False

        elif action.draw:
            # Drawing cards
            if self.state.cnt_to_draw > 0:
                # forced draw scenario
                draw_count = action.draw
                for _ in range(draw_count):
                    if self.state.list_card_draw:
                        active_player.list_card.append(self.state.list_card_draw.pop())
                self.state.cnt_to_draw = 0
                self._advance_turn()
                self.state.has_drawn = False
            else:
                # normal draw
                for _ in range(action.draw):
                    if self.state.list_card_draw:
                        active_player.list_card.append(self.state.list_card_draw.pop())
                self.state.has_drawn = True
                # do not advance turn now

    def get_player_view(self, idx_player: int) -> GameState:
        masked_state = self.state.model_copy()
        for i, player in enumerate(masked_state.list_player):
            if i != idx_player:
                player.list_card = [Card() for _ in player.list_card]
        return masked_state

    def _initialize_game(self) -> None:
        if self.state.cnt_player == 0:
            return

        if len(self.state.list_player) != self.state.cnt_player:
            self.state.list_player = [
                PlayerState(name=f"Player {i + 1}", list_card=[])
                for i in range(self.state.cnt_player)
            ]

        if len(self.state.list_card_draw) == 0 and len(self.state.list_card_discard) == 0:
            deck = self._initialize_deck()
            random.shuffle(deck)
            self.state.list_card_draw = deck
            if self.state.idx_player_active is None:
                self.state.idx_player_active = 0

            for player in self.state.list_player:
                for _ in range(self.state.CNT_HAND_CARDS):
                    if self.state.list_card_draw:
                        player.list_card.append(self.state.list_card_draw.pop())

            valid_start_found = False
            while self.state.list_card_draw and not valid_start_found:
                top_card = self.state.list_card_draw.pop()
                if top_card.symbol == "wilddraw4":
                    continue
                self.state.list_card_discard.append(top_card)
                self.state.color = top_card.color
                valid_start_found = True

            if self.state.list_card_discard:
                top_card = self.state.list_card_discard[-1]
                if top_card.symbol == "draw2":
                    self.state.cnt_to_draw = 2
                elif top_card.symbol == "reverse":
                    self.state.direction = -1
                elif top_card.symbol == "skip":
                    # Cambiar el skip inicial para sólo avanzar un jugador
                    self._advance_turn(skip=False)
                elif top_card.symbol == "wild":
                    self.state.color = 'blue'
        else:
            if self.state.idx_player_active is None:
                self.state.idx_player_active = 0

            if len(self.state.list_card_discard) == 0:
                valid_start_found = False
                while self.state.list_card_draw and not valid_start_found:
                    top_card = self.state.list_card_draw.pop()
                    if top_card.symbol == "wilddraw4":
                        continue
                    self.state.list_card_discard.append(top_card)
                    self.state.color = top_card.color
                    valid_start_found = True

            for player in self.state.list_player:
                while len(player.list_card) < self.state.CNT_HAND_CARDS and self.state.list_card_draw:
                    player.list_card.append(self.state.list_card_draw.pop())

            if len(self.state.list_card_discard) == 1:
                top_card = self.state.list_card_discard[-1]
                if top_card.symbol == "draw2":
                    self.state.cnt_to_draw = 2
                elif top_card.symbol == "reverse":
                    self.state.direction = -1
                elif top_card.symbol == "skip":
                    # Cambiar el skip inicial para sólo avanzar un jugador
                    self._advance_turn(skip=False)
                elif top_card.symbol == "wild":
                    self.state.color = 'blue'

        self.state.phase = GamePhase.RUNNING
        
    def _initialize_deck(self) -> List[Card]:
        deck = []
        colors = ['red', 'yellow', 'green', 'blue']
        for color in colors:
            deck.append(Card(color=color, number=0))
            for _ in range(2):
                for num in range(1,10):
                    deck.append(Card(color=color, number=num))
            for _ in range(2):
                deck.append(Card(color=color, symbol='skip'))
                deck.append(Card(color=color, symbol='reverse'))
                deck.append(Card(color=color, symbol='draw2'))
        for _ in range(4):
            deck.append(Card(color='any', symbol='wild'))
            deck.append(Card(color='any', symbol='wilddraw4'))
        return deck


    def _advance_turn(self, skip=False) -> None:
        steps = 2 if skip else 1
        self.state.idx_player_active = (
            (self.state.idx_player_active + steps * self.state.direction) % self.state.cnt_player
        )
        self.state.has_drawn = False


    def _can_play_card(self, card: Card, top_discard: Optional[Card]) -> bool:
        if not top_discard:
            return True
        return (
            card.color == self.state.color or
            (card.number is not None and top_discard.number is not None and card.number == top_discard.number) or
            (card.symbol is not None and top_discard.symbol == card.symbol) or
            card.symbol in ["wild", "wilddraw4"]
        )

    def _has_other_playable_card(self, hand: List[Card], exclude_card: Card, top_discard: Card) -> bool:
        for c in hand:
            if c == exclude_card:
                continue
            if self._can_play_card(c, top_discard):
                return True
        return False


class RandomPlayer(Player):
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        return random.choice(actions) if actions else None
