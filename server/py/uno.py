# -runcmd: cd ../.. & venv\Scripts\python server/py/uno.py
# runcmd: cd ../.. & venv\Scripts\python benchmark/benchmark_uno.py python uno.Uno

from server.py.game import Game, Player
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
import random


class Card(BaseModel):
    color: Optional[str] = None  # color of the card (see LIST_COLOR)
    number: Optional[int] = None  # number of the card (if not a symbol card)
    symbol: Optional[str] = None  # special cards (see LIST_SYMBOL)


class Action(BaseModel):
    card: Optional[Card] = None  # the card to play
    color: Optional[str] = None  # the chosen color to play (for wild cards)
    draw: Optional[int] = None  # the number of cards to draw for the next player
    uno: bool = False  # true to announce "UNO" with the second last card

    def __lt__(self, other):
        """Define less than for sorting Actions."""
        if not isinstance(other, Action):
            return NotImplemented
        return (
            (self.card.color if self.card else '', self.card.number if self.card else -1,
             self.card.symbol if self.card else '', self.color, self.draw, self.uno)
            < 
            (other.card.color if other.card else '', other.card.number if other.card else -1,
             other.card.symbol if other.card else '', other.color, other.draw, other.uno)
        )


class PlayerState(BaseModel):
    name: Optional[str] = None  # name of player
    list_card: List[Card] = []  # list of cards


class GamePhase(str, Enum):
    SETUP = 'setup'  # before the game has started
    RUNNING = 'running'  # while the game is running
    FINISHED = 'finished'  # when the game is finished


