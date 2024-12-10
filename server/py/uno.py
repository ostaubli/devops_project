# -runcmd: cd ../.. & venv\Scripts\python server/py/uno.py
# runcmd: cd ../.. & venv\Scripts\python benchmark/benchmark_uno.py python uno.Uno
from PIL.ImImagePlugin import number
from dataclasses import field

from PIL.ImageColor import colormap
from fontTools.cffLib import topDictOperators
from numpy.ma.core import append

from server.py.game import Game, Player #from server.py.game import Game, Player
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
import random

LIST_COLOR: List[str] = ['red', 'blue', 'yellow', 'green']
# draw2 = draw two cards, wild = chose color, 
# wilddraw4 = chose color and draw 4
LIST_SYMBOL: List[str] = ['skip', 'reverse', 'draw2', 'wild', 'wilddraw4']

def compare_tuples_for_lt(t1:tuple, t2:tuple) -> bool:
    """ Compares two tuples element-wise for less-than ordering.
    Handles 'None' values as less than any other
    """
    for v1, v2 in zip(t1, t2):
        if v1 is None and v2 is None:
            continue

        if v1 is None:
            return True

        if v2 is None:
            return False
            
        if v1 < v2:
            return True

        if v1 > v2:
            return False

    return False


class Card(BaseModel):
    color: Optional[str] = None   # color of the card (see LIST_COLOR)
    number: Optional[int] = None  # number of the card (if not a symbol card)
    symbol: Optional[str] = None  # special cards (see LIST_SYMBOL)

    def __lt__(self, other):
        """ This method checks if one Card object is less than another,
        using the global method compare_tuples_for_lt()
        """
        if not isinstance(other, Card):
            return False
        t1 = (self.color, self.number, self.symbol)
        t2 = (other.color, other.number, other.symbol)
        return compare_tuples_for_lt(t1, t2)

    def __eq__(self, other):
        """ Checks to see if two Card objects are equal
        """
        if not isinstance(other, Card): return False
        other: Card = other

        t1 = (self.color, self.number, self.symbol,)
        t2 = (other.color, other.number, other.symbol,)

        return t1 == t2

class Action(BaseModel):
    card: Optional[Card] = None  # the card to play
    number:Optional[int] = None
    color: Optional[str] = None  # the chosen color to play (for wild cards)
    draw: Optional[int] = None   # number of cards to draw for the next player
    uno: bool = False            # announce "UNO" with the second last card

    def __lt__(self, other):
        """ Method checks if one Action object is less than another one,
        uses the global method ocmpare_tuples_for_lt()
        """
        t1 = (self.card, self.color, self.draw, self.uno)
        t2 = (other.card, other.color, other.draw, other.uno)
        return compare_tuples_for_lt(t1, t2)

class PlayerState(BaseModel):
    name: Optional[str] = None  # name of player
    list_card: List[Card] = field(default_factory=list)  # list of cards

    @staticmethod
    def _display_deco(function):
        """ Decorator to format the output of the display method, 
        created within this class. """
        def inner(*args, **kwargs):
            print("---- Player State ----")
            result = function(*args, **kwargs)
            print("-----------------------")
            return result
        return inner 

    def add_card(self, card: Card):
        """ Add a card to the player's hand card-stack, 
        when the player pulls a card. """
        self.list_card.append(card)

    def play_card(self, card: Card):
        """ Remove a card from the player's hand stack, 
        when the player plays a card. """
        if card in self.list_card:
            self.list_card.remove(card)

    def check_uno(self) -> bool:
        """ Check whether the player has only one card left to play. """
        uno_card = len(self.list_card) == 1
        return uno_card
    
    def check_no_cards(self) -> bool:
        """ Check whether the player has no cards to play anymore. 
        Then the player won the game. """
        no_card = len(self.list_card) == 0
        return no_card
    
    @_display_deco
    def display_player_state(self):
        """ Display the player's current state and hand card stack. """
        print(f"Player: {self.name}")
        print("Current cards in hand: ", 
            [str(card) for card in self.list_card]
            )
    

