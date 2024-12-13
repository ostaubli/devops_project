from server.py.game import Game, Player
from typing import List, Optional
from enum import Enum
import random
from pydantic import BaseModel

class Card(BaseModel):
    """Represents a UNO card with optional color, number, and/or symbol."""
    color: Optional[str] = None
    number: Optional[int] = None
    symbol: Optional[str] = None


class Action(BaseModel):
    """Represents an action that a player can take in the UNO game."""
    card: Optional[Card] = None
    color: Optional[str] = None
    draw: Optional[int] = None
    uno: bool = False

    def __lt__(self, other: object) -> bool:
        """Compare actions for sorting purposes."""
        if not isinstance(other, Action):
            return NotImplemented
        return (
            (self.card.color if self.card and self.card.color else '',
             self.card.number if self.card and self.card.number is not None else -1,
             self.card.symbol if self.card and self.card.symbol else '',
             self.color if self.color else '',
             self.draw if self.draw else 0,
             self.uno)
            <
            (other.card.color if other.card and other.card.color else '',
             other.card.number if other.card and other.card.number is not None else -1,
             other.card.symbol if other.card and other.card.symbol else '',
             other.color if other.color else '',
             other.draw if other.draw else 0,
             other.uno)
        )


class PlayerState(BaseModel):
    """Represents the state of a single player."""
    name: Optional[str] = None
    list_card: List[Card] = []


class GamePhase(str, Enum):
    """Phases of the UNO game."""
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'


