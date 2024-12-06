# -runcmd: cd ../.. & venv\Scripts\python server/py/uno.py
# runcmd: cd ../.. & venv\Scripts\python benchmark/benchmark_uno.py python uno.Uno

from server.py.game import Game, Player #from server.py.game import Game, Player
from typing import List, Optional
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

    @staticmethod
    def _display_deco(function):
        """ Decorator to format the output of the display method, created within this class. """
        def inner(*args, **kwargs):
            print("---- Player State ----")
            result = function(*args, **kwargs)
            print("-----------------------")
            return result
        return inner 

    def add_card(self, card: Card):
        """ Add a card to the player's hand card-stack, when the player pulls a card. """
        self.list_card.append(card)

    def play_card(self, card: Card):
        """ Remove a card from the player's hand stack, when the player plays a card. """
        if card in self.list_card:
            self.list_card.remove(card)

    def check_uno(self) -> bool:
        """ Check whether the player has only one card left to play. """
        uno_card = len(self.list_card) == 1
        return uno_card
    
    def check_no_cards(self) -> bool:
        """ Check whether the player has no cards to play anymore. Then the player won the game. """
        no_card = len(self.list_card) == 0
        return no_card
    
    @_display_deco
    def display_player_state(self):
        """ Display the player's current state and hand card stack. """
        print(f"Player: {self.name}")
        print("Current cards in hand: ", [str(card) for card in self.list_card])
    

class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


def create_deck():
    initial_deck = []
    initial_deck.extend(
        [Card(color=color, number=0) for color in LIST_COLOR]
    )

    initial_deck.extend(
        [
            Card(color=color, number=number)
            for _ in range(2)
            for color in LIST_COLOR
            for number in range(1, 10)
        ]
    )
    initial_deck.extend(
        [
            Card(color=color, symbol=symbol)
            for _ in range(2)
            for color in LIST_COLOR
            for symbol in ['skip', 'reverse', 'draw2']
        ]
    )

    initial_deck.extend(
        [
            Card(color='any', symbol=symbol)
            for _ in range(4)
            for symbol in ['wild', 'wilddraw4']
        ]
    )

    return initial_deck

class GameState(BaseModel):
    # numbers of cards for each player to start with
    CNT_HAND_CARDS: int = 0
    # any = for wild cards
    LIST_COLOR: List[str] = ['red', 'green', 'yellow', 'blue', 'any']
    # draw2 = draw two cards, wild = chose color, wilddraw4 = chose color and draw 4
    LIST_SYMBOL: List[str] = ['skip', 'reverse', 'draw2', 'wild', 'wilddraw4']
    LIST_CARD: List[Card] = [
        # 76 Numbered Cards
        Card(color='red', number=0), Card(color='green', number=0), Card(color='yellow', number=0),
        Card(color='blue', number=0),
        *[Card(color=color, number=number) for color in ['red', 'green', 'yellow', 'blue'] for number in
          range(1, 10)] * 2,  # Two copies of each 1-9
        # 8 Skip Cards
        *[Card(color=color, symbol='skip') for color in ['red', 'green', 'yellow', 'blue']],
        # 8 Reverse Cards
        *[Card(color=color, symbol='reverse') for color in ['red', 'green', 'yellow', 'blue']],
        # 8 Draw 2 Cards
        *[Card(color=color, symbol='draw2') for color in ['red', 'green', 'yellow', 'blue']],
        # 4 Wild Cards
        Card(color='any', symbol='wild'), Card(color='any', symbol='wild'),
        # 4 Wild Draw 4 Cards
        Card(color='any', symbol='wilddraw4'), Card(color='any', symbol='wilddraw4'),
    ]

    list_card_draw: Optional[List[Card]] = []   # list of cards to draw
    list_card_discard: Optional[List[Card]] = []# list of cards discarded
    list_player: List[PlayerState] = []         # list of player-states
    phase: GamePhase = GamePhase.SETUP          # the current game-phase ("setup"|"running"|"finished")
    cnt_player: int = 0                         # number of players N (to be set in the phase "setup")
    idx_player_active: Optional[int] = 0        # the index (0 to N-1) of active player
    direction: int = 1                          # direction of the game, +1 to the left, -1 to right
    color: str = ''                             # active color (last card played or the chosen color after a wild cards)
    cnt_to_draw: int = 0                        # accumulated number of cards to draw for the next player
    has_drawn: bool = False                     # flag to indicate if the last player has alreay drawn cards or not

    def setup_game(self, players: List[str]) -> None:
        """Initialize the game with players."""
        self.list_player = [PlayerState(name=player) for player in players]
        self.cnt_player = len(players)
        self.list_card_draw = random.sample(self.LIST_CARD, len(self.LIST_CARD))
        self.phase = GamePhase.SETUP
        self.deal_cards()
    
    def deal_cards(self) -> None:
        """Deal cards to each player."""
        for player in self.list_player:
            for _ in range(self.CNT_HAND_CARDS):
                card = self.list_card_draw.pop()
                player.add_card(card)

        # Set initial discard card
        self.list_card_discard.append(self.list_card_draw.pop())
        self.color = self.list_card_discard[-1].color

    def next_player(self) -> None:
        """Advance to the next player."""
        self.idx_player_active = (self.idx_player_active + self.direction) % self.cnt_player

    def reverse_direction(self) -> None:
        """Reverse the direction of play."""
        self.direction *= -1

    def draw_card(self, player_idx: int, count: int = 1) -> None:
        """Draw cards for a player."""
        player = self.list_player[player_idx]
        for _ in range(count):
            if not self.list_card_draw:
                self.reshuffle_discard_pile()
            player.add_card(self.list_card_draw.pop())
    
    def reshuffle_discard_pile(self) -> None:
        """Reshuffle the discard pile into the draw pile."""
        if len(self.list_card_discard) <= 1:
            raise ValueError("Not enough cards in the discard pile to reshuffle.")
        self.list_card_draw = self.list_card_discard[:-1]
        random.shuffle(self.list_card_draw)
        self.list_card_discard = [self.list_card_discard[-1]]