class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


def create_deck() -> List[Card]:
    """Creates the initial game deck."""
    deck = []

    # Add one zero card for each color
    deck.extend([Card(color=color, number=0) for color in LIST_COLOR])

    # Add two copies of each numbered card (1–9) for each color
    deck.extend([
        Card(color=color, number=number)
        for color in LIST_COLOR
        for number in range(1, 10)
        for _ in range(2)
    ])

    # Add two copies of each action card (skip, reverse, draw2) for each color
    deck.extend([
        Card(color=color, symbol=symbol)
        for color in LIST_COLOR
        for symbol in ['skip', 'reverse', 'draw2']
        for _ in range(2)
    ])

    # Add four copies of wild cards (wild, wilddraw4)
    deck.extend([
        Card(color='any', symbol=symbol)
        for symbol in ['wild', 'wilddraw4']
        for _ in range(4)
    ])

    return deck

class GameState(BaseModel):
    # numbers of cards for each player to start with
    CNT_HAND_CARDS: int = 0
    # any = for wild cards
    list_card_draw: Optional[List[Card]] = field(
        default_factory=create_deck
        )  # list of cards to draw
    list_card_discard: Optional[List[Card]] = field(
        default_factory=list
        )  # list of cards discarded
    list_player: List[PlayerState] = field(
        default_factory=list
        )  # list of player-states

    # the current game-phase ("setup"|"running"|"finished")
    phase: GamePhase = GamePhase.SETUP
    # number of players N (to be set in the phase "setup")
    cnt_player: int = 0
    # the index (0 to N-1) of active player
    idx_player_active: Optional[int] = 0
    # direction of the game, +1 to the left, -1 to right
    direction: int = 1
    # active color (last card played or the chosen color after a wild cards)
    color: str = ''
    # accumulated number of cards to draw for the next player
    cnt_to_draw: int = 0
    # flag to indicate if the last player has alreay drawn cards or not
    has_drawn: bool = False

    def setup_game(self, players: List[str]) -> None:
        """Initialize the game with players."""
        self.list_player = [PlayerState(name=player) for player in players]
        self.cnt_player = len(players)
        self.list_card_draw = random.sample(
            self.LIST_CARD, len(self.LIST_CARD)
            )
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
        self.idx_player_active = (
            self.idx_player_active + self.direction
            ) % self.cnt_player

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
            raise ValueError(
                "Not enough cards in the discard pile to reshuffle."
                )
        self.list_card_draw = self.list_card_discard[:-1]
        random.shuffle(self.list_card_draw)
        self.list_card_discard = [self.list_card_discard[-1]]

