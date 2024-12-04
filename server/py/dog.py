# runcmd: cd ../.. & venv\Scripts\python server/py/dog_template.py

import random
from typing import List, Optional, ClassVar
from enum import Enum
from pydantic import BaseModel

if __name__ == '__main__':
    from game import Game, Player
else:
    from server.py.game import Game, Player


class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank


class Marble(BaseModel):
    pos: str       # position on board (0 to 95)
    is_save: bool  # true if marble was moved out of kennel and was not yet moved


class PlayerState(BaseModel):
    name: str                  # name of player [PlayerBlue, PlayerRed, PlayerYellow, PlayerGreen]
    list_card: List[Card]      # list of cards
    list_marble: List[Marble]  # list of marbles


class Action(BaseModel):
    card: Card                 # card to play
    pos_from: Optional[int]    # position to move the marble from
    pos_to: Optional[int]      # position to move the marble to
    card_swap: Optional[Card]  # optional card to swap ()


class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class GameState(BaseModel):

    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']  # 4 suits (colors)
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10',      # 13 ranks + Joker
        'J', 'Q', 'K', 'A', 'JKR'
    ]
    LIST_CARD: ClassVar[List[Card]] = [
        # 2: Move 2 spots forward
        Card(suit='♠', rank='2'), Card(suit='♥', rank='2'), Card(suit='♦', rank='2'), Card(suit='♣', rank='2'),
        # 3: Move 3 spots forward
        Card(suit='♠', rank='3'), Card(suit='♥', rank='3'), Card(suit='♦', rank='3'), Card(suit='♣', rank='3'),
        # 4: Move 4 spots forward or back
        Card(suit='♠', rank='4'), Card(suit='♥', rank='4'), Card(suit='♦', rank='4'), Card(suit='♣', rank='4'),
        # 5: Move 5 spots forward
        Card(suit='♠', rank='5'), Card(suit='♥', rank='5'), Card(suit='♦', rank='5'), Card(suit='♣', rank='5'),
        # 6: Move 6 spots forward
        Card(suit='♠', rank='6'), Card(suit='♥', rank='6'), Card(suit='♦', rank='6'), Card(suit='♣', rank='6'),
        # 7: Move 7 single steps forward
        Card(suit='♠', rank='7'), Card(suit='♥', rank='7'), Card(suit='♦', rank='7'), Card(suit='♣', rank='7'),
        # 8: Move 8 spots forward
        Card(suit='♠', rank='8'), Card(suit='♥', rank='8'), Card(suit='♦', rank='8'), Card(suit='♣', rank='8'),
        # 9: Move 9 spots forward
        Card(suit='♠', rank='9'), Card(suit='♥', rank='9'), Card(suit='♦', rank='9'), Card(suit='♣', rank='9'),
        # 10: Move 10 spots forward
        Card(suit='♠', rank='10'), Card(suit='♥', rank='10'), Card(suit='♦', rank='10'), Card(suit='♣', rank='10'),
        # Jake: A marble must be exchanged
        Card(suit='♠', rank='J'), Card(suit='♥', rank='J'), Card(suit='♦', rank='J'), Card(suit='♣', rank='J'),
        # Queen: Move 12 spots forward
        Card(suit='♠', rank='Q'), Card(suit='♥', rank='Q'), Card(suit='♦', rank='Q'), Card(suit='♣', rank='Q'),
        # King: Start or move 13 spots forward
        Card(suit='♠', rank='K'), Card(suit='♥', rank='K'), Card(suit='♦', rank='K'), Card(suit='♣', rank='K'),
        # Ass: Start or move 1 or 11 spots forward
        Card(suit='♠', rank='A'), Card(suit='♥', rank='A'), Card(suit='♦', rank='A'), Card(suit='♣', rank='A'),
        # Joker: Use as any other card you want
        Card(suit='', rank='JKR'), Card(suit='', rank='JKR'), Card(suit='', rank='JKR')
    ] * 2

    cnt_player: int = 4                             # number of players (must be 4)
    phase: GamePhase  = GamePhase.SETUP             # current phase of the game
    cnt_round: int = 0                              # current round
    bool_card_exchanged: bool = False               # true if cards was exchanged in round
    idx_player_started: int = random.randint(0,3)   # index of player that started the round
    idx_player_active: int =idx_player_started      # index of active player in round
    list_player: List[PlayerState] = []             # list of players
    list_card_draw: List[Card] = LIST_CARD       # list of cards to draw
    list_card_discard: List[Card] = []              # list of cards discarded
    card_active: Optional[Card]   = None             # active card (for 7 and JKR with sequence of actions)

    def setup_players(self) ->None:
        player_blue = PlayerState(
                name="PlayerBlue",
                list_card=[],
                list_marble=[Marble(pos="64", is_save=True), 
                             Marble(pos="65", is_save=True),
                             Marble(pos="66", is_save=True),
                             Marble(pos="67", is_save=True)]
                )
        player_green = PlayerState(
                name="PlayerGreen",
                list_card=[],
                list_marble=[Marble(pos="72", is_save=True), 
                             Marble(pos="73", is_save=True),
                             Marble(pos="74", is_save=True),
                             Marble(pos="75", is_save=True)]
                )
        player_red = PlayerState(
                name="PlayerRed",
                list_card=[],
                list_marble=[Marble(pos="80", is_save=True), 
                             Marble(pos="81", is_save=True),
                             Marble(pos="82", is_save=True),
                             Marble(pos="83", is_save=True)]
                )
        player_yellow = PlayerState(
                name="PlayerYellow",
                list_card=[],
                list_marble=[Marble(pos="88", is_save=True), 
                             Marble(pos="89", is_save=True),
                             Marble(pos="90", is_save=True),
                             Marble(pos="91", is_save=True)]
                )
        self.list_player = [player_blue,player_green,player_red,player_yellow]

    def deal_cards(self) -> bool:
        # Check if all players are out of cards.
        for player in self.list_player:
            if not player.list_card:
                continue
            else:
                print(f"{player.name} has still {len(player.list_card)} card's")
                return False

        # Go to next Gameround
        self.cnt_round +=1

        # get number of Cards
        cards_per_round = [6, 5, 4, 3, 2]
        for i in range(1, 12):
            # Ermitteln der Kartenanzahl durch Modulo-Operation
            num_cards = cards_per_round[(i - 1) % len(cards_per_round)]

        # Check if there are enough cards in the draw deck; if not, add a new card deck.
        if num_cards*4 > len(self.list_card_draw):
            ## reshuffle the Deck
            self.list_card_draw = GameState.LIST_CARD
            self.list_card_discard = []

        # Randomly select cards for players.
        for player in self.list_player:
            player.list_card = random.sample(self.list_card_draw, num_cards)
            for card in player.list_card :
                self.list_card_draw.remove(card)

        return True


    def get_list_possible_action(self) -> List[Action]:
        '''
        List of Action from active players Cards

        '''
        pass

    def set_action_to_game(self, action: Action):
        '''
        Make the Action to the board
        Marvel pos 15 to pos 18
        '''

        pass

    def check_final_pos(pos:int) -> bool:
        '''
        Pos Blocked
        '''
        pass

    def sending_home(pos:int) -> None: # Set player X Marvel home
        '''
        Pos of other player ==> Sending Home
        '''
        pass
           

class Dog(Game):

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """
        self.state = GameState()
        self.state.setup_players()
        self.state.phase = GamePhase.RUNNING
        self.state.deal_cards()
        print("debug X all done")
      
    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        self.state = state

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        return self.state

    def print_state(self) -> None:
        """ Print the current game state """
        pass

    def get_list_action(self) -> List[Action]:
        """ Get a list of possible actions for the active player """
        pass

    def apply_action(self, action: Action) -> None:
        """ Apply the given action to the game """
        pass

    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        pass


class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == '__main__':

    game = Dog()
    print(len(game.state.list_card_draw))
    print("Neue Karten Vergeben mit bestehenden Karten? ", game.state.deal_cards())
    print
