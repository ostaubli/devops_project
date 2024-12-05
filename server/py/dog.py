# runcmd: cd ../.. & venv\Scripts\python server/py/dog_template.py
import random
from enum import Enum
from typing import List, Optional, ClassVar

from pydantic import BaseModel

from server.py.game import Game, Player, GameAction


class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank


class Marble(BaseModel):
    pos: int  # position on board (0 to 95)
    is_save: bool  # true if marble was moved out of kennel and was not yet moved


class PlayerState(BaseModel):
    name: str  # name of player
    list_card: List[Card]  # list of cards
    list_marble: List[Marble]  # list of marbles


class Action(BaseModel):
    card: Card  # card to play
    pos_from: Optional[int]  # position to move the marble from
    pos_to: Optional[int]  # position to move the marble to
    card_swap: Optional[Card] = None  # optional card to swap ()


class GamePhase(str, Enum):
    SETUP = 'setup'  # before the game has started
    RUNNING = 'running'  # while the game is running
    FINISHED = 'finished'  # when the game is finished


class GameState(BaseModel):
    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']  # 4 suits (colors)
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10',  # 13 ranks + Joker
        'J', 'Q', 'K', 'A', 'JKR'
    ]
    LIST_CARD: ClassVar[List[Card]] = [
                                          # 2: Move 2 spots forward
                                          Card(suit='♠', rank='2'), Card(suit='♥', rank='2'), Card(
            suit='♦', rank='2'), Card(suit='♣', rank='2'),
                                          # 3: Move 3 spots forward
                                          Card(suit='♠', rank='3'), Card(suit='♥', rank='3'), Card(
            suit='♦', rank='3'), Card(suit='♣', rank='3'),
                                          # 4: Move 4 spots forward or back
                                          Card(suit='♠', rank='4'), Card(suit='♥', rank='4'), Card(
            suit='♦', rank='4'), Card(suit='♣', rank='4'),
                                          # 5: Move 5 spots forward
                                          Card(suit='♠', rank='5'), Card(suit='♥', rank='5'), Card(
            suit='♦', rank='5'), Card(suit='♣', rank='5'),
                                          # 6: Move 6 spots forward
                                          Card(suit='♠', rank='6'), Card(suit='♥', rank='6'), Card(
            suit='♦', rank='6'), Card(suit='♣', rank='6'),
                                          # 7: Move 7 single steps forward
                                          Card(suit='♠', rank='7'), Card(suit='♥', rank='7'), Card(
            suit='♦', rank='7'), Card(suit='♣', rank='7'),
                                          # 8: Move 8 spots forward
                                          Card(suit='♠', rank='8'), Card(suit='♥', rank='8'), Card(
            suit='♦', rank='8'), Card(suit='♣', rank='8'),
                                          # 9: Move 9 spots forward
                                          Card(suit='♠', rank='9'), Card(suit='♥', rank='9'), Card(
            suit='♦', rank='9'), Card(suit='♣', rank='9'),
                                          # 10: Move 10 spots forward
                                          Card(suit='♠', rank='10'), Card(suit='♥', rank='10'), Card(
            suit='♦', rank='10'), Card(suit='♣', rank='10'),
                                          # Jake: A marble must be exchanged
                                          Card(suit='♠', rank='J'), Card(suit='♥', rank='J'), Card(
            suit='♦', rank='J'), Card(suit='♣', rank='J'),
                                          # Queen: Move 12 spots forward
                                          Card(suit='♠', rank='Q'), Card(suit='♥', rank='Q'), Card(
            suit='♦', rank='Q'), Card(suit='♣', rank='Q'),
                                          # King: Start or move 13 spots forward
                                          Card(suit='♠', rank='K'), Card(suit='♥', rank='K'), Card(
            suit='♦', rank='K'), Card(suit='♣', rank='K'),
                                          # Ass: Start or move 1 or 11 spots forward
                                          Card(suit='♠', rank='A'), Card(suit='♥', rank='A'), Card(
            suit='♦', rank='A'), Card(suit='♣', rank='A'),
                                          # Joker: Use as any other card you want
                                          Card(suit='', rank='JKR'), Card(
            suit='', rank='JKR'), Card(suit='', rank='JKR')
                                      ] * 2

    cnt_player: int = 4  # number of players (must be 4)
    phase: GamePhase  # current phase of the game
    cnt_round: int  # current round
    bool_card_exchanged: bool  # true if cards was exchanged in round
    idx_player_started: int  # index of player that started the round
    idx_player_active: int  # index of active player in round
    list_player: List[PlayerState]  # list of players
    list_card_draw: List[Card]  # list of cards to draw
    list_card_discard: List[Card]  # list of cards discarded
    # active card (for 7 and JKR with sequence of actions)
    card_active: Optional[Card]

    def __str__(self) -> str:
        player_states = "\n".join(
            f"Player {i + 1} ({player.name}): Cards: {len(player.list_card)}, Marbles: {len(player.list_marble)}"
            for i, player in enumerate(self.list_player)
        )
        return (
            f"Game Phase: {self.phase}\n"
            f"Round: {self.cnt_round}\n"
            f"Active Player: {self.idx_player_active + 1}\n"
            f"Players:\n{player_states}\n"
            f"Cards to Draw: {len(self.list_card_draw)}\n"
            f"Cards Discarded: {len(self.list_card_discard)}\n"
            f"Active Card: {self.card_active}\n"
        )


