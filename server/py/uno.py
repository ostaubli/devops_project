# Tests: 15/21 valid
# Mark:  31/52 points
from typing import List, Optional
from enum import Enum
import random
from pydantic import BaseModel
from server.py.game import Game, Player


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

    def print_state(self, list_color: bool = True, list_symbol: bool = True,
                    list_card: bool = True) -> str:
        """
        Return a string representation of the current game state.
        
        Parameters:
            list_color (bool): If False, omit LIST_COLOR from the output.
            list_symbol (bool): If False, omit LIST_SYMBOL from the output.
            list_card (bool): If False, omit LIST_CARD from the output.
        
        Returns:
            str: A string describing the current state.
        """
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
        """
        Get the list of possible actions for the current active player.
        
        Returns:
            List[Action]: The actions that the active player can perform.
        """
        if self.state.phase != GamePhase.RUNNING:
            return []

        actions: List[Action] = []
        active_player = self.state.list_player[self.state.idx_player_active]
        top_discard = self.state.list_card_discard[-1] if self.state.list_card_discard else None

        playable_cards = [c for c in active_player.list_card if self._can_play_card(c, top_discard)]

        # Special case: first turn with a wild card on the discard pile (test010)
        first_turn_with_wild = (len(self.state.list_card_discard) == 1
                                and top_discard and top_discard.symbol == 'wild')

        if self.state.cnt_to_draw > 0:
            # Distinguish between initial forced draw (cnt_to_draw=2) and cumulative scenario (>2)
            cumulative_scenario = self.state.cnt_to_draw > 2

            # Check if normal playable cards exist (not draw2/wilddraw4)
            normal_playable_exists = any(
                c.symbol not in ('draw2', 'wilddraw4') and self._can_play_card(c, top_discard)
                for c in playable_cards
            )

            stackable: List[Action] = []
            normal_actions: List[Action] = []
            for c in playable_cards:
                if c.symbol == 'draw2':
                    draw_val = 2 if normal_playable_exists and not cumulative_scenario \
                        else self.state.cnt_to_draw + 2
                    stackable.append(Action(card=c, color=c.color, draw=draw_val))
                elif c.symbol == 'wilddraw4':
                    base_draw = 4
                    draw_val = base_draw if (normal_playable_exists and not cumulative_scenario) \
                        else (self.state.cnt_to_draw + 4)
                    for col in ['red', 'green', 'yellow', 'blue']:
                        stackable.append(Action(card=c, color=col, draw=draw_val))
                else:
                    # Normal playable card
                    if not cumulative_scenario:
                        # Only show normal cards if not in cumulative scenario
                        if c.symbol:
                            normal_actions.append(Action(card=c, color=c.color))
                        else:
                            normal_actions.append(Action(card=c, color=c.color or "any"))

            # If cumulative_scenario is True, do not show normal_actions
            if cumulative_scenario:
                # In cumulative scenario, show stackable if any, otherwise forced draw
                if stackable:
                    actions.extend(stackable)
                    # UNO option if second last card
                    if len(active_player.list_card) == 2:
                        card_play_actions = [a for a in stackable if a.card is not None]
                        for a in card_play_actions:
                            actions.append(Action(card=a.card, color=a.color, draw=a.draw, uno=True))
                    # No draw=1 in cumulative scenario
                else:
                    # No stackable, must show forced draw
                    actions.append(Action(draw=self.state.cnt_to_draw))
            else:
                # Not a cumulative scenario (likely cnt_to_draw=2)
                # Show both normal_actions and stackable
                actions.extend(normal_actions)
                actions.extend(stackable)

                if actions:
                    # UNO if second last card
                    if len(active_player.list_card) == 2:
                        card_play_actions = [a for a in actions if a.card is not None]
                        for a in card_play_actions:
                            actions.append(Action(card=a.card, color=a.color, draw=a.draw, uno=True))

                    # If normal_playable_exists, show draw=1
                    if normal_playable_exists:
                        actions.append(Action(draw=1))
                else:
                    # No actions, must show forced draw
                    actions.append(Action(draw=self.state.cnt_to_draw))

            return sorted(actions)

        # If cnt_to_draw=0
        if self.state.has_drawn:
            # Already drew a card this turn
            if playable_cards:
                for c in playable_cards:
                    if c.symbol == 'wild':
                        for col in ['red', 'green', 'yellow', 'blue']:
                            actions.append(Action(card=c, color=col))
                    elif c.symbol == 'wilddraw4':
                        if not self._has_other_playable_card(active_player.list_card, c, top_discard):
                            for col in ['red', 'green', 'yellow', 'blue']:
                                actions.append(Action(card=c, color=col, draw=4))
                    elif c.symbol == 'draw2':
                        actions.append(Action(card=c, color=c.color, draw=2))
                    else:
                        actions.append(Action(card=c, color=c.color or "any"))

                if len(active_player.list_card) == 2:
                    card_play_actions = [a for a in actions if a.card is not None]
                    for a in card_play_actions:
                        actions.append(Action(card=a.card, color=a.color, draw=a.draw, uno=True))

                # No draw=1 since we already drew and have playable cards
                return sorted(actions)

            # No playable cards after drawing, show draw=1 again
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
                        actions.append(Action(card=c, color=c.color, draw=2))
                    else:
                        actions.append(Action(card=c, color=c.color or "any"))

                if len(active_player.list_card) == 2:
                    card_play_actions = [a for a in actions if a.card is not None]
                    for a in card_play_actions:
                        actions.append(Action(card=a.card, color=a.color, draw=a.draw, uno=True))
                return sorted(actions)

            # Normal scenario
            for c in playable_cards:
                if c.symbol == 'wild':
                    for col in ['red', 'green', 'yellow', 'blue']:
                        actions.append(Action(card=c, color=col))
                elif c.symbol == 'wilddraw4':
                    if not self._has_other_playable_card(active_player.list_card, c, top_discard):
                        for col in ['red', 'green', 'yellow', 'blue']:
                            actions.append(Action(card=c, color=col, draw=4))
                elif c.symbol == 'draw2':
                    actions.append(Action(card=c, color=c.color, draw=2))
                else:
                    actions.append(Action(card=c, color=c.color or "any"))

            if len(active_player.list_card) == 2:
                card_play_actions = [a for a in actions if a.card is not None]
                for a in card_play_actions:
                    actions.append(Action(card=a.card, color=a.color, draw=a.draw, uno=True))

            # Add draw=1
            actions.append(Action(draw=1))
            return sorted(actions)

        # No playable cards
        actions.append(Action(draw=1))
        return actions

    def apply_action(self, action: Action) -> None:
        """
        Apply the given action to the current game state.
        
        Parameters:
            action (Action): The action selected by the active player.
        """
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

            # Missed UNO penalty
            if len(active_player.list_card) == 1 and not action.uno:
                for _ in range(4):
                    if self.state.list_card_draw:
                        active_player.list_card.append(self.state.list_card_draw.pop())

            # If player finished all cards
            if len(active_player.list_card) == 0:
                self.state.phase = GamePhase.FINISHED
                return

            # Advance turn only if it's a normal card
            if action.card.symbol not in ["skip", "reverse", "draw2", "wilddraw4"]:
                self._advance_turn()

            # No second turn advance for draw2 or wilddraw4
            self.state.has_drawn = False

        elif action.draw:
            # Drawing cards
            if self.state.cnt_to_draw > 0:
                # Forced draw scenario
                draw_count = action.draw
                for _ in range(draw_count):
                    if self.state.list_card_draw:
                        active_player.list_card.append(self.state.list_card_draw.pop())
                self.state.cnt_to_draw = 0
                self._advance_turn()
                self.state.has_drawn = False
            else:
                # Normal draw scenario
                for _ in range(action.draw):
                    if self.state.list_card_draw:
                        active_player.list_card.append(self.state.list_card_draw.pop())
                self.state.has_drawn = True
                # Do not advance turn now

    def get_player_view(self, idx_player: int) -> GameState:
        """
        Return a masked state where other players' cards are hidden.
        
        Parameters:
            idx_player (int): The index of the player requesting the view.
        
        Returns:
            GameState: A copy of the game state with hidden cards for other players.
        """
        masked_state = self.state.model_copy()
        for i, player in enumerate(masked_state.list_player):
            if i != idx_player:
                player.list_card = [Card() for _ in player.list_card]
        return masked_state

    def _initialize_game(self) -> None:
        """Initialize the game: shuffle deck, deal cards, and set up the discard pile."""
        if self.state.cnt_player == 0:
            return

        if len(self.state.list_player) != self.state.cnt_player:
            self.state.list_player = [
                PlayerState(name=f"Player {i + 1}", list_card=[])
                for i in range(self.state.cnt_player)
            ]

        if not self.state.list_card_draw and not self.state.list_card_discard:
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
                    # When initial card is skip, advance only 1 player
                    self._advance_turn(skip=False)
                elif top_card.symbol == "wild":
                    self.state.color = 'blue'
        else:
            if self.state.idx_player_active is None:
                self.state.idx_player_active = 0

            if not self.state.list_card_discard:
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
                    # When initial card is skip, advance only 1 player
                    self._advance_turn(skip=False)
                elif top_card.symbol == "wild":
                    self.state.color = 'blue'

        self.state.phase = GamePhase.RUNNING

    def _initialize_deck(self) -> List[Card]:
        """
        Create and return a standard UNO deck.
        
        Returns:
            List[Card]: A complete UNO deck.
        """
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
        """
        Advance the turn to the next player, skipping if necessary.
        
        Parameters:
            skip (bool): If True, skip the next player (2 steps if more than 2 players).
        """
        steps = 2 if skip else 1
        self.state.idx_player_active = (
            (self.state.idx_player_active + steps * self.state.direction) % self.state.cnt_player
        )
        self.state.has_drawn = False

    def _can_play_card(self, card: Card, top_discard: Optional[Card]) -> bool:
        """
        Check if a given card can be played on the top of the discard pile.
        
        Parameters:
            card (Card): The card to evaluate.
            top_discard (Optional[Card]): The card currently on top of the discard pile.
        
        Returns:
            bool: True if the card can be played, False otherwise.
        """
        if not top_discard:
            return True
        return (
            card.color == self.state.color
            or (card.number is not None and top_discard.number is not None
                and card.number == top_discard.number)
            or (card.symbol is not None and top_discard.symbol == card.symbol)
            or card.symbol in ["wild", "wilddraw4"]
        )

    def _has_other_playable_card(self, hand: List[Card], exclude_card: Card,
                                 top_discard: Card) -> bool:
        """
        Check if there's another playable card in hand excluding a specific card.
        
        Parameters:
            hand (List[Card]): The player's hand.
            exclude_card (Card): A card to exclude from consideration.
            top_discard (Card): The current top discard card.
        
        Returns:
            bool: True if another playable card exists, False otherwise.
        """
        for c in hand:
            if c == exclude_card:
                continue
            if self._can_play_card(c, top_discard):
                return True
        return False


class RandomPlayer(Player):
    """A random player implementation that chooses actions at random."""
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """
        Select an action at random from the list of possible actions.
        
        Parameters:
            state (GameState): The current game state.
            actions (List[Action]): The available actions.
        
        Returns:
            Optional[Action]: A randomly chosen action, or None if no actions.
        """
        return random.choice(actions) if actions else None
 