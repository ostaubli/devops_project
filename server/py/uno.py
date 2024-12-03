# -runcmd: cd ../.. & venv\Scripts\python server/py/uno.py
# runcmd: cd ../.. & venv\Scripts\python benchmark/benchmark_uno.py python uno.Uno

from server.py.game import Game, Player
from typing import List, Optional
from typing import ClassVar
from pydantic import BaseModel
from enum import Enum
import random


class Card(BaseModel):
    color: Optional[str] = None   # color of the card (see LIST_COLOR)
    number: Optional[int] = None  # number of the card (if not a symbol card)
    symbol: Optional[str] = None  # special cards (see LIST_SYMBOL)


class Action(BaseModel):
    card: Optional[Card] = None  # the card to play
    color: Optional[str] = None  # the chosen color to play (for wild cards)
    draw: Optional[int] = None   # the number of cards to draw for the next player
    uno: bool = False            # true to announce "UNO" with the second last card


class PlayerState(BaseModel):
    name: Optional[str] = None  # name of player
    list_card: List[Card] = []  # list of cards


class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


from typing import ClassVar

class GameState(BaseModel):
    # Define class-level constants with ClassVar
    CNT_HAND_CARDS: ClassVar[int] = 7
    LIST_CARD: ClassVar[List[Card]] = [
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
        Card(color='red', symbol='skip'), Card(color='green', symbol='skip'), Card(color='yellow', symbol='skip'), Card(color='blue', symbol='skip'),
        Card(color='red', symbol='reverse'), Card(color='green', symbol='reverse'), Card(color='yellow', symbol='reverse'), Card(color='blue', symbol='reverse'),
        Card(color='red', symbol='draw2'), Card(color='green', symbol='draw2'), Card(color='yellow', symbol='draw2'), Card(color='blue', symbol='draw2'),
        Card(color='any', symbol='wild'), Card(color='any', symbol='wild'),
        Card(color='any', symbol='wilddraw4'), Card(color='any', symbol='wilddraw4'),
    ]

    # Instance attributes
    list_card_draw: Optional[List[Card]]     # list of cards to draw
    list_card_discard: Optional[List[Card]]  # list of cards discarded
    list_player: List[PlayerState]           # list of player-states
    phase: GamePhase                         # the current game-phase ("setup"|"running"|"finished")
    cnt_player: int                          # number of players N (to be set in the phase "setup")
    idx_player_active: Optional[int]         # the index (0 to N-1) of active player
    direction: int                           # direction of the game, +1 to the left, -1 to right
    color: str                               # active color (last card played or the chosen color after a wild cards)
    cnt_to_draw: int                         # accumulated number of cards to draw for the next player
    has_drawn: bool                          # flag to indicate if the last player has already drawn cards or not

    @classmethod
    def get_hand_card_count(cls) -> int:
        """Return the number of cards each player should start with."""
        return cls.CNT_HAND_CARDS

    @classmethod
    def get_card_list(cls) -> List[Card]:
        """Return the complete list of cards."""
        return cls.LIST_CARD[:]


