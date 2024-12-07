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

        # Logic for start cards
        for card in cards:
            if card.rank in start_cards:
                for marble in active_player.list_marble:
                    if marble.pos == 64:  # Marble in the kennel
                        actions.append(Action(
                            card=card,
                            pos_from=64,
                            pos_to=0,
                            card_swap=None
                        ))

        # Logic for "Jake" (J) cards: Swapping actions
        for card in cards:
            if card.rank == 'J':  # Jake card logic
                for marble in active_player.list_marble:
                    if marble.pos < 64:  # Active player's marble must not be in the kennel
                        for opponent in self.state.list_player:
                            if opponent != active_player:
                                for opp_marble in opponent.list_marble:
                                    if not opp_marble.is_save:  # Only swap with unsaved opponent marbles
                                        actions.append(Action(
                                            card=card,
                                            pos_from=marble.pos,
                                            pos_to=opp_marble.pos,
                                            card_swap=None
                                        ))

        return actions

    def apply_action(self, action: Action) -> None:
        if action:
            # Get the active player
            active_player = self.state.list_player[self.state.idx_player_active]

            if action.card.rank == 'J':  # Jake (Jack) card: Handle swapping
                # Find the marbles to swap
                moving_marble = next(
                    (marble for marble in active_player.list_marble if marble.pos == action.pos_from), None
                )
                opponent_marble = None
                for player in self.state.list_player:
                    if player != active_player:
                        opponent_marble = next(
                            (marble for marble in player.list_marble if marble.pos == action.pos_to), None
                        )
                        if opponent_marble:
                            break

                if moving_marble and opponent_marble:
                    # Swap positions
                    moving_marble.pos, opponent_marble.pos = opponent_marble.pos, moving_marble.pos

            else:
                # Existing logic for handling other card types
                moving_marble = next(
                    (marble for marble in active_player.list_marble if marble.pos == action.pos_from), None
                )
                if moving_marble:
                    # Check if the target position has an opponent's marble
                    opponent_marble = None
                    for player in self.state.list_player:
                        if player != active_player:
                            for marble in player.list_marble:
                                if marble.pos == action.pos_to:
                                    opponent_marble = marble
                                    break

                    # Handle displacement of opponent's marble
                    if opponent_marble:
                        opponent_marble.pos = 72  # Move opponent's marble back to kennel
                        opponent_marble.is_save = False

                    # Move the active player's marble
                    moving_marble.pos = action.pos_to
                    moving_marble.is_save = True

            # Remove the card used from the active player's hand
            if action.card in active_player.list_card:
                active_player.list_card.remove(action.card)

        # Proceed to the next player's turn
        self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player

        # Existing logic for end-of-round handling
        if self.state.idx_player_active == self.state.idx_player_started:
            self.state.cnt_round += 1
            self.state.bool_card_exchanged = False
            self.state.idx_player_started = (self.state.idx_player_started + 1) % self.state.cnt_player

            # Determine number of cards to deal
            if 1 <= self.state.cnt_round <= 5:
                cards_per_player = 7 - self.state.cnt_round  # 6, 5, 4, 3, 2 cards
            elif self.state.cnt_round == 6:
                cards_per_player = 6  # Reset to 6 cards
            else:
                cards_per_player = max(7 - ((self.state.cnt_round - 1) % 5 + 1), 2)

            # Deal cards to players
            draw_pile = self.state.list_card_draw
            for player in self.state.list_player:
                player.list_card = draw_pile[:cards_per_player]
                draw_pile = draw_pile[cards_per_player:]

            # Update the draw pile
            self.state.list_card_draw = draw_pile

    def get_player_view(self, idx_player: int) -> GameState:
        return self.state


class RandomPlayer(Player):
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        if len(actions) > 0:
            return random.choice(actions)
        return None
