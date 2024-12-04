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
                                          Card(suit='♠', rank='2'), Card(suit='♥', rank='2'), Card(suit='♦', rank='2'),
                                          Card(suit='♣', rank='2'),
                                          Card(suit='♠', rank='3'), Card(suit='♥', rank='3'), Card(suit='♦', rank='3'),
                                          Card(suit='♣', rank='3'),
                                          Card(suit='♠', rank='4'), Card(suit='♥', rank='4'), Card(suit='♦', rank='4'),
                                          Card(suit='♣', rank='4'),
                                          Card(suit='♠', rank='5'), Card(suit='♥', rank='5'), Card(suit='♦', rank='5'),
                                          Card(suit='♣', rank='5'),
                                          Card(suit='♠', rank='6'), Card(suit='♥', rank='6'), Card(suit='♦', rank='6'),
                                          Card(suit='♣', rank='6'),
                                          Card(suit='♠', rank='7'), Card(suit='♥', rank='7'), Card(suit='♦', rank='7'),
                                          Card(suit='♣', rank='7'),
                                          Card(suit='♠', rank='8'), Card(suit='♥', rank='8'), Card(suit='♦', rank='8'),
                                          Card(suit='♣', rank='8'),
                                          Card(suit='♠', rank='9'), Card(suit='♥', rank='9'), Card(suit='♦', rank='9'),
                                          Card(suit='♣', rank='9'),
                                          Card(suit='♠', rank='10'), Card(suit='♥', rank='10'),
                                          Card(suit='♦', rank='10'), Card(suit='♣', rank='10'),
                                          Card(suit='♠', rank='J'), Card(suit='♥', rank='J'), Card(suit='♦', rank='J'),
                                          Card(suit='♣', rank='J'),
                                          Card(suit='♠', rank='Q'), Card(suit='♥', rank='Q'), Card(suit='♦', rank='Q'),
                                          Card(suit='♣', rank='Q'),
                                          Card(suit='♠', rank='K'), Card(suit='♥', rank='K'), Card(suit='♦', rank='K'),
                                          Card(suit='♣', rank='K'),
                                          Card(suit='♠', rank='A'), Card(suit='♥', rank='A'), Card(suit='♦', rank='A'),
                                          Card(suit='♣', rank='A'),
                                          Card(suit='', rank='JKR'), Card(suit='', rank='JKR'),
                                          Card(suit='', rank='JKR')
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
        active_player = self.state.list_player[self.state.idx_player_active]
        cards = active_player.list_card

        # Iterate over each card in the player's hand
        for card in cards:
            if card.rank == 'A':
                # Check if any marble is at the start position (pos=0)
                for marble in active_player.list_marble:
                    if marble.pos == 0:
                        # Add actions for moving 1 or 11 steps
                        actions.append(Action(card=card, pos_from=0, pos_to=1))
                        actions.append(Action(card=card, pos_from=0, pos_to=11))

            # Add more logic for handling other card types if needed
            # Example for start cards like 'K' or 'JKR'
            elif card.rank in ['K', 'JKR']:
                for marble in active_player.list_marble:
                    if marble.pos == 64:  # Example: marble in the kennel
                        actions.append(Action(card=card, pos_from=64, pos_to=0))

        return actions

    def apply_action(self, action: Action) -> None:
        if action is None:
            # Skip turn
            self.state.idx_player_active = (self.state.idx_player_active + 1) % len(self.state.list_player)
            return

        active_player = self.state.list_player[self.state.idx_player_active]

        # Find the marble to move
        for marble in active_player.list_marble:
            if marble.pos == action.pos_from:
                # Process ACE-specific logic
                if action.card.rank == 'A' and action.pos_to in [1, 11]:
                    # Move the marble by the specified steps (1 or 11)
                    marble.pos = action.pos_to
                else:
                    # Default move logic for other cards
                    marble.pos = action.pos_to

                # Remove the card from the player's hand
                active_player.list_card.remove(action.card)

                # End turn
                self.state.idx_player_active = (self.state.idx_player_active + 1) % len(self.state.list_player)
                return

    def get_player_view(self, idx_player: int) -> GameState:
        return self.state


class RandomPlayer(Player):
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        if len(actions) > 0:
            return random.choice(actions)
        return None
