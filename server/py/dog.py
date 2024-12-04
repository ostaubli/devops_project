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
    list_card_draw: List[Card] = LIST_CARD       # list of cards to draw ==> Was list_id_card_draw in given Template
    list_card_discard: List[Card] = []              # list of cards discarded
    card_active: Optional[Card]   = None             # active card (for 7 and JKR with sequence of actions)

    def setup_players(self) ->None: # Kägi
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

    def deal_cards(self) -> None: # Kägi
        # Check if all players are out of cards.
        for player in self.list_player:
            if not player.list_card:
                continue
            else:
                print(f"{player.name} has still {len(player.list_card)} card's")
                return

        # Go to next Gameround
        self.cnt_round +=1

        # get number of Cards
        cards_per_round = [6, 5, 4, 3, 2]
        num_cards = cards_per_round[(self.cnt_round - 1) % len(cards_per_round)]
        
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


    def get_list_possible_action(self) -> List[Action]: #Nicolas
        '''
        List of Action from active players Cards

        TODO: Home Handling to do
        TODO: Marble blocks the way (RULE) if new on start
        '''
        list_steps_split_7 = [
            [1, 1, 1, 1, 1, 1, 1],
            [2, 1, 1, 1, 1, 1],
            [2, 2, 1, 1, 1],
            [2, 2, 2, 1],
            [3, 1, 1, 1, 1],
            [3, 2, 1, 1],
            [3, 2, 2],
            [3, 3, 1],
            [4, 1, 1, 1],
            [4, 2, 1],
            [4, 3],
            [5, 2],
            [6, 1],
        ]
        active_player = self.list_player[self.idx_player_active]
        cards = active_player.list_card
        marbles = active_player.list_marbles

        action_list = []
        for marble in marbles:
            for card in cards:
                match card.rank:
                    case '2':
                        action_list.append(Action(card = card,pos_from = marble.pos, pos_to = ((marble.pos + 2) % 64 )))
                    case '3':
                        action_list.append(Action(card = card,pos_from = marble.pos, pos_to = ((marble.pos + 3) % 64 )))
                    case '4':
                        action_list.append(Action(card = card,pos_from = marble.pos, pos_to = ((marble.pos + 4) % 64 )))
                        action_list.append(Action(card = card,pos_from = marble.pos, pos_to = ((marble.pos - 4) % 64 )))
                    case '5':
                        action_list.append(Action(card = card,pos_from = marble.pos, pos_to = ((marble.pos + 5) % 64 )))
                    case '6':
                        action_list.append(Action(card = card,pos_from = marble.pos, pos_to = ((marble.pos + 6) % 64 )))
                    case '7':
                        for steps_split in list_steps_split_7:
                            for i, steps in enumerate(steps_split):
                                action_list.append(Action(card = card,pos_from = marble.pos, pos_to = (marble.pos + steps) % 64))
                    case '8':
                        action_list.append(Action(card=card, pos_from=marble.pos, pos_to=((marble.pos + 8) % 64)))
                    case '9':
                        action_list.append(Action(card=card, pos_from=marble.pos, pos_to=((marble.pos + 9) % 64)))
                    case '10':
                        action_list.append(Action(card=card, pos_from=marble.pos, pos_to=((marble.pos + 10) % 64)))
                    case 'J':
                        #TODO Jake Logic
                        pass
                    case 'Q':
                        action_list.append(Action(card=card, pos_from=marble.pos, pos_to=((marble.pos + 12) % 64)))
                    case 'K':
                        action_list.append(Action(card=card, pos_from=marble.pos, pos_to=((marble.pos + 13) % 64)))
                        #TODO Going Out
                    case 'A':
                        action_list.append(Action(card=card, pos_from=marble.pos, pos_to=((marble.pos + 11) % 64)))
                        action_list.append(Action(card=card, pos_from=marble.pos, pos_to=((marble.pos + 1) % 64)))
                        #TODO Going OUT
                    case 'JKR':
                       pass








        '''        
        Define Each Action for Each Card
        
        Cards 2-10 Ex 7/4 -> Move One Marble the Amount of Value
        Card 4 -> Move one Marble +4 or -4
        Card 7 -> Move one to four Marbles in total of 7
        Card Ace -> Move one Marble 1 or 11 or get out
        Card Queen -> Move one Marble 12
        Card King -> Move one Marble 13 or get out
        Card Jake -> Marble position Exchange
        Card Joker -> Card Swap
        
        
        
        '''




    def set_action_to_game(self, action: Action):
        """
        Apply the given action to the game state.
        Moves the marble from pos_from to pos_to based on the action,
        and handles special cases like sending marbles home and marking marbles as safe.
        """
        # Get the active player
        active_player = self.list_player[self.idx_player_active]

        # Ensure the card played is in the player's hand
        if action.card not in active_player.list_card:
            raise ValueError("The card played is not in the active player's hand.")

        # Ensure pos_from and pos_to are defined
        if action.pos_from is None or action.pos_to is None:
            raise ValueError("Both pos_from and pos_to must be specified for the action.")

        # Find the marble to move based on pos_from
        marble_to_move = next((m for m in active_player.list_marble if m.pos == str(action.pos_from)), None)
        if not marble_to_move:
            raise ValueError(f"No marble found at the specified pos_from: {action.pos_from}")

        # Update the marble's position
        marble_to_move.pos = str(action.pos_to)

        # Check if the marble's new position is in a final or safe zone
        self.check_final_pos(pos_to=action.pos_to, pos_from=action.pos_from, marble=marble_to_move)

        # Handle cases where another player's marble occupies the destination
        for player in self.list_player:
            if player != active_player:
                opponent_marble = next((m for m in player.list_marble if m.pos == str(action.pos_to)), None)
                if opponent_marble:
                    self.sending_home(opponent_marble)  # Send the opponent's marble home

        # Discard the played card
        active_player.list_card.remove(action.card)
        self.list_card_discard.append(action.card)

        # Handle special cards
        if action.card.rank == '7':
            # 7 allows multiple movements; the game logic should track additional actions
            self.card_active = action.card
        elif action.card.rank == 'J':
            # J allows swapping marbles (specific logic to be implemented separately)
            pass
        elif action.card.rank == 'JKR':
            # Joker allows flexibility, which may require additional rules
            pass
        else:
            # Reset the active card for regular actions
            self.card_active = None



    def check_final_pos(self, pos_to: int, pos_from: int, marble: Marble) -> None:
        '''
        Check whether the final position of the marble is a special position.
        1) The marble is save if it is in one of the four final spots of its color or
        2) if it is newly out of the kennel.
        '''
        final_positions: list = [68, 69, 70, 71, 76, 77, 78, 79, 84, 85, 86, 87, 92, 93, 94, 95]
        if pos_to in final_positions:
            marble.is_save = True

        last_positions: list = [64, 65, 66, 67, 72, 73, 74, 75, 80, 81, 82, 83, 88, 89, 90, 91]
        if pos_from in last_position:
            marble.is_save = True

    def sending_home(self, murmel: Marble) -> None:  # Set player X Marvel home
        '''
        Function to send a player home. There are two possibilities:
        1) a marble of another player lands exactly on the position of my marble
        2) my marble gets jumped over by a marble with a 7-card.
        '''

        # First case
        for player in self.list_player:
            for marble in player.list_marble:
                if marble.pos == self.pos_to:
                    marble.pos = 0 # Anpassen. Marble zurück auf Startposition. Wie definieren wir die Startposition? Fix zuweisen oder Logik?
                    marble.is_save = True

        # Second case
        if Action.card.rank == 7:           # Müssen wir hier noch eine Action mitgeben?
            for player in self.list_player:
                for marble in player.list_marble:
                    if murmel.pos_from < marble.pos < murmel.pos_to and marble.is_save == False:
                        marble.pos = 0 # Anpassen. Marble zurück auf Startposition. Wie definieren wir die Startposition? Fix zuweisen oder Logik?
                        marble.is_save = True


    def init_next_turn(self) -> None: # Kägi
        '''
        If action is finished, set the next player active.

        Logic:
        - Iterate over players starting from the one next to the current active player.
        - Check if the next player has cards:
        1. If True, leave the loop and set this player as the active one.
        2. If False, skip to the next player.
        3. If the loop completes a full cycle back to the active player without finding any player with cards, deal new cards and set the active player to the next in normal order.
        '''

        # TODO: Kägi needs to test this (bedtime now)

        #TODO: Laurcence alternative for going to the next turn in one Line
        # self.state.idx_player_active = (self.state.idx_player_active + 1)%4

        pass
        idx_next_player = self.idx_player_active + 1 if self.idx_player_active + 1 < 4 else 0

        while not self.list_player[idx_next_player].list_card and idx_next_player!=self.idx_player_active:# logic 3
            idx_next_player = idx_next_player + 1 if idx_next_player + 1 < 4 else 0

        else:
            if not self.list_player[idx_next_player].list_card:# logic 3
                self.idx_player_active = self.idx_player_active + 1 if self.idx_player_active + 1 < 4 else 0
                self.deal_cards()
            else: # logic 1 & 2
                self.idx_player_active = idx_next_player


class Dog(Game):

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """

        self.state = GameState()
        self.state.setup_players()
        self.state.phase = GamePhase.RUNNING
        self.state.deal_cards() # deal first cards to players
      
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
        """ Apply the given action to the game 
        Aktion auf das spielbrett übertragen ==> Gamestate verändern
        Logiken:
        1.1 Normaler Zug von ausgangspos zu zielpos gilt für alle karte ausser JKR, 7 und Jack
        1.2 7 spezialkarte welche 7 x einen schritt machen kann
        1.3 Jack tauscht zwei kugeln miteinander NOTE: Muss eine davon eine eigene Kugel sein?
        1.4 JKR kann alle logiken von 1 bis und mit 3 aufweisen NOTE: Idee für umsetzung?

        2. Wenn Zug abgeschlossen Aktiver spieler weitergeben
        """
        # TODO: Logik 1.1

        # TODO: Logik 1.2

        # TODO: Logik 1.3

        # TODO: Logik 1.4
        
        # TODO: Logik 2
        
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