class Uno(Game):

    def __init__(self) -> None:
        """ Important: Game initialization also requires a set_state call to set the number of players """
        self.state = GameState()

    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        self.state = state
        self.state.phase = GamePhase.RUNNING

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        return self.state

    def print_state(self) -> None:
        """ Print the current game state fo debbuging"""
        if not self.state:
            print("Game state has not been initialized")
            return
        
        print("\n==== Game State ====")
        print(f"Phase: {self.state.phase}")
        print(f"Direction: {'Clockwise' if self.state.direction == 1 else 'Counterclockwise'}")
        print(f"Active Player Index: {self.state.idx_player_active}")
        print(f"Active Color: {self.state.color}")
        print(f"Cards to Draw: {self.state.cnt_to_draw}")
        print(f"Has Drawn: {'Yes' if self.state.has_drawn else 'No'}")

        print("\n-- Players --")
        for idx, player in enumerate(self.state.list_player):
            active_marker = " (Active)" if idx == self.state.idx_player_active else ""
            print(f"Player {idx + 1}{active_marker}: {player.name}")
            print(f"  Cards: {[str(card) for card in player.list_card]}")

        print("\n-- Draw Pile --")
        print(f"Cards remaining: {len(self.state.list_card_draw)}")

        print("\n-- Discard Pile --")
        if self.state.list_card_discard:
            print(f"Top Card: {self.state.list_card_discard[-1]}")
        else:
            print("Discard pile is empty.")

        print("====================\n")

        

    def get_list_action(self) -> List[Action]:
        """ Get a list of possible actions for the active player """
        if not self.state:
            raise ValueError("GameState not initialized")

        active_player = self.state.list_player[self.state.idx_player_active]
        possible_actions = []

        for card in active_player.list_card:
            # Check for card number, color, wildcard matches
            if (card.color == self.state.color or 
                card.number == self.state.list_card_discard[-1].number or
                card.color.lower() == 'any'): # wildcards
                action = Action(card=card)
                possible_actions.append(action)

        # if a wild card is played, add actions for choosing colors
        for action in possible_actions:
            if action.card.symbol in ['wild', 'wilddraw4']:
                for color in self.state.LIST_COLOR[:-1]: #excludes 'any'
                    colored_action = Action(card=action.card, color=color)
                    possible_actions.append(colored_action)

        # draw a card if no cards can be played
        if not possible_actions:
            possible_actions.append(Action(draw=1))



    def apply_action(self, action: Action) -> None:
        """ Apply the given action to the game """
        if not self.state: # in case game state has not been initialized
            raise ValueError("Game state has not been initialized")

        # Case 1: Play a card
        if action.card:
            if action.card not in active_player.list_card:
                raise ValueError("Player cannot play a card they don't have")

            # Remove card from player hand
            active_player.list_card.remove(action.card)

            # Add card to discard pile
            self.state.list_card_discard.append(action.card)

            # Update the active color (for wildcards)
            if action.card.symbol in ['wild', 'wilddraw4']:
                if not action.color:
                    raise ValueError("A color must be chosen when playing a wildcard")
                self.state.color = action.color
            else:
                self.state.color = action.card.color

            # Handle special card effects
            if action.card.symbol == 'skip':
                self._skip_next_player()
            elif action.card.symbol == 'reverse':
                self._reverse_direction()
            elif action.card.symbol == 'draw2':
                self.state.cnt_to_draw += 2
            elif action.card.symbol == 'wilddraw4':
                self.state.cnt_to_draw += 4

            # Validate UNO call
            if len(active_player.list_card) == 1 and not action.uno:
                print(f"Player {active.player.name} failed to call UNO!")

        elif action.draw:
            self._draw_cards(self.state.idx_player_active, action.draw)

        # Move to the next player
        self._advance_to_next_player()

    def _skip_next_player(self) -> None:
        """Skip the next player's turn"""
        self._advance_to_next_player()

    def _reverse_direction(self) -> None:
        """Reverse direction of play"""
        self.state.direction *= -1

    def _draw_cards(self, player_index:int, count:int) -> None:
        """Draw cards from the draw pile and add to player's hand"""
        player = self.state.list_player[player_index]
        for _ in range(count):
            if not self.state.list_card_discard:
                # reshuffle discard pile into draw pile if empty
                self._reshuffle_discard_pile()
            player.list_card.append(self.state.list_card_draw.pop())

    def _reshuffle_discard_pile(self) -> None:
        """Reshuffle the discard pile into the draw pile"""
        if len(self.state.list_card_discard) <= 1:
            raise ValueError("Not enough cards to reshuffle")
        self.state.list_card_draw = self.state.list_card_discard[:-1]
        random.shuffle(self.state.list_card_draw)
        self.state.list_card_discard = [self.state.list_card_discard[-1]]

    def _advance_to_next_player(self) -> None:
        """Advance to the next player in the correct direction"""
        self.state.idx_player_active = (self.state.idx_player_active + self.state.direction % self.state.cnt_player)


    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        if not self.state:
            raise ValueError("Game state has not been initialized")

        # clone current state to create masked view
        masked_state = self.state.copy(deep=True)

        # Mask the cards of all other players
        for i, player in enumerate(masked_state.list_player):
            if i != idx.player:
                # replace the list of cards with a placeholder showing card count
                player.list_card = [Card() for _ in range(len(player.list_card))]

        # reveal current player's hand
        masked_state.list_player[idx_player].list_card = self.state.list_player[idx_player].list_card

        # mask draw pile (size can be revealed but not cards)
        masked_state.list_card_draw = [Card() * len(self.state.list_card_draw)]

        # return masked state
        return masked_state


class RandomPlayer(Player):
    def __init__(self, name: str = "Player") -> None:
        self.state=PlayerState(name= name)

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        if not actions:
            print(f"{self.state.name} hase no valid actions to undertake and must wither draw or skip.")

        action = random.choice(actions) # randomly chooses an action

        # wildcard case action
        if action.card and action.card.symbol in ["wild", "wildcard4"]:
            action.color = random.choice(state.LIST_COLOR[:-1]) # chooses a color not 'any'

        # UNO case action
        if len(self.state.list_card)==1:
            action.uno=True
            print(f"{self.state.name} UNO. Game won! ")


        #if len(actions) > 0:
        #    return random.choice(actions)
        return action


if __name__ == '__main__':

    uno = Uno()
    state = GameState(cnt_player=3)
    uno.set_state(state)

