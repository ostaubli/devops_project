# runcmd: cd ../.. & venv\Scripts\python server/py/dog_template.py
#import sys
#import os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


from server.py.game import Game, Player
from typing import List, Optional, ClassVar
from pydantic import BaseModel
from enum import Enum
import random
from pprint import pprint


class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank


class Marble(BaseModel):
    pos: str       # position on board (0 to 95)
    is_save: bool  # true if marble was moved out of kennel and was not yet moved


class PlayerState(BaseModel):
    name: str                  # name of player
    list_card: List[Card]      # list of cards
    list_marble: List[Marble]  # list of marbles
    teamMate: str


class Action(BaseModel):
    card: Optional[Card] = None           # Make optional
    pos_from: Optional[int] = None        # Make optional
    pos_to: Optional[int] = None          # Make optional
    card_swap: Optional[Card] = None      # Make optional)


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

    cnt_player: int = 4                # number of players (must be 4)
    phase: GamePhase                   # current phase of the game
    cnt_round: int                     # current round
    bool_card_exchanged: bool          # true if cards was exchanged in round
    idx_player_started: int            # index of player that started the round
    idx_player_active: int             # index of active player in round
    list_player: List[PlayerState]     # list of players
    list_card_draw: List[Card]         # list of cards to draw
    list_card_discard: List[Card]      # list of cards discarded
    card_active: Optional[Card]        # active card (for 7 and JKR with sequence of actions)

    def get_card_steps(self, rank: str) -> int:
        """ Return the number of steps based on the card rank """
        if rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10']:
            return int(rank)
        elif rank in ['Q']:
            return 12
        elif rank in ['K']:
            return 13


class Dog(Game):

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """
        # Shuffle the cards
        shuffled_cards = random.sample(GameState.LIST_CARD, len(GameState.LIST_CARD))

        # Setup the board with 95 places and initial marble positions
        blue_marbles = [Marble(pos=str(i), is_save=True) for i in range(64, 68)]
        green_marbles = [Marble(pos=str(i), is_save=True) for i in range(72, 76)]
        red_marbles = [Marble(pos=str(i), is_save=True) for i in range(80, 84)]
        yellow_marbles = [Marble(pos=str(i), is_save=True) for i in range(88, 92)]

        # Initialize players
        self.state = GameState(
            cnt_player=4,
            phase=GamePhase.SETUP,
            cnt_round=0,
            bool_card_exchanged=False,
            idx_player_started=random.randint(0, 3),  # Randomly select start player
            idx_player_active=0,
            list_player=[
                PlayerState(name="Blue", list_card=[], list_marble=blue_marbles, teamMate = "Green"),
                PlayerState(name="Green", list_card=[], list_marble=green_marbles, teamMate = "Blue"),
                PlayerState(name="Red", list_card=[], list_marble=red_marbles, teamMate = "Yellow"),
                PlayerState(name="Yellow", list_card=[], list_marble=yellow_marbles, teamMate= "Red"),
            ],
            list_card_draw=shuffled_cards,
            list_card_discard=[],
            card_active=None
        )
        
    
         # Deal 6 cards to each player directly in the init
        num_cards_per_player = 6  # Example number of cards per player
        for player in self.state.list_player:
            player.list_card = [self.state.list_card_draw.pop() for _ in range(num_cards_per_player)]

        
        # Exchange card with teammate
        if self.state.bool_card_exchanged:
            for player in self.state.list_player:
                for teammate in self.state.list_player:
                    if teammate.name == player.teamMate and player.name < teammate.name: 
                        card_to_exchange = random.choice(player.list_card)
                        player.list_card.remove(card_to_exchange)
                        card_from_teammate = random.choice(teammate.list_card)
                        teammate.list_card.remove(card_from_teammate)
                        teammate.list_card.append(card_to_exchange)
                        player.list_card.append(card_from_teammate)
            self.state.bool_card_exchanged = False

        # Transition to the running phase, since we're starting the game directly
        self.state.phase = GamePhase.RUNNING
        self.state.cnt_round = 1
        self.state.idx_player_active = self.state.idx_player_started
        self.state.bool_card_exchanged = True
    
    def reshuffle_if_empty(self):
        """ Reshuffle the discard pile into the draw pile when empty """
        if not self.state.list_card_draw:  # Check if the draw pile is empty
            if self.state.list_card_discard:  # Check if there are discarded cards
                # Move discarded cards to the draw pile
                self.state.list_card_draw.extend(self.state.list_card_discard)
                self.state.list_card_discard.clear()  # Clear the discard pile
                random.shuffle(self.state.list_card_draw)  # Shuffle the draw pile
            else:
                # No cards in either pile; raise an error
                raise ValueError("Both draw and discard piles are empty! Game cannot continue.")

    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        self.state = state

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        return self.state

    def print_state(self) -> None:
        """ Print the current game state """
        
        print("\n=== Brandi Dog Game State ===")
        print(f"Phase: {self.state.phase}")
        print(f"Round: {self.state.cnt_round}")
        print(f"Player to Start: {self.state.list_player[self.state.idx_player_started].name}")
        print(f"Active Player: {self.state.list_player[self.state.idx_player_active].name}")
        print(f"Cards Left in Draw Pile: {len(self.state.list_card_draw)}")
        print(f"Cards in Discard Pile: {len(self.state.list_card_discard)}")
        print("\n--- Players ---")
        for player in self.state.list_player:
            print(f"Player: {player.name}")
            print(f"  Marbles: {', '.join([f'Pos {m.pos} (Saved: {m.is_save})' for m in player.list_marble])}")
            print(f"  Cards in Hand: {len(player.list_card)}")
        print("\n--- Active Card ---")
        if self.state.card_active:
            print(f"Active Card: {self.state.card_active.suit}{self.state.card_active.rank}")
        else:
            print("No Active Card")
        print("\n============================\n")

    def get_list_action(self) -> List[Action]:
        """ Get a list of possible actions for the active player """
        list_action = []
        player = self.state.list_player[self.state.idx_player_active]

        # Check if Player can move forward (NO SPECIAL CARDS HERE)
        for card in player.list_card:
            if card.rank in ['2', '3', '4', '5', '6', '8', '9', '10', 'Q']:
                for marble in player.list_marble:
                    if int(marble.pos) >= 0 and int(marble.pos) <= 63:    # for now only marbles on board are checked
                        pos_from = marble.pos
                        steps = self.get_card_steps(card)
                        pos_to = (pos_from + steps)

                        if self.is_valid_move(pos_from, pos_to):
                            action = Action(card=card, pos_from=pos_from, pos_to=pos_to)
                            list_action.append(action)

        return list_action

    def apply_action(self, action: Optional[Action]) -> None:
        """ Apply the given action to the game """

        if action is None:
            self.reshuffle_if_empty()
            return

        player = self.state.list_player[self.state.idx_player_active]
        
        # check if any marbles should be moved
        marble_to_move = None
        for marble in player.list_marble:
            if marble.pos == action.pos_from:
                marble_to_move = marble
                break

        # if there are marbles to be moved, then move them and discard the card of the player afterwards
        if not marble_to_move is None:
            marble_to_move.pos = action.pos_to
            player.list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)
        
    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        return self.state


class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == '__main__':
    game = Dog()
    game.print_state()
    actions = game.get_list_action()
    print(actions)
    start_game_action = next((a for a in actions if a.action_type == ActionType.GAME_START), None)
    if start_game_action:
        game.apply_action(start_game_action)
    game.print_state()