class GameState(BaseModel):
    # Static constants
    CNT_HAND_CARDS: int = 7
    LIST_COLOR: List[str] = ['red', 'green', 'yellow', 'blue', 'any']
    LIST_SYMBOL: List[str] = ['skip', 'reverse', 'draw2', 'wild', 'wilddraw4']

    # Dynamic state
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
        """Initialize the game."""
        self.state = GameState(
            list_card_draw=[],  # Empty draw pile
            list_card_discard=[],  # Empty discard pile
            list_player=[],  # No players yet
            phase=GamePhase.SETUP,  # Initial phase is setup
            cnt_player=0,  # No players initially
            idx_player_active=None,  # No active player
            direction=1,  # Default direction
            color='any',  # No color yet
            cnt_to_draw=0,  # No cards to draw yet
            has_drawn=False  # No drawing action performed
        )

    def set_state(self, state: GameState) -> None:
        """Set the game to a given state."""
        self.state = state
        if self.state.phase == GamePhase.SETUP:
            self._initialize_game()

    def get_state(self) -> GameState:
        """Get the complete, unmasked game state."""
        return self.state

    def print_state(self) -> None:
        """Print the current game state."""
        print(self.state.json(indent=2))

    def get_list_action(self) -> List[Action]:
        """Get a list of possible actions for the active player."""
        actions = []
        active_player = self.state.list_player[self.state.idx_player_active]
        top_discard = self.state.list_card_discard[-1] if self.state.list_card_discard else None

        # Check valid playable cards
        for card in active_player.list_card:
            if (
                top_discard and
                (card.color == self.state.color or
                (card.number is not None and card.number == top_discard.number) or
                card.symbol == top_discard.symbol or
                card.symbol in ["wild", "wilddraw4"])
            ):
                if card.symbol == "wilddraw4" and any(
                    c.color == self.state.color or
                    (c.number == top_discard.number if top_discard else False)
                    for c in active_player.list_card if c != card
                ):
                    continue  # Skip if other playable cards exist
                actions.append(Action(card=card, color=card.color or "any"))

        # Draw action
        draw_count = self.state.cnt_to_draw or 1
        actions.append(Action(draw=draw_count))

        # UNO announcement for second last card
        if len(active_player.list_card) == 2:
            actions.extend(
                [Action(card=action.card, color=action.color, uno=True)
                for action in actions if action.card]
            )

        return actions


    def apply_action(self, action: Action) -> None:
        """Apply the given action to the game."""
        if action.card:
            self.state.list_card_discard.append(action.card)
            self.state.list_player[self.state.idx_player_active].list_card.remove(action.card)
            self.state.color = action.color or action.card.color

            if action.card.symbol == "reverse":
                self.state.direction *= -1
                if self.state.cnt_player == 2:  # Reverse acts as skip for 2 players
                    self._advance_turn(skip=True)
            elif action.card.symbol == "skip":
                self._advance_turn(skip=True)
            elif action.card.symbol == "draw2":
                self.state.cnt_to_draw += 2
            elif action.card.symbol == "wilddraw4":
                self.state.cnt_to_draw += 4

        elif action.draw:
            for _ in range(action.draw):
                if self.state.list_card_draw:
                    self.state.list_player[self.state.idx_player_active].list_card.append(self.state.list_card_draw.pop())

        # Check for UNO violation
        if len(self.state.list_player[self.state.idx_player_active].list_card) == 1 and not action.uno:
            for _ in range(4):  # Draw 4 cards penalty
                if self.state.list_card_draw:
                    self.state.list_player[self.state.idx_player_active].list_card.append(self.state.list_card_draw.pop())

        if len(self.state.list_player[self.state.idx_player_active].list_card) == 0:
            self.state.phase = GamePhase.FINISHED
        else:
            self._advance_turn()


    def get_player_view(self, idx_player: int) -> GameState:
        """Get the masked state for the active player."""
        masked_state = self.state.copy()
        for i, player in enumerate(masked_state.list_player):
            if i != idx_player:
                player.list_card = [Card() for _ in player.list_card]
        return masked_state

    def _initialize_game(self) -> None:
        """Initialize game state for players and draw cards."""
        self.state.list_player = [
            PlayerState(name=f"Player {i + 1}", list_card=[])
            for i in range(self.state.cnt_player)
        ]

        # Initialize deck
        deck = self._initialize_deck()
        random.shuffle(deck)
        self.state.list_card_draw = deck

        # Distribute cards to players
        for player in self.state.list_player:
            for _ in range(self.state.CNT_HAND_CARDS):
                if self.state.list_card_draw:
                    player.list_card.append(self.state.list_card_draw.pop())

        # Initialize the discard pile with a valid starting card
        while self.state.list_card_draw:
            top_card = self.state.list_card_draw.pop()
            if top_card.symbol not in ["wilddraw4"]:  # Ensure a valid starting card
                self.state.list_card_discard.append(top_card)
                self.state.color = top_card.color
                # Handle special starting cards
                if top_card.symbol == "draw2":
                    self.state.cnt_to_draw = 2
                elif top_card.symbol == "reverse" and self.state.cnt_player == 2:
                    self.state.direction *= -1  # Reverse acts as skip for 2 players
                elif top_card.symbol == "skip":
                    self._advance_turn(skip=True)
                break

        self.state.idx_player_active = 0
        self.state.phase = GamePhase.RUNNING


    def _initialize_deck(self) -> List[Card]:
        """Create a full deck of UNO cards."""
        deck = []
        for color in self.state.LIST_COLOR[:-1]:  # Exclude 'any' for standard cards
            for number in range(10):
                deck.append(Card(color=color, number=number))
            for number in range(1, 10):  # Add second set of numbers
                deck.append(Card(color=color, number=number))
            for symbol in ["skip", "reverse", "draw2"]:
                deck.append(Card(color=color, symbol=symbol))
                deck.append(Card(color=color, symbol=symbol))

        # Add wild and wild draw 4 cards
        for _ in range(4):
            deck.append(Card(color="any", symbol="wild"))
            deck.append(Card(color="any", symbol="wilddraw4"))

        return deck

    def _advance_turn(self, skip=False) -> None:
        """Advance to the next player's turn."""
        steps = 2 if skip else 1
        self.state.idx_player_active = (
            (self.state.idx_player_active + steps * self.state.direction) % self.state.cnt_player
        )



class RandomPlayer(Player):
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """Given masked game state and possible actions, select the next action."""
        return random.choice(actions) if actions else None


if __name__ == "__main__":
    uno = Uno()
    state = GameState(cnt_player=3)
    uno.set_state(state)