class Uno(Game):

    def __init__(self) -> None:
        """ Important: Game initialization also requires a 
        set_state call to set the number of players """
        self.state = GameState()

    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        self.state = state

        if len(self.state.list_card_discard) == 0:
            self.state.list_card_discard = [
                state.list_card_draw.pop()
                ] if state.list_card_draw else []

        if len(self.state.list_player) != self.state.cnt_player:
            self.state.list_player = [
                PlayerState() for i in range(state.cnt_player)
                ]

        self.state.idx_player_active = state.idx_player_active
        active_player = self.state.list_player[self.state.idx_player_active]
        self.state.direction = 1

        top_card = self.state.list_card_discard[-1]
        if top_card.symbol == 'draw2':
            self.state.cnt_to_draw += 2
        if top_card.symbol == 'wilddraw4' and len(
            self.state.list_card_discard
            ) == 1:

            self.state.list_card_discard.append(state.list_card_draw.pop())
        if top_card.symbol == 'reverse':
            self.state.direction *= -1
        if top_card.symbol == 'skip':  # check this <<<<<==
            self.state.idx_player_active += 1
            self.state.idx_player_active %= self.state.cnt_player

        for i in range(self.state.CNT_HAND_CARDS):
            for player in self.state.list_player:
                player.list_card.append(state.list_card_draw.pop())

        self.state.phase = GamePhase.RUNNING

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        return self.state


    def get_list_action(self) -> List[Action]:
        """ Get a list of possible actions for the active player """
        if not self.state:
            raise ValueError("GameState not initialized")
        possible_actions = []
        active_player = self.state.list_player[self.state.idx_player_active]
        #possible_actions = []

        top_card = self.state.list_card_discard[-1]

        if (top_card.symbol == 'wild' and
        len(self.state.list_card_discard) == 1):
            for my_card in active_player.list_card:
                possible_actions.append(
                    Action(card=my_card, color=my_card.color)
                    )

            return possible_actions

        if not self.state.has_drawn:
            possible_actions.append(Action(draw=1))

        if top_card.symbol is None:
            for my_card in active_player.list_card:
            # print(f"{my_card=}")
                if my_card == top_card:
                    possible_actions.append(
                        Action(card=my_card, color=my_card.color)
                        )

                elif my_card.number == top_card.number:
                # possible_actions.append(Action(draw=1))
                    possible_actions.append(
                        Action(card=my_card, color=my_card.color)
                        )

                elif my_card.color == top_card.color:
                    possible_actions.append(
                        Action(card=my_card, color=my_card.color)
                        )

                if my_card.symbol == "wilddraw4":
                    for color in LIST_COLOR:
                        possible_actions.append(
                            Action(card=my_card, color=color, draw=4)
                        )

                if my_card.symbol == "wild":
                    for color in LIST_COLOR:
                        possible_actions.append(
                            Action(card=my_card, color=color)
                        )

                if my_card.symbol == "draw2":
                    if my_card.color == top_card.color:
                        possible_actions.append(
                            Action(card=my_card, color=color, draw=2)
                        )

                if my_card.symbol == "skip":
                    if my_card.color == top_card.color:
                        possible_actions.append(
                            Action(card=my_card, color=color)
                        )
        #                  idx_player_next = (idx_player_active + 2 * 
        #                   direction + cnt_player) % cnt_player
        #  rule for apply action test 014
                if my_card.symbol == "reverse":
                    if my_card.color == top_card.color:
                        possible_actions.append(
                            Action(card=my_card, color=color)
                        )


        if top_card.symbol is not None:
            if top_card.symbol == 'skip':
                for my_card in active_player.list_card:
                    if my_card.symbol == "skip":
                        possible_actions.append(
                            Action(card=my_card, color=my_card.color)
                            )
                    if (my_card.symbol == "reverse" and 
                    my_card.color == top_card.color):
                        possible_actions.append(
                            Action(card=my_card, color=my_card.color)
                            )
                    if (my_card.symbol is None and
                    my_card.color == top_card.color):
                        possible_actions.append(
                            Action(card=my_card, color=my_card.color)
                            )

            elif top_card.symbol == "reverse":
                for my_card in active_player.list_card:
                    if my_card.symbol == "reverse":
                        possible_actions.append(
                            Action(card=my_card, color= my_card.color)
                            )
                    if (my_card.symbol == 'skip' and
                    my_card.color == top_card.color):
                        possible_actions.append(
                            Action(card=my_card, color=my_card.color)
                            )
                    if (my_card.symbol == "draw2" and
                    my_card.color == top_card.color):
                        possible_actions.append(
                            Action(
                                card=my_card, color=my_card.color, draw = 2
                                )
                            )
                    if (my_card.symbol is None and
                    my_card.color == top_card.color):
                        possible_actions.append(
                            Action(card=my_card, color=my_card.color)
                            )

            elif top_card.symbol == "draw2":

                can_we_cover_this = False
                for my_card in active_player.list_card:
                    if my_card.symbol == "draw2":
                        can_we_cover_this = True
                        possible_actions.append(
                            Action(card=my_card, color=my_card.color, draw=2)
                            )
                    if (my_card.symbol == 'skip' and
                    my_card.color == top_card.color):
                        can_we_cover_this = True
                        possible_actions.append(
                            Action(card=my_card, color=my_card.color)
                            )
                    if (my_card.symbol is None and
                    my_card.color == top_card.color):
                        can_we_cover_this = True
                        possible_actions.append(
                            Action(card=my_card, color=my_card.color)
                            )

                if not can_we_cover_this:
                    possible_actions[0].draw = 2

            elif top_card.symbol == "wilddraw4":

                if my_card.symbol == "wilddraw4":
                   for color in LIST_COLOR:
                       possible_actions.append(
                        Action(card=my_card, color=color, draw=4)
                        )
                if (my_card.symbol is None and
                my_card.color == top_card.color):
                    possible_actions.append(
                        Action(card=my_card, color=my_card.color)
                        )




        return possible_actions

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


    def print_state(self) -> None:
        """ Print the current game state fo debbuging"""
        if not self.state:
            print("Game state has not been initialized")
            return

        print("\n==== Game State ====")
        print(f"Phase: {self.state.phase}")
        print(f"""Direction: {
            'Clockwise' if self.state.direction == 1 else 'Counterclockwise'
            }""")
        print(f"Active Player Index: {self.state.idx_player_active}")
        print(f"Active Color: {self.state.color}")
        print(f"Cards to Draw: {self.state.cnt_to_draw}")
        print(f"Has Drawn: {'Yes' if self.state.has_drawn else 'No'}")

        print("\n-- Players --")
        for idx, player in enumerate(self.state.list_player):
            active_marker = (
                " (Active)" if idx == self.state.idx_player_active else ""
            )
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



    def apply_action(self, action: Action) -> None:
        """ Apply the given action to the game """
        if not self.state: # in case game state has not been initialized
            raise ValueError("Game state has not been initialized")

        active_player = self.state.list_player[self.state.idx_player_active]
        # print(f"\t\t WE TRY TO APPLY THIS ACTION: {action=}")
        # Test 11 Try
        # if action.draw != 0 and not self.state.has_drawn:
        #     self.state.has_drawn = True
        #     card = self.state.list_card_draw.pop()
        #     # print(f"\t\tWE GET THIS CARD {card=}")
        #     self.state.list_player[
        #         self.state.idx_player_active
        #         ].list_card.append(card)

        # actions = self.get_list_action()

        if action.draw and not self.state.has_drawn:
            self.state.has_drawn = True
            card = self.state.list_card_draw.pop()
            active_player.add_card(card)

        # Do not advance the turn if only drawing
            return

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
                    raise ValueError(
                        "A color must be chosen when playing a wildcard"
                        )
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

        #elif action.draw:
        #    self._draw_cards(self.state.idx_player_active, action.draw)

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
        self.state.idx_player_active = (
            self.state.idx_player_active + self.state.direction %
            self.state.cnt_player
            )


    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player 
        (e.g. the oppontent's cards are face down)"""
        if not self.state:
            raise ValueError("Game state has not been initialized")

        # clone current state to create masked view
        masked_state = self.state.copy(deep=True)

        # Mask the cards of all other players
        for i, player in enumerate(masked_state.list_player):
            if i != idx.player:
                # replace the list of cards with a 
                # placeholder showing card count
                player.list_card = [
                    Card() for _ in range(len(player.list_card))
                    ]

        # reveal current player's hand
        masked_state.list_player[
            idx_player
            ].list_card = self.state.list_player[idx_player].list_card

        # mask draw pile (size can be revealed but not cards)
        masked_state.list_card_draw = [
            Card() * len(self.state.list_card_draw)
            ]

        # return masked state
        return masked_state


class RandomPlayer(Player):
    def __init__(self, name: str = "Player") -> None:
        self.state=PlayerState(name= name)

    def select_action(self, state: GameState,
                actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions,
        select the next action """
        if not actions:
            print(f"""{self.state.name} hase no valid actions 
            to undertake and must wither draw or skip.""")

        action = random.choice(actions) # randomly chooses an action

        # wildcard case action
        if (action.card and 
        action.card.symbol in ["wild", "wildcard4"]):
            action.color = random.choice(
                state.LIST_COLOR[:-1]) # chooses a color not 'any'

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