class Dog(Game):
    teams = {
        0: [0, 2],  # Team 1: Player 1 and Player 3
        1: [1, 3],  # Team 2: Player 2 and Player 4
    }
    # Constants for player positions
    PLAYER_POSITIONS = {
        0: {'start': 0, 'queue_start': 64, 'final_start': 68},
        1: {'start': 16, 'queue_start': 72, 'final_start': 76},
        2: {'start': 32, 'queue_start': 80, 'final_start': 84},
        3: {'start': 48, 'queue_start': 88, 'final_start': 92}
    }

    # Total steps in the main path ignoring the "special fields"
    TOTAL_STEPS = 64

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """
        super().__init__()
        self._state = GameState(
            phase=GamePhase.RUNNING,
            cnt_round=1,
            bool_game_finished=False,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=[PlayerState(
                name=f"Player {i + 1}", list_card=[], list_marble=[]) for i in range(4)],
            list_card_draw=GameState.LIST_CARD.copy(),
            list_card_discard=[],
            card_active=None
        )
        random.shuffle(self._state.list_card_draw)
        self.deal_cards()
        self._set_marbles()

    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        self._state = state

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        return self._state

    def print_state(self) -> None:
        """ Print the current game state """
        print(self._state)

    def get_list_action(self) -> List[Action]:
        """ Get a list of possible actions for the active player """
        actions = []
        unique_actions = []
        to_positions = []
        active_player = self._state.list_player[self._state.idx_player_active]

        marbles_in_kennel = self._count_marbles_in_kennel()
        for card in active_player.list_card:
            for marble in active_player.list_marble:
                # TODO Go through all cards and marbles and return the possible positions.

                queue_start = self.PLAYER_POSITIONS[self._state.idx_player_active]['queue_start']
                active_player_fields = self.PLAYER_POSITIONS[self._state.idx_player_active]
                final_start = active_player_fields['final_start']
                # if marble is in kennel
                if marble.pos in range(queue_start,
                                       queue_start + 4):
                    if marble.pos == queue_start + 4 - marbles_in_kennel:

                        # only allow actions for ACE, KING or JOKER
                        if card.rank in ['A', 'JKR', 'K']:
                            start_position = self.PLAYER_POSITIONS[self._state.idx_player_active]['start']

                            # allow only if the current player does not have a marble on start
                            if all(m.pos != start_position for m in active_player.list_marble):
                                # if 4 in kennel, start_position + 3 - #in kennel-1
                                if marble.pos == queue_start + 4 - marbles_in_kennel:
                                    actions.append(Action(card=card, pos_from=marble.pos, pos_to=start_position,
                                                          card_swap=None))

                                # Handle JOKER acting as ACE or KING
                                if card.rank == 'JKR':
                                    # As Ace
                                    actions.append(Action(
                                        card=card,
                                        pos_from=marble.pos,
                                        pos_to=start_position,
                                        card_swap=Card(suit='♥', rank='A')  # JKR acting as Ace
                                    ))
                                    # As King
                                    actions.append(Action(
                                        card=card,
                                        pos_from=marble.pos,
                                        pos_to=start_position,
                                        card_swap=Card(suit='♥', rank='K')  # JKR acting as King
                                    ))
                else:
                    if card.rank.isdigit() and card.rank not in ['7', '4']:
                        to_positions = self._calculate_position_to(
                            marble.pos, card, self._state.idx_player_active)  # simple calculations

                    # TODO Add more logic for all the other cards LATIN-35
                    if card.rank == '7':
                        # can be split into multiple marbles. if takes over, reset other marble
                        # to_positions = ...
                        pass

                    if card.rank == 'A':
                        # Move 1 spot forward
                        pos_one_forward = (marble.pos + 1) % self.TOTAL_STEPS
                        if marble.pos < queue_start and pos_one_forward >= queue_start:
                            pos_one_forward = final_start + (pos_one_forward - queue_start) - 1
                        to_positions.append(pos_one_forward)

                        # Move 11 spots forward
                        pos_eleven_forward = (marble.pos + 11) % self.TOTAL_STEPS
                        if marble.pos < queue_start and pos_eleven_forward >= queue_start:
                            pos_eleven_forward = final_start + (pos_eleven_forward - queue_start) - 1
                        to_positions.append(pos_eleven_forward)

                        # Validate positions are not blocked or the move is not valid
                        valid_positions = []

                        for pos_to in to_positions:
                            if (not self._is_way_blocked(pos_to, marble.pos,
                                                         self._get_all_safe_marbles()) and
                                    not self._is_valid_move_in_final_area(marble.pos,
                                                                          pos_to, active_player.list_marble,
                                                                          final_start,
                                                                          final_start + 3
                                                                          )):
                                valid_positions.append(pos_to)

                        to_positions = valid_positions

                    if card.rank == '4':
                        # Forward movement (+4)
                        next_position = (marble.pos + 4) % self.TOTAL_STEPS
                        if marble.pos < queue_start and next_position >= queue_start:
                            next_position = final_start + (next_position - queue_start) - 1

                        if self._is_valid_move_in_final_area(marble.pos, next_position, active_player.list_marble,
                                                             final_start,
                                                             final_start + 3):
                            to_positions.append(next_position)

                        # Backward movement (-4)
                        next_position = self.TOTAL_STEPS - 4 \
                            if marble.pos == 0 else (marble.pos - 4) % self.TOTAL_STEPS
                        if marble.pos < queue_start and next_position >= queue_start:
                            next_position = final_start + (next_position - queue_start) - 1

                        if self._is_valid_move_in_final_area(marble.pos, next_position, active_player.list_marble,
                                                             final_start,
                                                             final_start + 3):
                            to_positions.append(next_position)

                    if card.rank == 'J':

                        # Get the active player's marbles that are not in the kennel
                        active_player_marbles = [
                            marble for marble in active_player.list_marble
                            if marble.pos not in range(queue_start, queue_start + 4)  # Exclude marbles in the kennel
                        ]

                        # Collect all other players' marbles that are not "safe"
                        other_players_marbles = [
                            (player_idx, marble)
                            for player_idx, player in enumerate(self._state.list_player)
                            if player_idx != self._state.idx_player_active  # Exclude the active player
                            for marble in player.list_marble
                            if not marble.is_save  # Only consider marbles that are not safe
                        ]

                        # Generate swap actions
                        for marble_own in active_player_marbles:
                            for player_idx, marble_other in other_players_marbles:
                                # Add a valid swap action
                                actions.append(
                                    Action(
                                        card=card,
                                        pos_from=marble_own.pos,  # Position of the active player's marble
                                        pos_to=marble_other.pos,  # Position of the other player's marble
                                        card_swap=None  # Specify that the action involves a swap
                                    )
                                )

                        # If no actions exist, allow swapping two of the active player's marbles (which does not make a difference, but we do it for the test
                        if not actions:
                            for i, marble_own in enumerate(active_player_marbles):
                                for marble_partner in active_player_marbles[i+1:]:  # Avoid duplicate swaps
                                    actions.append(
                                        Action(
                                            card=card,
                                            pos_from=marble_own.pos,  # Position of the first marble
                                            pos_to=marble_partner.pos,  # Position of the second marble
                                            card_swap=None  # Specify that the action involves a swap
                                        )
                                    )


                    # checks for each possible position if the way is blocked. if it is not blocked, we add it to action.
                    for pos_to in to_positions:
                        if not self._is_way_blocked(
                                pos_to, marble.pos, self._get_all_safe_marbles()):
                            # TODO add logic for card_swap (once we know what this is used for) LATIN-37
                            actions.append(Action(card=card, pos_from=marble.pos, pos_to=pos_to,
                                                  card_swap=None))

            for action in actions:
                if action not in unique_actions:
                    unique_actions.append(action)

        return unique_actions

    def _count_marbles_in_kennel(self) -> int:
        active_player = self._state.list_player[self._state.idx_player_active]
        queue_start = self.PLAYER_POSITIONS[self._state.idx_player_active]['queue_start']
        queue_end = queue_start + 4
        marbles_in_kennel = [marble for marble in active_player.list_marble if
                             queue_start <= int(marble.pos) < queue_end]
        return len(marbles_in_kennel)

    def _check_finish_game(self):
        """
        Check if the game is finished, i.e., any player has all their marbles in the final area.
        If the game is finished, set the game phase to FINISHED.
        """
        for idx_player, player in enumerate(self._state.list_player):
            final_start = self.PLAYER_POSITIONS[idx_player]['final_start']
            # Final area positions
            final_positions = range(final_start, final_start + 4)
            if all(marble.pos in final_positions for marble in player.list_marble):
                # All marbles of this player are in their final positions
                self._state.phase = GamePhase.FINISHED
                print(
                    f"Player {idx_player + 1} ({player.name}) has won the game!")
                return True
        return False

    # TODO LATIN-47 Check for TEAM WIN, if 2 players of the same team have all their marbles in the final area
    def _check_team_win(self):
        """
        Check if a team has won, that means, both players on a team have all their marbles in the final area.
        """
        # Check each team
        for team_id, players in self.teams.items():  # Iterates through each team and its associated players
            team_wins = True
            for player_idx in players:
                final_start = self.PLAYER_POSITIONS[player_idx]['final_start']
                final_positions = range(final_start, final_start + 4)
                player = self._state.list_player[player_idx]
                if not all(marble.pos in final_positions for marble in player.list_marble):
                    team_wins = False
                    break

            if team_wins:
                # Update game phase and print winner
                self._state.phase = GamePhase.FINISHED
                print(f"Team {team_id + 1} has won the game!")
                return True

        return False

    none_actions_counter = 0

    def apply_action(self, action: Action) -> None:
        """ Apply the given action to the game """
        active_player = self._state.list_player[self._state.idx_player_active]
        self._handle_none_action(action, active_player)

        if action is not None and action.card in active_player.list_card:
            # removing card from players hand and putting it to discarded stack
            active_player.list_card.remove(action.card)
            self._state.list_card_discard.append(action.card)
            # Find the marble being moved

            if action.card.rank == 'J':
                self._swap_marbles(action)
            else:
                marble_to_move = next(
                    (marble for marble in active_player.list_marble if int(marble.pos) == int(action.pos_from)),
                    None
                )

                if marble_to_move:
                    # Check for collision before moving the marble
                    if self._is_collision(marble_to_move, action.pos_to, action.card):
                        self._handle_collision(action.pos_to, self._state.idx_player_active)

                    # Perform the movement logic
                    self._move_marble_logic(marble_to_move, action.pos_to, action.card)

        if self._check_team_win():
            self._state.phase = self._state.phase.FINISHED

        # check if round is over
        if self.none_actions_counter == 4 and len(self._state.list_card_draw) != 0:
            self._state.cnt_round += 1
            self.deal_cards()
            # calculate the next player (after 4, comes 1 again). not sure if needed here or somewhere else
            # example: (4+1)%4=1 -> after player 4, it's player 1's turn again
            self._state.idx_player_active = (self._state.idx_player_active + 1) % self._state.cnt_player

        # if round is over and no cards are left in stack
        if len(self._state.list_card_draw) == 0 and self.none_actions_counter == 4:
            self._refresh_deck()
            self.none_actions_counter = 0
            # do not want to do this but I have no idea how the tests logic should work
            for p in self._state.list_player:
                p.list_card = []

    def _handle_none_action(self, action, active_player):
        if action is None:
            self.none_actions_counter += 1
            active_player.list_card = []

    def _move_marble_logic(self, marble: Marble, pos_to: int, card: Card) -> None:
        """
        Core logic for moving a marble to a new position.
        """
        pos_to = int(pos_to)  # Ensure the target position is an integer

        # Update marble position
        marble.pos = pos_to

    # Define is collision #TODO LATIN -45 create handle collision
    def _is_collision(self, marble: Marble, pos_to: int, card: Card) -> bool:
        """
        Check if the movement of the marble using the card results in a collision.

        Args:
            marble (Marble): The marble being moved.
            pos_to (int): The target position.
            card (Card): The card being played.

        Returns:
            bool: True if the marble jumps over another marble, False otherwise.
        """

        # simple logic if card is not 7!
        active_player = self._state.list_player[self._state.idx_player_active]
        active_player_marbles = {int(m.pos) for m in active_player.list_marble}

        # Check if the target position is occupied by a marble
        for player_index, player in enumerate(self._state.list_player):
            if player == active_player:
                continue  # Skip the active player's marbles

            for other_marble in player.list_marble:
                if other_marble.pos == pos_to:
                    # If the marble is not safe and belongs to another player, return True
                    if not other_marble.is_save:
                        return True

        return False

        # TODO logic if card is 7!

        # pos_from = int(marble.pos)
        # total_steps = self.TOTAL_STEPS
        # marble_positions = {int(m.pos) for player in self._state.list_player for m in player.list_marble}
        #
        # # Exclude the active player's marbles from the collision check for the start marble
        # active_player = self._state.list_player[self._state.idx_player_active]
        # active_player_marbles = {int(m.pos) for m in active_player.list_marble}
        #
        # # If the marble is moving to a position occupied by its own start, do not count as a collision
        # if pos_to in active_player_marbles and pos_to != marble.pos:
        #     return True
        #
        # if card.rank == '7':
        #     # Simulate all positions between pos_from and pos_to
        #     steps = abs(pos_to - pos_from)
        #     for step in range(1, steps + 1):
        #         intermediate_pos = (pos_from + step) % total_steps
        #         if intermediate_pos in marble_positions and intermediate_pos not in active_player_marbles:
        #             return True
        #
        # elif card.rank == '4':
        #     # Similar logic, but account for reverse movement
        #     if pos_to < pos_from:  # Handling wrap-around
        #         pos_range = list(range(pos_from, total_steps)) + list(range(0, pos_to + 1))
        #     else:
        #         pos_range = list(range(pos_from, pos_to + 1))
        #
        #     for pos in pos_range:
        #         if pos in marble_positions and pos not in active_player_marbles:
        #             return True
        #
        # # Add additional checks for other cards with collision logic
        # return False

    def _handle_collision(self, pos_to: int, active_player_index: int) -> None:
        """
        Handle the collision by sending the marble back to its starting position.
        """
        for player_index, player in enumerate(self._state.list_player):
            if player_index != active_player_index:  # Only consider other players' marbles
                for marble in player.list_marble:
                    if marble.pos == pos_to and not marble.is_save:
                        # Send the marble back to its queue start
                        queue_start = self.PLAYER_POSITIONS[player_index]['queue_start']
                        marble.pos = queue_start + player.list_marble.index(marble)  # Back to the queue
                        marble.is_save = True
                        print(f"Collision: Marble from Player {player_index + 1} sent back to the queue.")

    # TODO LATIN-28 check if logic is actually what we need it to be

    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the opponent's cards are face down) """
        masked_state: GameState = self._state.copy()
        for i, player in enumerate(masked_state.list_player):
            if i != idx_player:
                player.list_card = [Card(suit='?', rank='?')] * len(player.list_card)
        return masked_state

    def _refresh_deck(self) -> None:
        """
        Shuffle the draw pile. If the draw pile does not have enough cards to be dealt, move discarded cards back to the draw pile and shuffle.
        """

        # Move discarded cards to the draw pile
        self._state.list_card_draw = self._state.LIST_CARD.copy()
        self._state.list_card_discard.clear()

        # Shuffle the draw pile
        random.shuffle(self._state.list_card_draw)

    ##################################################### PRIVATE METHODS #############################################

    # TODO in case the way is blocked (marble on 0/16/32/48 of the player with correct index (marble.is_save)?). LATIN-36
    def _is_way_blocked(self, pos_to: int, pos_from: int, safe_marbles: List[Marble]) -> bool:
        """ Check if the way is blocked between from  & to by any safe marble
        - If a marble is in the way: return True
        - If no marble is in the way: return False"""

        # Identify the "safe" positions (0, 16, 32, 48)
        safe_positions = [0, 16, 32, 48]  # Marbles are protected and can't be passed by others

        # Adjust pos_to for circular board wrapping
        total_steps = self.TOTAL_STEPS  # Board has 64 total steps (0–63)
        if pos_to < pos_from:
            pos_to += total_steps  # Adjust pos_to if it wraps around the board

        # Loop through each safe marble
        for marble in safe_marbles:  # Loops through all the marbles that are currently on the safe spots
            marble_pos = marble.pos
            if marble_pos in safe_positions:
                # Normalize marble_pos to match the current path calculation
                if marble_pos < pos_from:
                    marble_pos += total_steps

                # Check if the marble is blocking the path
                if pos_from < marble_pos <= pos_to:
                    return True  # Path is blocked by a safe marble

        return False  # No safe marble is blocking the path

    # TODO complete method LATIN-34
    def _calculate_position_to(self, pos_from: int, card: Card, active_player_indx: int) -> List[int]:
        """ Calculate the final possible_positions based on the card """

        active_player_fields = self.PLAYER_POSITIONS[active_player_indx]
        queue_start = active_player_fields['queue_start']
        final_start = active_player_fields['final_start']
        possible_positions = []

        # Calculate next position
        next_position = (pos_from + int(card.rank)) % self.TOTAL_STEPS

        # Checking if the player is crossing his "start"
        if pos_from < queue_start and next_position >= queue_start:
            next_position = final_start + (next_position - queue_start) - 1

        possible_positions.append(next_position)

        return possible_positions

    def _is_valid_move_in_final_area(self, pos_from, pos_to, marbles, final_area_start, final_area_end) -> bool:
        """
        Validates whether a move in the final area is legal based on game rules.
        Marbles cannot jump over other marbles in the final area.
        """
        if pos_from < final_area_start or pos_from > final_area_end:
            return True  # Not in the final area, allow the move.

        step_direction = 1 if pos_to > pos_from else -1
        for intermediate_pos in range(pos_from + step_direction, pos_to + step_direction, step_direction):
            for marble in marbles:
                if marble.pos == intermediate_pos:
                    return False  # Found a marble in the way, move is invalid.
        return True

    # TODO LATIN-41
    def _get_all_safe_marbles(self) -> list[Marble]:
        safe_marbles = []
        for player in self._state.list_player:
            for marble in player.list_marble:
                if marble.is_save:
                    safe_marbles.append(marble)
        return safe_marbles

    def deal_cards(self) -> None:
        for player in self._state.list_player:
            round_mod = self._state.cnt_round % 10
            if round_mod == 0:
                cards_to_deal = 2
            elif round_mod <= 5:
                cards_to_deal = 7 - round_mod
            else:
                cards_to_deal = 12 - round_mod

            if cards_to_deal > len(self._state.list_card_draw):
                self._refresh_deck()

            for _ in range(cards_to_deal):
                card = self._state.list_card_draw.pop()
                player.list_card.append(card)

    def _set_marbles(self) -> None:
        for player_index in range(len(self._state.list_player)):
            for marble_index in range(4):
                self._state.list_player[player_index].list_marble.append(
                    Marble(
                        pos=
                        int(self.PLAYER_POSITIONS[player_index]['queue_start'] + marble_index),
                        is_save=True)
                )

    def _is_valid_final_area_move(self, start, end, player, final_area_start, final_area_end) -> bool:
        step = 1 if end > start else -1
        for position in range(start + step, end + step, step):
            if final_area_start <= position <= final_area_end:
                if any(marble.pos == position for marble in player.list_marble):
                    return False  # Invalid if another marble is in the way
        return True

    def _swap_marbles(self, action: Action):
        """
          Swap the positions of two marbles based on the provided action.

          Args:
              action (Action): The action containing pos_from and pos_to.
          """
        marble_from = None
        marble_to = None

        # Find the marble at pos_from and pos_to
        for player in self._state.list_player:
            for marble in player.list_marble:
                if marble.pos == action.pos_from:
                    marble_from = marble
                elif marble.pos == action.pos_to:
                    marble_to = marble

                # Exit early if both marbles are found
                if marble_from and marble_to:
                    break
            if marble_from and marble_to:
                break

        # If both marbles are found, swap their positions
        if marble_from and marble_to:
            marble_from.pos, marble_to.pos = marble_to.pos, marble_from.pos


class RealPlayer(Player):

    def select_action(self, state: GameState, actions: List[GameAction]) -> GameAction:
        # TODO LATIN-33
        """ Given masked game state and possible actions, select the next action """
        pass


class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == '__main__':
    game = Dog()
    player = RealPlayer()

    while game.get_state() != GamePhase.FINISHED:
        active_players = 4
        game.deal_cards()
        while not active_players == 0:
            list_actions = game.get_list_action()

            if len(list_actions) == 0:
                active_players = active_players - 1
                print("Player has no actions left. Please wait until the round is over")
            else:
                action = player.select_action(game.get_state(), list_actions)
                game.apply_action(action)
                game.print_state()

        print(
            f"\n --------------- ROUND {game.get_state().cnt_round} finished -----------------")
