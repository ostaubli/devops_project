from game import Game, Player
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
    LIST_CARD: List[Card] = [
        Card(color='red', number=0), Card(color='green', number=0), Card(color='yellow', number=0), Card(color='blue', number=0),
        Card(color='red', number=1), Card(color='green', number=1), Card(color='yellow', number=1), Card(color='blue', number=1),
        Card(color='red', number=2), Card(color='green', number=2), Card(color='yellow', number=2), Card(color='blue', number=2),
        Card(color='red', number=3), Card(color='green', number=3), Card(color='yellow', number=3), Card(color='blue', number=3),
        Card(color='red', number=4), Card(color='green', number=4), Card(color='yellow', number=4), Card(color='blue', number=4),
        Card(color='red', number=5), Card(color='green', number=5), Card(color='yellow', number=5), Card(color='blue', number=5),
        Card(color='red', number=6), Card(color='green', number=6), Card(color='yellow', number=6), Card(color='blue', number=6),
        Card(color='red', number=7), Card(color='green', number=7), Card(color='yellow', number=7), Card(color='blue', number=7),
        Card(color='red', number=8), Card(color='green', number=8), Card(color='yellow', number=8), Card(color='blue', number=8),
        Card(color='red', number=9), Card(color='green', number=9), Card(color='yellow', number=9), Card(color='blue', number=9),
        Card(color='red', number=1), Card(color='green', number=1), Card(color='yellow', number=1), Card(color='blue', number=1),
        Card(color='red', number=2), Card(color='green', number=2), Card(color='yellow', number=2), Card(color='blue', number=2),
        Card(color='red', number=3), Card(color='green', number=3), Card(color='yellow', number=3), Card(color='blue', number=3),
        Card(color='red', number=4), Card(color='green', number=4), Card(color='yellow', number=4), Card(color='blue', number=4),
        Card(color='red', number=5), Card(color='green', number=5), Card(color='yellow', number=5), Card(color='blue', number=5),
        Card(color='red', number=6), Card(color='green', number=6), Card(color='yellow', number=6), Card(color='blue', number=6),
        Card(color='red', number=7), Card(color='green', number=7), Card(color='yellow', number=7), Card(color='blue', number=7),
        Card(color='red', number=8), Card(color='green', number=8), Card(color='yellow', number=8), Card(color='blue', number=8),
        Card(color='red', number=9), Card(color='green', number=9), Card(color='yellow', number=9), Card(color='blue', number=9),
        # skip next player
        Card(color='red', symbol='skip'), Card(color='green', symbol='skip'), Card(color='yellow', symbol='skip'), Card(color='blue', symbol='skip'),
        Card(color='red', symbol='skip'), Card(color='green', symbol='skip'), Card(color='yellow', symbol='skip'), Card(color='blue', symbol='skip'),
        # revers playing direction
        Card(color='red', symbol='reverse'), Card(color='green', symbol='reverse'), Card(color='yellow', symbol='reverse'), Card(color='blue', symbol='reverse'),
        Card(color='red', symbol='reverse'), Card(color='green', symbol='reverse'), Card(color='yellow', symbol='reverse'), Card(color='blue', symbol='reverse'),
        # next player must draw 2 cards
        Card(color='red', symbol='draw2'), Card(color='green', symbol='draw2'), Card(color='yellow', symbol='draw2'), Card(color='blue', symbol='draw2'),
        Card(color='red', symbol='draw2'), Card(color='green', symbol='draw2'), Card(color='yellow', symbol='draw2'), Card(color='blue', symbol='draw2'),
        # current player choses color for next player to play
        Card(color='any', symbol='wild'), Card(color='any', symbol='wild'),
        Card(color='any', symbol='wild'), Card(color='any', symbol='wild'),
        # current player choses color for next player to play and next player must draw 4 cards
        Card(color='any', symbol='wilddraw4'), Card(color='any', symbol='wilddraw4'),
        Card(color='any', symbol='wilddraw4'), Card(color='any', symbol='wilddraw4'),
    ]

    # list_card_draw: Optional[List[Card]]     # list of cards to draw
    # list_card_discard: Optional[List[Card]]  # list of cards discarded
    # list_player: List[PlayerState]           # list of player-states
    # phase: GamePhase                         # the current game-phase ("setup"|"running"|"finished")
    # cnt_player: int                          # number of players N (to be set in the phase "setup")
    # idx_player_active: Optional[int]         # the index (0 to N-1) of active player
    # direction: int                           # direction of the game, +1 to the left, -1 to right
    # color: str                               # active color (last card played or the chosen color after a wild cards)
    # cnt_to_draw: int                         # accumulated number of cards to draw for the next player
    # has_drawn: bool                          # flag to indicate if the last player has alreay drawn cards or not

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

    LIST_COLOR = ['red', 'blue', 'yellow', 'green']

    def is_card_valid(card: Card):
        okay = True
        okay = okay and card.number in [None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        okay = okay and card.symbol in [None, 'skip', 'reverse', 'draw2', 'wild', 'wilddraw4']
        okay = okay and card.color in LIST_COLOR + ['any']
        if card.color == 'any':
            okay = okay and card.symbol in ['wild', 'wilddraw4']
        if card.symbol in ['skip', 'reverse', 'draw2']:
            okay = okay and card.color != 'any'
        return okay
# def test_card_values(self):
        """Test 002: Validate card values [1 points]"""
    game_server = Uno()
    
    state = GameState(cnt_player=2)
    game_server.set_state(state)
    game_server.get_state()
    str_state = f'GameState:\n{state}\n'
#######################################################

    for card in state.list_card_draw + state.list_card_discard:
        hint = str_state
        hint += f'Error: Card values not valid {card}.'
        assert is_card_valid(card), hint  #adjust to print if you want

    for player in state.list_player:
        for card in player.list_card:
            hint = str_state
            hint += f'Error: Card values not valid {card}.'
            assert is_card_valid(card), hint #adjust