class Uno(Game):
    def __init__(self) -> None:
        """ Initialize the game and set default state """
        self.state = GameState(
            phase=GamePhase.SETUP,
            list_card_draw=[],
            list_card_discard=[],
            list_player=[],
            cnt_player=0,
            idx_player_active=0,
            direction=1,
            color="",
            cnt_to_draw=0,
            has_drawn=False,
        )

    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        self.state = state

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        return self.state

    def print_state(self) -> None:
        """ Print the current game state """
        print(self.state.model_dump_json(indent=4))

    def get_list_action(self) -> List[Action]:
        """ Get a list of possible actions for the active player """
        actions = []
        player = self.state.list_player[self.state.idx_player_active]
        top_card = self.state.list_card_discard[-1] if self.state.list_card_discard else None

        # Check for playable cards
        for card in player.list_card:
            if (
                card.color == self.state.color or
                card.number == (top_card.number if top_card else None) or
                card.symbol == (top_card.symbol if top_card else None) or
                card.color == "any"
            ):
                actions.append(Action(card=card, color=card.color if card.color != "any" else None))

        # Add the option to draw a card
        actions.append(Action(draw=1))

        return actions

    def apply_action(self, action: Action) -> None:
        """ Apply the given action to the game """
        if action.draw:
            # Draw cards
            for _ in range(action.draw):
                if self.state.list_card_draw:
                    drawn_card = self.state.list_card_draw.pop()
                    self.state.list_player[self.state.idx_player_active].list_card.append(drawn_card)
            self.state.has_drawn = True
        elif action.card:
            # Play a card
            player = self.state.list_player[self.state.idx_player_active]
            player.list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)
            self.state.color = action.color or self.state.color

            # Handle special card effects
            if action.card.symbol == "reverse":
                self.state.direction *= -1
            elif action.card.symbol == "skip":
                self.state.idx_player_active = (self.state.idx_player_active + self.state.direction) % self.state.cnt_player
            elif action.card.symbol == "draw2":
                self.state.cnt_to_draw += 2
            elif action.card.symbol == "wilddraw4":
                self.state.cnt_to_draw += 4

            # Check for "UNO"
            if action.uno and len(player.list_card) == 1:
                print(f"{player.name} called UNO!")

        # Move to the next player
        self.state.idx_player_active = (self.state.idx_player_active + self.state.direction) % self.state.cnt_player

        # Check for game end
        if len(self.state.list_player[self.state.idx_player_active].list_card) == 0:
            self.state.phase = GamePhase.FINISHED

    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player """
        state_copy = self.state.copy()
        for i, player in enumerate(state_copy.list_player):
            if i != idx_player:
                player.list_card = [Card()] * len(player.list_card)
        return state_copy


class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


# # Global constants for game configuration
# CNT_HAND_CARDS = 7

# # Global card list outside of GameState
# LIST_CARD = [
#     Card(color='red', number=0), Card(color='green', number=0), Card(color='yellow', number=0), Card(color='blue', number=0),
#     Card(color='red', number=1), Card(color='green', number=1), Card(color='yellow', number=1), Card(color='blue', number=1),
#     Card(color='red', number=2), Card(color='green', number=2), Card(color='yellow', number=2), Card(color='blue', number=2),
#     Card(color='red', number=3), Card(color='green', number=3), Card(color='yellow', number=3), Card(color='blue', number=3),
#     Card(color='red', number=4), Card(color='green', number=4), Card(color='yellow', number=4), Card(color='blue', number=4),
#     Card(color='red', number=5), Card(color='green', number=5), Card(color='yellow', number=5), Card(color='blue', number=5),
#     Card(color='red', number=6), Card(color='green', number=6), Card(color='yellow', number=6), Card(color='blue', number=6),
#     Card(color='red', number=7), Card(color='green', number=7), Card(color='yellow', number=7), Card(color='blue', number=7),
#     Card(color='red', number=8), Card(color='green', number=8), Card(color='yellow', number=8), Card(color='blue', number=8),
#     Card(color='red', number=9), Card(color='green', number=9), Card(color='yellow', number=9), Card(color='blue', number=9),
#     Card(color='red', symbol='skip'), Card(color='green', symbol='skip'), Card(color='yellow', symbol='skip'), Card(color='blue', symbol='skip'),
#     Card(color='red', symbol='reverse'), Card(color='green', symbol='reverse'), Card(color='yellow', symbol='reverse'), Card(color='blue', symbol='reverse'),
#     Card(color='red', symbol='draw2'), Card(color='green', symbol='draw2'), Card(color='yellow', symbol='draw2'), Card(color='blue', symbol='draw2'),
#     Card(color='any', symbol='wild'), Card(color='any', symbol='wild'),
#     Card(color='any', symbol='wilddraw4'), Card(color='any', symbol='wilddraw4'),
# ]

if __name__ == '__main__':
    uno = Uno()

    # Access LIST_CARD and CNT_HAND_CARDS using class methods
    shuffled_cards = GameState.get_card_list()  # Copy the card list
    random.shuffle(shuffled_cards)  # Shuffle the cards

    # Distribute cards to players
    num_players = 3
    players = []
    for i in range(num_players):
        hand_cards = [shuffled_cards.pop() for _ in range(GameState.get_hand_card_count())]
        players.append(PlayerState(name=f"Player {i + 1}", list_card=hand_cards))

    # Set the initial discard pile with one card
    discard_pile = [shuffled_cards.pop()]

    # Initialize the game state
    state = GameState(
        cnt_player=num_players,
        list_card_draw=shuffled_cards,  # Remaining cards as the draw pile
        list_card_discard=discard_pile,  # First discard card
        list_player=players,  # Players with their starting hands
        phase=GamePhase.RUNNING,  # Start the game in the RUNNING phase
        idx_player_active=0,  # Start with the first player
        direction=1,  # Default direction
        color=discard_pile[-1].color,  # Set the initial color based on the first discard card
        cnt_to_draw=0,
        has_drawn=False,
    )

    uno.set_state(state)
    uno.print_state()


