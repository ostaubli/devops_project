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

        # Define start cards that allow moving out of kennel
        start_cards = ['A', 'K', 'JKR']

        # Check if any marble is in the kennel
        has_marble_in_kennel = any(marble.pos == 64 for marble in active_player.list_marble)
        if not has_marble_in_kennel:
            return []

        # Generate actions for valid start cards
        for card in active_player.list_card:
            if card.rank in start_cards:
                actions.append(Action(
                    card=card,
                    pos_from=64,  # From kennel
                    pos_to=0,     # To start position
                    card_swap=None
                ))

        return actions



    def apply_action(self, action: Action) -> None:
        active_player = self.state.list_player[self.state.idx_player_active]

        if action is None:
            # Move to the next player
            self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player

            # Check if we've gone through all players
            if self.state.idx_player_active == self.state.idx_player_started:
                # Move to the next round
                self.state.cnt_round += 1
                self.state.idx_player_started = (self.state.idx_player_started + 1) % self.state.cnt_player
                self.state.bool_card_exchanged = False

                # Determine the number of cards to deal based on the current round
                if 1 <= self.state.cnt_round <= 5:
                    cards_per_player = 7 - self.state.cnt_round  # 6, 5, 4, 3, 2
                elif self.state.cnt_round == 6:
                    cards_per_player = 6  # Reset to 6
                else:
                    # Handle rounds beyond 6 if the game cycles
                    cards_per_player = 7 - ((self.state.cnt_round - 1) % 5 + 1)
                    cards_per_player = max(cards_per_player, 2)

                # Deal new cards based on the determined number
                draw_pile = self.state.list_card_draw
                for player in self.state.list_player:
                    player.list_card = draw_pile[:cards_per_player]
                    draw_pile = draw_pile[cards_per_player:]
                self.state.list_card_draw = draw_pile

                # Set active player to the player after the starting player
                self.state.idx_player_active = (self.state.idx_player_started + 1) % self.state.cnt_player
            return

        # Validate the action: check if moving out of kennel is valid
        if action.pos_from == 64:  # 64 is the kennel position
            marble_to_move = next((m for m in active_player.list_marble if m.pos == action.pos_from), None)
            if marble_to_move is None:
                raise ValueError("No marble in the kennel to move")

        # Update the marble's position
        for marble in active_player.list_marble:
            if marble.pos == action.pos_from:
                marble.pos = action.pos_to
                break



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
