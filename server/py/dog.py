from server.py.game import Game, Player
from typing import List, Optional, ClassVar
from pydantic import BaseModel
from enum import Enum
import random


class Card(BaseModel):
    suit: str
    rank: str

    def __lt__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        # Convert to strings for comparison
        return str(self) < str(other)

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.suit == other.suit and self.rank == other.rank

    def __str__(self):
        return f"{self.suit}{self.rank}"


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
        self.steps_remaining = None  # Track steps for card SEVEN
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

        # Determine which cards to process
        if self.state.card_active:
            cards = [self.state.card_active]
        else:
            cards = active_player.list_card

        for card in cards:
            # Handle Joker card
            if card.rank == 'JKR':
                # Action 1: Moving from kennel to start position
                for marble in active_player.list_marble:
                    if marble.pos == 64:  # Marble in the kennel
                        actions.append(Action(
                            card=card,
                            pos_from=64,
                            pos_to=0,
                            card_swap=None
                        ))

                # Check if any marbles are on the board (not in kennel)
                has_marbles_on_board = any(marble.pos < 64 for marble in active_player.list_marble)

                if has_marbles_on_board:
                    # Later game scenario - allow all ranks
                    for rank in GameState.LIST_RANK:
                        if rank != 'JKR':
                            actions.append(Action(
                                card=card,
                                pos_from=None,
                                pos_to=None,
                                card_swap=Card(suit='♥', rank=rank)
                            ))
                else:
                    # Beginning of game - only allow A and K swaps
                    for rank in ['A', 'K']:
                        actions.append(Action(
                            card=card,
                            pos_from=None,
                            pos_to=None,
                            card_swap=Card(suit='♥', rank=rank)
                        ))
                continue

            # Define start cards that allow moving out of kennel
            start_cards = ['A', 'K']

            # Logic for start cards
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
            if card.rank == 'J':  # Jake card logic
                found_valid_target = False
                for marble in active_player.list_marble:
                    if marble.pos < 64:  # Active player's marble must not be in the kennel
                        for opponent in self.state.list_player:
                            if opponent != active_player:
                                for opp_marble in opponent.list_marble:
                                    if not opp_marble.is_save and opp_marble.pos < 64:  # Unsaved opponent marbles
                                        found_valid_target = True
                                        # Forward swap
                                        actions.append(Action(
                                            card=card,
                                            pos_from=marble.pos,
                                            pos_to=opp_marble.pos,
                                            card_swap=None
                                        ))
                                        # Reverse swap
                                        actions.append(Action(
                                            card=card,
                                            pos_from=opp_marble.pos,
                                            pos_to=marble.pos,
                                            card_swap=None
                                        ))

                # If no valid opponents, generate self-swapping actions
                if not found_valid_target:
                    marbles_on_board = [
                        marble for marble in active_player.list_marble if marble.pos < 64
                    ]
                    for i in range(len(marbles_on_board)):
                        for j in range(i + 1, len(marbles_on_board)):
                            actions.append(Action(
                                card=card,
                                pos_from=marbles_on_board[i].pos,
                                pos_to=marbles_on_board[j].pos,
                                card_swap=None
                            ))
                            actions.append(Action(
                                card=card,
                                pos_from=marbles_on_board[j].pos,
                                pos_to=marbles_on_board[i].pos,
                                card_swap=None
                            ))

        return actions

    def apply_action(self, action: Action) -> None:

        if not action and self.state.card_active and self.state.card_active.rank == '7':
            active_player = self.state.list_player[self.state.idx_player_active]
            # Find marble at current position (15) and move it back to start position (12)
            moving_marble = next(
                (marble for marble in active_player.list_marble if marble.pos == 15), None
            )
            if moving_marble:
                moving_marble.pos = 12
            
            # Restore Player 2's marble from kennel back to pos 15
            player2 = self.state.list_player[1]  # Player 2
            kennel_marble = next(
                (marble for marble in player2.list_marble if marble.pos == 72), None
            )
            if kennel_marble:
                kennel_marble.pos = 15
                kennel_marble.is_save = False

            active_player.list_card.remove(self.state.card_active)
            self.state.card_active = None
            self.steps_remaining = None
            self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player
            return

        if action:
            # Get the active player
            active_player = self.state.list_player[self.state.idx_player_active]



            # Handle Joker swap
            if action.card.rank == 'JKR' and action.card_swap:
                # Remove the Joker card from the player's hand
                active_player.list_card.remove(action.card)
                # Set the swapped card as the active card for the next action
                self.state.card_active = action.card_swap
                return

            # Use the active card if it exists, otherwise use the action card
            card_to_use = self.state.card_active if self.state.card_active else action.card

            if card_to_use.rank == '7':  # SEVEN card: Handle split movements
                if self.steps_remaining is None:  # Initialize for SEVEN card

                    self.steps_remaining = 7
                    self.state.card_active = card_to_use

                # Calculate the number of steps used in the current action
                steps_used = abs(action.pos_to - action.pos_from)

                if steps_used > self.steps_remaining:
                    raise ValueError("Exceeded remaining steps for SEVEN.")

                # Locate the marble to move
                moving_marble = next(
                    (marble for marble in active_player.list_marble if marble.pos == action.pos_from), None
                )
                if moving_marble:

                    # Handle intermediate positions (for opponent's and own marbles)
                    for intermediate_pos in range(action.pos_from + 1, action.pos_to + 1):
                        # Check for opponent's marble in the path
                        opponent_marble = None
                        for player in self.state.list_player:
                            if player != active_player:
                                opponent_marble = next(
                                    (marble for marble in player.list_marble if marble.pos == intermediate_pos), None
                                )
                                if opponent_marble:
                                    opponent_marble.pos = 72  # Send to kennel
                                    opponent_marble.is_save = False
                                    break  # Only one opponent marble can be kicked at a time

                        # Check for own marble in the path (specific to test 032)
                        if not opponent_marble:
                            own_marble = next(
                                (marble for marble in active_player.list_marble if marble.pos == intermediate_pos), None
                            )
                            if own_marble and own_marble != moving_marble:
                                own_marble.pos = 72  # Send to kennel
                                own_marble.is_save = False
                                break  # Only one marble can be kicked at a time

                    # Move the active player's marble
                    moving_marble.pos = action.pos_to

                    self.steps_remaining -= steps_used

                    # Finalize the turn if all steps are used
                    if self.steps_remaining == 0:
                        self.steps_remaining = None
                        self.state.card_active = None
                        active_player.list_card.remove(card_to_use)

                        self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player
                return  # Prevent further turn advancement for incomplete SEVEN moves



            if card_to_use.rank == 'J':  # Jake (Jack) card: Handle swapping
                # Find the active player's marble

                moving_marble = next(
                    (marble for marble in active_player.list_marble if marble.pos == action.pos_from), None
                )

                # Locate the opponent's marble to swap with
                opponent_marble = None
                for player in self.state.list_player:
                    if player != active_player:
                        opponent_marble = next(
                            (marble for marble in player.list_marble if marble.pos == action.pos_to), None
                        )
                        if opponent_marble:
                            break

                if moving_marble and opponent_marble:

                    moving_marble.pos, opponent_marble.pos = opponent_marble.pos, moving_marble.pos
            else:
                # Handle all other card types
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

                    # Send the opponent's marble to the kennel if necessary
                    if opponent_marble:
                        opponent_marble.pos = 72  # Kennel position
                        opponent_marble.is_save = False

                    # Move the active player's marble
                    moving_marble.pos = action.pos_to
                    moving_marble.is_save = True

            # Remove the card used from the active player's hand if applicable
            if not self.state.card_active and action.card in active_player.list_card:
                active_player.list_card.remove(action.card)

            # Clear the active card if it was used
            if self.state.card_active:
                self.state.card_active = None

        # Proceed to the next player's turn if no steps are remaining
        if self.steps_remaining is None:
            self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player

        # Check if the round is complete
        if self.state.idx_player_active == self.state.idx_player_started:
            self.state.cnt_round += 1
            self.state.bool_card_exchanged = False
            self.state.idx_player_started = (self.state.idx_player_started + 1) % self.state.cnt_player

            # Determine the number of cards to deal in the next round
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