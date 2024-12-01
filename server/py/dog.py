# runcmd: cd ../.. & venv\Scripts\python server/py/dog_template.py
from server.py.game import Game, Player
from typing import List, Optional, ClassVar
from pydantic import BaseModel
from enum import Enum
import random


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


class Dog(Game):

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """
        self.state = GameState(
            cnt_player=4,
            phase=GamePhase.SETUP,
            cnt_round=0,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=[
                PlayerState(name=f"Player {i + 1}", list_card=[],
                            list_marble=[Marble(pos=-1, is_save=False) for _ in range(4)])
                for i in range(4)
            ],
            list_card_draw=random.sample(GameState.LIST_CARD, len(GameState.LIST_CARD)),
            list_card_discard=[],
            card_active=None,
        )

    def send_home(self, pos: int) -> None:
        """Send the marble at the given position back to the kennel, if not in finish area."""
        for i, player in enumerate(self.state.list_player):
            for marble in player.list_marble:
                if marble.pos == pos:
                    # Check if the marble is in the finish area
                    if self.is_in_finish_area(marble, i):
                        print(f"{player.name}'s marble at position {pos} is in the finish and cannot be sent home.")
                        return

                    # Send marble back to the kennel
                    marble.pos = -1  # Reset marble position to kennel
                    marble.is_save = False
                    print(f"{player.name}'s marble at position {pos} sent back to the kennel.")
                    return  # Only one marble occupies a position, so stop after handling
        print(f"No marble found at position {pos} to send home.")

    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        self.state = state

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        return self.state

    def print_state(self) -> None:
        """ Print the current game state """
        print(f"Round: {self.state.cnt_round}, Phase: {self.state.phase}")
        for idx, player in enumerate(self.state.list_player):
            print(f"{player.name}: Cards: {player.list_card}, Marbles: {player.list_marble}")

    def deal_cards(self) -> None:
        """ Deal cards to all players. """
        for player in self.state.list_player:
            player.list_card = self.state.list_card_draw[:6]
            self.state.list_card_draw = self.state.list_card_draw[6:]

    def get_list_action(self) -> List[Action]:
        """ Get a list of possible actions for the active player """
        actions = []
        player = self.state.list_player[self.state.idx_player_active]

        # Check possible card plays based on player cards and current game state
        for card in player.list_card:
            if card.rank == 'JKR':  # Joker can be played as any card
                actions.append(Action(card=card, pos_from=None, pos_to=None, card_swap=None))
            elif card.rank == '7':  # For card 7, players can choose to move multiple marbles
                for marble in player.list_marble:
                    if marble.is_save:
                        actions.append(Action(card=card, pos_from=marble.pos, pos_to=None, card_swap=None))
            else:  # For other cards, move marbles or perform other actions
                for marble in player.list_marble:
                    if marble.is_save:
                        actions.append(Action(card=card, pos_from=marble.pos, pos_to=marble.pos + int(card.rank), card_swap=None))
                    else:
                        actions.append(Action(card=card, pos_from=None, pos_to=None, card_swap=None))

        return actions

    def apply_action(self, action: Action) -> None:
        """ Apply the given action to the game """
        player = self.state.list_player[self.state.idx_player_active]

        if action.card.rank == 'JKR':  # Joker: use as any card
            # Action can be anything based on the game rules, e.g., swap a card or move a marble
            pass
        elif action.card.rank == '7':  # Special behavior for card '7'
            for marble in player.list_marble:
                if marble.pos == action.pos_from and marble.is_save:
                    marble.pos = action.pos_to
                    marble.is_save = False
        else:  # Regular behavior for moving marbles based on card rank
            for marble in player.list_marble:
                if marble.pos == action.pos_from and marble.is_save:
                    marble.pos = action.pos_to
                    marble.is_save = False

        # Update the cards: if it's a move action, discard the played card
        player.list_card.remove(action.card)
        self.state.list_card_discard.append(action.card)

        # Proceed to the next player after applying the action
        self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player
        self.state.cnt_round += 1

    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the opponent's cards are face down) """
        # Mask the opponent's cards, only showing the player's own cards
        masked_state = self.state.model_copy()
        for i, player in enumerate(masked_state.list_player):
            if i != idx_player:
                player.list_card = []  # Hide the cards of other players
        return masked_state


class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        return random.choice(actions) if actions else None


if __name__ == '__main__':
    # Initialize game and players
    game = Dog()
    players = [RandomPlayer() for i in range(4)]

    # Game setup
    game.deal_cards()
    game.print_state()

    # Main game loop
    while game.state.phase != GamePhase.FINISHED:
        actions = game.get_list_action()
        active_player = players[game.state.idx_player_active]
        selected_action = active_player.select_action(game.get_player_view(game.state.idx_player_active), actions)
        if selected_action:
            game.apply_action(selected_action)
        game.print_state()

        # End condition (example: after 10 rounds)
        if game.state.cnt_round > 10:
            game.state.phase = GamePhase.FINISHED

    print("Game Over")