class GameState(BaseModel):
    """Represents the entire state of the UNO game."""
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
    """UNO game implementation."""

    def __init__(self) -> None:
        """Initialize a new UNO game with default state."""
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
        """
        Set the current game state.

        If the phase is SETUP, initialize the game.
        """
        self.state = state
        if self.state.phase == GamePhase.SETUP:
            self._initialize_game()

    def get_state(self) -> GameState:
        """Return the current game state."""
        return self.state

    def print_state(self) -> None:
        # Just call a helper method that returns the desired string
        print_str = self._generate_state_str(list_color=True, list_symbol=True, list_card=True)
        print(print_str)

    def _generate_state_str(self, list_color: bool = True, list_symbol: bool = True,
                            list_card: bool = True) -> str:
        """
        Return a string representation of the current game state.
        """
        print_str = "Game State:"
        fields = self.state.__fields__.keys() if hasattr(self.state, '__fields__') else self.state.__dict__.keys()
        for keys in fields:
            if not list_color and keys == 'LIST_COLOR':
                continue
            if not list_symbol and keys == 'LIST_SYMBOL':
                continue
            if not list_card and keys == 'LIST_CARD':
                continue
            print_str += f'\n{keys} : {getattr(self.state, keys)}'
        return print_str

    def get_list_action(self) -> List[Action]:
        """
        Get the list of possible actions for the current active player.
        """
        if self.state.phase != GamePhase.RUNNING:
            return []

        assert self.state.idx_player_active is not None  # Ensures index is int
        active_player = self.state.list_player[self.state.idx_player_active]
        top_discard = self.state.list_card_discard[-1] if self.state.list_card_discard else None

        playable_cards = [c for c in active_player.list_card if self._can_play_card(c, top_discard)]

        # Special case: first turn with a wild card on the discard pile (test010)
        first_turn_with_wild = (len(self.state.list_card_discard) == 1
                                and top_discard and top_discard.symbol == 'wild')

        actions: List[Action] = []
        if self.state.cnt_to_draw > 0:
            cumulative_scenario = self.state.cnt_to_draw > 2
            normal_playable_exists = any(
                c.symbol not in ('draw2', 'wilddraw4') and self._can_play_card(c, top_discard)
                for c in playable_cards
            )

            stackable: List[Action] = []
            normal_actions: List[Action] = []
            for c in playable_cards:
                if c.symbol == 'draw2':
                    draw_val = 2 if (normal_playable_exists and not cumulative_scenario) \
                        else self.state.cnt_to_draw + 2
                    stackable.append(Action(card=c, color=c.color if c.color else 'any', draw=draw_val))
                elif c.symbol == 'wilddraw4':
                    base_draw = 4
                    draw_val = base_draw if (normal_playable_exists and not cumulative_scenario) \
                        else (self.state.cnt_to_draw + 4)
                    for col in ['red', 'green', 'yellow', 'blue']:
                        stackable.append(Action(card=c, color=col, draw=draw_val))
                else:
                    if not cumulative_scenario:
                        chosen_color = c.color if c.color else 'any'
                        normal_actions.append(Action(card=c, color=chosen_color))

            if cumulative_scenario:
                if stackable:
                    actions.extend(stackable)
                    if len(active_player.list_card) == 2:
                        card_play_actions = [a for a in stackable if a.card is not None]
                        for a in card_play_actions:
                            actions.append(Action(card=a.card, color=a.color, draw=a.draw, uno=True))
                else:
                    actions.append(Action(draw=self.state.cnt_to_draw))
            else:
                actions.extend(normal_actions)
                actions.extend(stackable)
                if actions:
                    if len(active_player.list_card) == 2:
                        card_play_actions = [a for a in actions if a.card is not None]
                        for a in card_play_actions:
                            actions.append(Action(card=a.card, color=a.color, draw=a.draw, uno=True))
                    if normal_playable_exists:
                        actions.append(Action(draw=1))
                else:
                    actions.append(Action(draw=self.state.cnt_to_draw))

            return sorted(actions)

        # If cnt_to_draw=0
        if self.state.has_drawn:
            # has_drawn=True, no pending draws
            if playable_cards:
                for c in playable_cards:
                    if c.symbol == 'wild':
                        for col in ['red', 'green', 'yellow', 'blue']:
                            actions.append(Action(card=c, color=col))
                    elif c.symbol == 'wilddraw4':
                        # Now _has_other_playable_card accepts Optional[Card]
                        if not self._has_other_playable_card(active_player.list_card, c, top_discard):
                            for col in ['red', 'green', 'yellow', 'blue']:
                                actions.append(Action(card=c, color=col, draw=4))
                    elif c.symbol == 'draw2':
                        actions.append(Action(card=c, color=c.color if c.color else 'any', draw=2))
                    else:
                        actions.append(Action(card=c, color=c.color if c.color else 'any'))

                if len(active_player.list_card) == 2:
                    card_play_actions = [a for a in actions if a.card is not None]
                    for a in card_play_actions:
                        actions.append(Action(card=a.card, color=a.color, draw=a.draw, uno=True))
                return sorted(actions)

            actions.append(Action(draw=1))
            return sorted(actions)

        # has_drawn=False, cnt_to_draw=0
        if playable_cards:
            if first_turn_with_wild:
                for c in playable_cards:
                    if c.symbol == 'wild':
                        for col in ['red', 'green', 'yellow', 'blue']:
                            actions.append(Action(card=c, color=col))
                    elif c.symbol == 'wilddraw4':
                        if not self._has_other_playable_card(active_player.list_card, c, top_discard):
                            for col in ['red', 'green', 'yellow', 'blue']:
                                actions.append(Action(card=c, color=col, draw=4))
                    elif c.symbol == 'draw2':
                        actions.append(Action(card=c, color=c.color if c.color else 'any', draw=2))
                    else:
                        actions.append(Action(card=c, color=c.color if c.color else 'any'))

                if len(active_player.list_card) == 2:
                    card_play_actions = [a for a in actions if a.card is not None]
                    for a in card_play_actions:
                        actions.append(Action(card=a.card, color=a.color, draw=a.draw, uno=True))
                return sorted(actions)

            for c in playable_cards:
                if c.symbol == 'wild':
                    for col in ['red', 'green', 'yellow', 'blue']:
                        actions.append(Action(card=c, color=col))
                elif c.symbol == 'wilddraw4':
                    if not self._has_other_playable_card(active_player.list_card, c, top_discard):
                        for col in ['red', 'green', 'yellow', 'blue']:
                            actions.append(Action(card=c, color=col, draw=4))
                elif c.symbol == 'draw2':
                    actions.append(Action(card=c, color=c.color if c.color else 'any', draw=2))
                else:
                    actions.append(Action(card=c, color=c.color if c.color else 'any'))

            if len(active_player.list_card) == 2:
                card_play_actions = [a for a in actions if a.card is not None]
                for a in card_play_actions:
                    actions.append(Action(card=a.card, color=a.color, draw=a.draw, uno=True))

            actions.append(Action(draw=1))
            return sorted(actions)

        actions.append(Action(draw=1))
        return actions

    def apply_action(self, action: Action) -> None:
        if self.state.phase != GamePhase.RUNNING:
            return

        assert self.state.idx_player_active is not None
        active_player = self.state.list_player[self.state.idx_player_active]
        if action.card:
            self.state.list_card_discard.append(action.card)
            active_player.list_card.remove(action.card)
            # Ensure color is always a string
            chosen_color = action.color if action.color is not None else (action.card.color if action.card.color else 'any')
            self.state.color = chosen_color

            if action.card.symbol == "reverse":
                self.state.direction *= -1
            elif action.card.symbol == "skip":
                self._advance_turn(skip=True)
            elif action.card.symbol == "draw2":
                self.state.cnt_to_draw += 2
            elif action.card.symbol == "wilddraw4":
                self.state.cnt_to_draw += 4

            # Missed UNO penalty
            if len(active_player.list_card) == 1 and not action.uno:
                for _ in range(4):
                    if self.state.list_card_draw:
                        active_player.list_card.append(self.state.list_card_draw.pop())

            # If player finished all cards
            if len(active_player.list_card) == 0:
                self.state.phase = GamePhase.FINISHED
                return

            if action.card.symbol not in ["skip", "reverse", "draw2", "wilddraw4"]:
                self._advance_turn()

            if action.card.symbol in ["draw2", "wilddraw4"] and self.state.cnt_player == 2:
                self._advance_turn()

            self.state.has_drawn = False

        elif action.draw:
            # Drawing cards action
            assert self.state.idx_player_active is not None
            if self.state.cnt_to_draw > 0:
                draw_count = action.draw
                if draw_count is None:
                    draw_count = self.state.cnt_to_draw  # fallback if needed
                for _ in range(draw_count):
                    if self.state.list_card_draw:
                        active_player.list_card.append(self.state.list_card_draw.pop())
                self.state.cnt_to_draw = 0
                self._advance_turn(skip=True)
                self.state.has_drawn = False
            else:
                draw_count = action.draw if action.draw is not None else 1
                for _ in range(draw_count):
                    if self.state.list_card_draw:
                        active_player.list_card.append(self.state.list_card_draw.pop())
                self.state.has_drawn = True

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

        # Only initialize deck if both draw and discard are empty
        if not self.state.list_card_draw and not self.state.list_card_discard:
            deck = self._initialize_deck()
            random.shuffle(deck)
            self.state.list_card_draw = deck

        if self.state.idx_player_active is None:
            self.state.idx_player_active = 0

        for player in self.state.list_player:
            while len(player.list_card) < self.state.CNT_HAND_CARDS and self.state.list_card_draw:
                player.list_card.append(self.state.list_card_draw.pop())

        valid_start_found = False
        if not self.state.list_card_discard:
            while self.state.list_card_draw and not valid_start_found:
                top_card = self.state.list_card_draw.pop()
                if top_card.symbol == "wilddraw4":
                    continue
                self.state.list_card_discard.append(top_card)
                self.state.color = top_card.color if top_card.color else 'any'
                valid_start_found = True

        if self.state.list_card_discard:
            top_card = self.state.list_card_discard[-1]
            if top_card.symbol == "draw2":
                self.state.cnt_to_draw = 2
            elif top_card.symbol == "reverse":
                self.state.direction = -1
            elif top_card.symbol == "skip":
                if valid_start_found:
                    self._advance_turn(skip=False)
                else:
                    self._advance_turn(skip=True)
            elif top_card.symbol == "wild":
                self.state.color = 'any'

        self.state.phase = GamePhase.RUNNING

    def _initialize_deck(self) -> List[Card]:
        deck: List[Card] = []
        colors = ['red', 'yellow', 'green', 'blue']
        for color in colors:
            deck.append(Card(color=color, number=0))
            for _ in range(2):
                for num in range(1, 10):
                    deck.append(Card(color=color, number=num))
            for _ in range(2):
                deck.append(Card(color=color, symbol='skip'))
                deck.append(Card(color=color, symbol='reverse'))
                deck.append(Card(color=color, symbol='draw2'))
        for _ in range(4):
            deck.append(Card(color='any', symbol='wild'))
            deck.append(Card(color='any', symbol='wilddraw4'))
        return deck

    def _advance_turn(self, skip: bool = False) -> None:
        assert self.state.idx_player_active is not None
        steps = 2 if skip else 1
        self.state.idx_player_active = (
            (self.state.idx_player_active + steps * self.state.direction) % self.state.cnt_player
        )
        self.state.has_drawn = False

    def _can_play_card(self, card: Card, top_discard: Optional[Card]) -> bool:
        # If there is no card on the discard pile, we can play anything
        if not top_discard:
            return True

        # Check by color first
        if card.color == self.state.color or self.state.color == 'any':
            return True

        # Check by matching number (if both have numbers)
        if card.number is not None and top_discard.number is not None:
            if card.number == top_discard.number:
                return True

        # Check by matching symbol
        if card.symbol is not None and top_discard.symbol == card.symbol:
            return True

        # Check if the card is a wildcard
        if card.symbol in ["wild", "wilddraw4"]:
            return True

        # If none of the conditions are met, the card can’t be played
        return False


    def _has_other_playable_card(self, hand: List[Card], exclude_card: Card,
                                 top_discard: Optional[Card]) -> bool:
        for c in hand:
            if c == exclude_card:
                continue
            if self._can_play_card(c, top_discard):
                return True
        return False


class RandomPlayer(Player):
    """A random player implementation that chooses actions at random."""
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        return random.choice(actions) if actions else None


# Example usage:
if __name__ == "__main__":
    # Initialize a UNO game with 2 players
    game = Uno()
    initial_state = GameState(cnt_player=2)
    game.set_state(initial_state)
    game.print_state()
    # You can now call game.get_list_action(), game.apply_action(), etc.
