# Code that passed 29 and 30 but failed previously passed test 02,06, (47, 48 , 49)


# runcmd: cd ../.. & venv\Scripts\python server/py/dog_template.py
from server.py.game import Game, Player
from typing import List, Optional, ClassVar
from pydantic import BaseModel
from enum import Enum
import random


class Card(BaseModel):
    suit: str
    rank: str


class Marble(BaseModel):
    pos: int
    is_save: bool


class PlayerState(BaseModel):
    name: str
    list_card: List[Card]
    list_marble: List[Marble]


class Action(BaseModel):
    card: Card
    pos_from: Optional[int]
    pos_to: Optional[int]
    card_swap: Optional[Card] = None


class GamePhase(str, Enum):
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'


class GameState(BaseModel):
    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10',
        'J', 'Q', 'K', 'A', 'JKR'
    ]
    LIST_CARD: ClassVar[List[Card]] = [
        Card(suit='♠', rank='2'), Card(suit='♥', rank='2'), Card(suit='♦', rank='2'), Card(suit='♣', rank='2'),
        Card(suit='♠', rank='3'), Card(suit='♥', rank='3'), Card(suit='♦', rank='3'), Card(suit='♣', rank='3'),
        Card(suit='♠', rank='4'), Card(suit='♥', rank='4'), Card(suit='♦', rank='4'), Card(suit='♣', rank='4'),
        Card(suit='♠', rank='5'), Card(suit='♥', rank='5'), Card(suit='♦', rank='5'), Card(suit='♣', rank='5'),
        Card(suit='♠', rank='6'), Card(suit='♥', rank='6'), Card(suit='♦', rank='6'), Card(suit='♣', rank='6'),
        Card(suit='♠', rank='7'), Card(suit='♥', rank='7'), Card(suit='♦', rank='7'), Card(suit='♣', rank='7'),
        Card(suit='♠', rank='8'), Card(suit='♥', rank='8'), Card(suit='♦', rank='8'), Card(suit='♣', rank='8'),
        Card(suit='♠', rank='9'), Card(suit='♥', rank='9'), Card(suit='♦', rank='9'), Card(suit='♣', rank='9'),
        Card(suit='♠', rank='10'), Card(suit='♥', rank='10'), Card(suit='♦', rank='10'), Card(suit='♣', rank='10'),
        Card(suit='♠', rank='J'), Card(suit='♥', rank='J'), Card(suit='♦', rank='J'), Card(suit='♣', rank='J'),
        Card(suit='♠', rank='Q'), Card(suit='♥', rank='Q'), Card(suit='♦', rank='Q'), Card(suit='♣', rank='Q'),
        Card(suit='♠', rank='K'), Card(suit='♥', rank='K'), Card(suit='♦', rank='K'), Card(suit='♣', rank='K'),
        Card(suit='♠', rank='A'), Card(suit='♥', rank='A'), Card(suit='♦', rank='A'), Card(suit='♣', rank='A'),
        Card(suit='', rank='JKR'), Card(suit='', rank='JKR'), Card(suit='', rank='JKR')
    ] * 2

    cnt_player: int = 4
    phase: GamePhase
    cnt_round: int
    bool_card_exchanged: bool
    idx_player_started: int
    idx_player_active: int
    list_player: List[PlayerState]
    list_card_draw: List[Card]
    list_card_discard: List[Card]
    card_active: Optional[Card]

    steps_remaining: Optional[int] = None


class Dog(Game):
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        draw_pile = list(GameState.LIST_CARD)
        random.shuffle(draw_pile)

        players = []
        for i in range(4):
            marbles = []
            for j in range(4):
                marbles.append(Marble(pos=64 + i * 8 + j, is_save=False))

            player_cards = draw_pile[:6]
            draw_pile = draw_pile[6:]

            players.append(PlayerState(
                name=f"Player {i + 1}",
                list_card=player_cards,
                list_marble=marbles
            ))

        self.state = GameState(
            phase=GamePhase.RUNNING,
            cnt_round=1,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=players,
            list_card_draw=draw_pile,
            list_card_discard=[],
            card_active=None
        )

    def set_state(self, state: GameState) -> None:
        self.state = state

    def get_state(self) -> GameState:
        return self.state

    def print_state(self) -> None:
        pass

    def get_list_action(self) -> List[Action]:
        actions = []
        # Get cards of active player
        active_player = self.state.list_player[self.state.idx_player_active]
        cards = active_player.list_card

        # Define start cards that allow moving out of kennel
        start_cards = ['A', 'K', 'JKR']

        # Check if any card allows moving out of kennel
        for card in cards:
            if card.rank in start_cards:
                # Check if marbe in the kennel (pos=64)
                for marble in active_player.list_marble:
                    if marble.pos == 64:
                        opponent_marble = None
                        for opponent in self.state.list_player:
                            if opponent != active_player:
                                for opp_marble in opponent.list_marble:
                                    if marble.pos == 0 and opponent_marble.is_save:  # Opponent marble on start
                                        opponent_marble = opp_marble
                                        break
                        actions.append(Action(
                            card=card,
                            pos_from=64,
                            pos_to=0,
                            card_swap=None
                        ))
        return actions

    def apply_action(self, action: Action) -> None:
        if action:
            active_player = self.state.list_player[self.state.idx_player_active]
            moving_marble = next(
                (marble for marble in active_player.list_marble if marble.pos == action.pos_from), None
            )

            if moving_marble:
                if action.card.rank == '7':  # SEVEN logic
                    if self.state.steps_remaining is None:  # Initialize SEVEN
                        self.state.steps_remaining = 7
                        self.state.card_active = action.card

                    steps_used = abs(action.pos_to - action.pos_from)
                    if steps_used > self.state.steps_remaining:
                        raise ValueError("Exceeded remaining steps for SEVEN.")

                    self.state.steps_remaining -= steps_used
                    moving_marble.pos = action.pos_to

                    if self.state.steps_remaining == 0:  # SEVEN move complete
                        self.state.steps_remaining = None
                        self.state.card_active = None
                        self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player
                else:
                    # Regular card logic
                    moving_marble.pos = action.pos_to
                    self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player

                # Handle opponent marble collision
                opponent_marble = None
                opponent_player = None
                for player in self.state.list_player:
                    if player != active_player:
                        for marble in player.list_marble:
                            if marble.pos == action.pos_to:  # Check for collision
                                opponent_marble = marble
                                opponent_player = player
                                break

                if opponent_marble:
                    # Send the opponent's marble back to the kennel
                    opponent_marble.pos = 64 + self.state.list_player.index(opponent_player) * 8  # Adjust to kennel position
                    opponent_marble.is_save = False


                # Remove the card used
                if action.card in active_player.list_card:
                    active_player.list_card.remove(action.card)

            # Check if round is complete
            if self.state.idx_player_active == self.state.idx_player_started:
                self.state.cnt_round += 1


    def get_player_view(self, idx_player: int) -> GameState:
        return self.state


class RandomPlayer(Player):
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        if len(actions) > 0:
            return random.choice(actions)
        return None
