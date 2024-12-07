from typing import List, Optional, ClassVar
from enum import Enum
import random
from pydantic import BaseModel
from server.py.game import Game, Player


class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank


class Marble(BaseModel):
    pos: int       # position on board (0 to 95)
    is_save: bool  # true if marble was moved out of kennel and was not yet moved


class PlayerState(BaseModel):
    name: str                  # name of player
    list_card: List[Card]      # list of cards
    list_marble: List[Marble]  # list of marbles


class Action(BaseModel):
    card: Card                 # card to play
    pos_from: Optional[int]    # position to move the marble from
    pos_to: Optional[int]      # position to move the marble to
    card_swap: Optional[Card] = None # optional card to swap ()


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

    KENNEL_POSITIONS = [
        [64, 65, 66, 67],  # Positions for player index 0
        [72, 73, 74, 75],  # Positions for player index 1
        [80, 81, 82, 83],  # Positions for player index 2
        [88, 89, 90, 91]  # Positions for player index 3
    ]

    # Define starting positions for each player
    START_POSITION = [0, 16, 32, 48]

    #Define Finish Position
    FINISH_POSITIONS = [
        [71, 70, 69, 68],  #  Positions for player index 0
        [79, 78, 77, 76],  #  Positions for player index 1
        [87, 86, 85, 84],  #  Positions for player index 0
        [95, 94, 93, 92],  #  Positions for player index 0
    ]

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """
        # Initialize the game state
        self.state: GameState = GameState(
            cnt_player=4,
            phase=GamePhase.SETUP,
            cnt_round=1,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=[],
            list_card_draw=[],
            list_card_discard=[],
            card_active=None,
        )

        # Initialize the deck of cards
        self.state.list_card_draw = GameState.LIST_CARD.copy()
        random.shuffle(self.state.list_card_draw)

        # Initialize the players
        for idx in range(self.state.cnt_player):
            player_state: PlayerState = PlayerState(
                name = f"Player {idx + 1}",
                list_card=[],
                list_marble=[],
            )

            # Initialize player's marbles
            for marble_idx in range(4):  # 4 marbles per player
                marble = Marble(
                    pos = self.KENNEL_POSITIONS[idx][marble_idx],  # get the position from the kennel
                    is_save = False)
                player_state.list_marble.append(marble)

            # Add the player state to the game state
            self.state.list_player.append(player_state)

        # Randomly select starting player
        self.state.idx_player_started = random.randint(0, self.state.cnt_player - 1)
        self.state.idx_player_active = self.state.idx_player_started

        # Initialize the state of the card exchange
        self.state.bool_card_exchanged = False

        # Initialize the number of rounds
        # (Stefan) Is this necessary? we already initialized cnt_round to 1 in INIT
        self.state.cnt_round = 1

        # # TODO: deal cards as an action ?? -> probably make a separate function for this outside the init
        # num_cards_per_player = 6  # Number of cards per player in the first round
        # total_cards_to_deal = num_cards_per_player * self.state.cnt_player
        # assert len(self.state.list_card_draw) >= total_cards_to_deal, (
        #     f"Not enough cards to deal: required {total_cards_to_deal}, "
        #     f"but only {len(self.state.list_card_draw)} available."
        # )
        #
        # for _ in range(num_cards_per_player):
        #     for player_state in self.state.list_player:
        #         # Draw a card for the player
        #         card = self.state.list_card_draw.pop()
        #         player_state.list_card.append(card)
        self.state.phase = GamePhase.RUNNING

        # Deal initial cards for the first round (6 cards per player)
        self.deal_cards(num_cards_per_player=6)

    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        self.state = state

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        return self.state

    def print_state(self) -> None:
        """ Print the current game state """
        if not self.state:
            print("No state set.")
            return

        print("\n--- Game State ---")
        print(f"Phase: {self.state.phase}")
        print(f"Round: {self.state.cnt_round}")
        print(f"Active Player: Player {self.state.idx_player_active + 1}")
        print(f"Started by: Player {self.state.idx_player_started + 1}")
        print(f"Cards Exchanged: {self.state.bool_card_exchanged}")
        print("\nDiscard Pile:")
        if self.state.list_card_discard:
            for card in self.state.list_card_discard:
                print(f"  {card.suit}{card.rank}")
        else:
            print("Empty")
        print("\nPlayers:")
        for idx, player in enumerate(self.state.list_player):
            print(f"Player {idx + 1} - {player.name}")
            print("Cards:")
            for card in player.list_card:
                print(f"{card.suit}{card.rank}")
            print("Marbles:")
            for marble in player.list_marble:
                print(f"Position: {marble.pos}, Safe: {marble.is_save}")

    def get_list_action(self) -> List[Action]:
        """ Get a list of possible actions for the active player """
        actions: List[Action] = []

        active_player_idx = self.state.idx_player_active
        active_player = self.state.list_player[active_player_idx]
        start_position = self.START_POSITION[active_player_idx]

        # shuffle cards and distribute, when all cards are played
        # TODO: I dont think this should be in the get_list_action function (Pascal)
        # Moved to start_new_round function. Each round, it checks if draw pile needs to be shuffled.
        
        # Check if cards have to be exchanged
        if not self.state.bool_card_exchanged:
            # target_player (diagonal player)
            target_player_idx = (active_player_idx + 2) % 4
            target_player = self.state.list_player[target_player_idx]

            # chose random card of the active player
            random_card_from_active = random.choice(active_player.list_card)

            # chose random card of the target player
            random_card_from_target = random.choice(target_player.list_card)

            # create exchange action
            exchange_action = Action(
                card=random_card_from_active,  # card that the active player gives away
                pos_from=None,
                pos_to=None,
                card_swap=random_card_from_target  # card that the target player gives away
            )
            actions.append(exchange_action)

            return actions

        # Check if the start position is unoccupied
        if not any(marble.pos == start_position
                   for marble in self.state.list_player[active_player_idx].list_marble):
            # Start position is unoccupied

            # Check if the player has any marbles in the kennel
            marbles_in_kennel = [
                marble for marble in self.state.list_player[active_player_idx].list_marble
                if marble.pos in self.KENNEL_POSITIONS[active_player_idx]
            ]
            marbles_in_kennel.sort(key=lambda x: x.pos)

            for card in active_player.list_card:
                if card.rank in ['K', 'A', 'JKR']:
                    if marbles_in_kennel:
                        # Move the marble in the first kennel position to the start position
                        action = Action(
                            card = card,
                            pos_from = marbles_in_kennel[0].pos,
                            pos_to = start_position,
                            card_swap = None
                        )
                        actions.append(action)

                        # After playing the card, add it to the discard pile
                        self.state.list_card_discard.append(card)
                        active_player.list_card.remove(card)  # Remove card from player's hand

        # Check possible move actions for each marble
        for card in active_player.list_card:
            if card.rank not in ['7', 'J', 'JKR', '4']:
                # "normal" Cards
                for marble_idx, marble in enumerate(active_player.list_marble):
                    if marble.pos not in self.KENNEL_POSITIONS[active_player_idx]:
                        # Total moves allowed by the card
                        if card.rank == 'A':
                            num_moves = 1 # TODO: Need to implement the logic for 1 or 11
                        elif card.rank == 'K':
                            num_moves = 13
                        elif card.rank == 'Q':
                            num_moves = 12
                        else:
                            num_moves = int(card.rank)

                        # Set move to allowed (will be rechecked in following steps)
                        move_allowed = True

                        # Create test game state
                        test_state = self.state.model_copy(deep = True)

                        for _ in range(num_moves):
                            test_state.list_player[active_player_idx].list_marble[marble_idx].pos += 1
                            validity = self.check_move_validity(
                                test_state, active_player_idx, marble_idx)
                            if not validity:
                                move_allowed = False
                                break

                        if move_allowed:
                            actions.append(
                                Action(
                                    card=card,
                                    pos_from=marble.pos,
                                    pos_to=test_state.list_player[active_player_idx].list_marble[marble_idx].pos,
                                    card_swap=None
                                )
                            )

                            # After playing the card, add it to the discard pile
                            self.state.list_card_discard.append(card)
                            active_player.list_card.remove(card)  # Remove card from player's hand

                # --- Card 7 ---
                if card.rank == '7':
                    for split1 in range(1, 8):  # First Action
                        split2 = 7 - split1    # Second Action
                        for marble1 in active_player.list_marble:
                            for marble2 in active_player.list_marble:
                                if marble1.pos not in self.KENNEL_POSITIONS[active_player_idx]:
                                    test_state = self.state.model_copy(deep=True)
                                    test_state.list_player[active_player_idx].list_marble[marble1.pos].pos += split1
                                    validity1 = self.check_move_validity(
                                        test_state, active_player_idx, marble1.pos)

                                    if split2 > 0 and marble2.pos != marble1.pos:
                                        test_state.list_player[active_player_idx].list_marble[marble2.pos].pos += split2
                                        validity2 = self.check_move_validity(
                                            test_state, active_player_idx, marble2.pos)
                                    else:
                                        validity2 = True

                                    if validity1 and validity2:
                                        actions.append(
                                            Action(
                                                card=card,
                                                pos_from=marble1.pos,
                                                pos_to=test_state.list_player[active_player_idx].list_marble[marble1.pos].pos,
                                                card_swap=None
                                            )
                                        )

                                        # After playing the card, add it to the discard pile
                                        self.state.list_card_discard.append(card)
                                        active_player.list_card.remove(card)  # Remove card from player's hand

                # --- Joker ---
                if card.rank == 'JKR':
                    for possible_card in range(1, 14):
                        for marble in active_player.list_marble:
                            if marble.pos not in self.KENNEL_POSITIONS[active_player_idx]:
                                num_moves = possible_card
                                move_allowed = True
                                test_state = self.state.model_copy(deep=True)

                                for _ in range(num_moves):
                                    test_state.list_player[active_player_idx].list_marble[marble.pos].pos += 1
                                    validity = self.check_move_validity(
                                        test_state, active_player_idx, marble.pos)
                                    if not validity:
                                        move_allowed = False
                                        break

                                if move_allowed:
                                    actions.append(
                                        Action(
                                            card=Card(suit='', rank=str(possible_card)),
                                            pos_from=marble.pos,
                                            pos_to=test_state.list_player[active_player_idx].list_marble[marble.pos].pos,
                                            card_swap=None
                                        )
                                    )

                                    # After playing the card, add it to the discard pile
                                    self.state.list_card_discard.append(card)
                                    active_player.list_card.remove(card)  # Remove card from player's hand

                # --- Jack ---
                if card.rank == 'J':
                    all_marbles = [
                        (idx, m) for idx, p in enumerate(self.state.list_player)
                        for m in p.list_marble
                    ]
                    for my_marble in active_player.list_marble:
                        for other_idx, other_marble in all_marbles:
                            if my_marble.pos != other_marble.pos:
                                actions.append(
                                    Action(
                                        card=card,
                                        pos_from=my_marble.pos,
                                        pos_to=other_marble.pos,
                                        card_swap=None
                                    )
                                )

                                # After playing the card, add it to the discard pile
                                self.state.list_card_discard.append(card)
                                active_player.list_card.remove(card)  # Remove card from player's hand

                if card.rank == '4':
                    for marble in active_player.list_marble:
                        if marble.pos not in self.KENNEL_POSITIONS[active_player_idx]:
                            pos_to_backwards = (marble.pos - 4) % 64
                            pos_to_forwards = (marble.pos + 4) % 64

                            # Check if backwards is allowed
                            test_state_backwards = self.state.model_copy(deep=True)
                            test_state_backwards.list_player[active_player_idx].list_marble[marble_idx].pos = pos_to_backwards

                            # Check if forwards is allowed
                            test_state_forwards = self.state.model_copy(deep=True)
                            test_state_forwards.list_player[active_player_idx].list_marble[marble_idx].pos = pos_to_forwards

                            if self.check_move_validity(test_state_backwards, active_player_idx, marble_idx):
                                actions.append(
                                    Action(
                                        card=card,
                                        pos_from=marble.pos,
                                        pos_to=pos_to_backwards,
                                        card_swap=None
                                    )
                                )

                            if self.check_move_validity(test_state_forwards, active_player_idx, marble_idx):
                                actions.append(
                                    Action(
                                        card=card,
                                        pos_from=marble.pos,
                                        pos_to=pos_to_forwards,
                                        card_swap=None
                                    )
                                )

                                # After playing the card, add it to the discard pile
                                self.state.list_card_discard.append(card)
                                active_player.list_card.remove(card)  # Remove card from player's hand

        return actions

    # (Stefan): deal cards as new action
    def deal_cards(self, num_cards_per_player: int):
        """Deal a specified number of cards to each player."""
        total_cards_to_deal = num_cards_per_player * self.state.cnt_player
        assert len(self.state.list_card_draw) >= total_cards_to_deal, (
            f"Not enough cards to deal: required {total_cards_to_deal}, "
            f"but only {len(self.state.list_card_draw)} available."
        )

        # Clear players' hands before dealing new cards
        for player_state in self.state.list_player:
            player_state.list_card.clear()

        # Deal the cards to each player
        for _ in range(num_cards_per_player):
            for player_state in self.state.list_player:
                card = self.state.list_card_draw.pop()  # Pop a card from the deck
                player_state.list_card.append(card)

        # If there aren't enough cards left to deal, reshuffle the discard pile into the draw pile
        if len(self.state.list_card_draw) < total_cards_to_deal:
            print("Not enough cards in draw pile. Reshuffling discard pile into draw pile.")
            self.state.list_card_draw.extend(self.state.list_card_discard)
            self.state.list_card_discard.clear()
            random.shuffle(self.state.list_card_draw)

    # (Stefan): I tested new round with a helper method start_new_round to simplify code in apply action.
    def start_new_round(self):
        """ Begin a new round by reshuffling and distributing cards. """
        # Increment round number
        self.state.cnt_round += 1
        if self.state.cnt_round > 5:
            self.state.cnt_round = 1  # Reset after round 5 to round 1

        # Set number of cards per player based on round
        if 1 <= self.state.cnt_round <= 5:
            num_cards_per_player = 7 - self.state.cnt_round  # 6, 5, 4, 3, 2 cards
        elif self.state.cnt_round == 6:
            num_cards_per_player = 6  # Reset to 6 cards
        else:
            num_cards_per_player = max(7 - ((self.state.cnt_round - 1) % 5 + 1), 2)

        # Deal the correct number of cards to each player for the current round
        self.deal_cards(num_cards_per_player)

        # Reset the exchange state and set active player
        self.state.bool_card_exchanged = False
        self.state.idx_player_active = 0

        # Set the game phase to RUNNING
        self.state.phase = GamePhase.RUNNING

    def apply_action(self, action: Action) -> None:
        """Apply the given action to the game."""
        active_player_index = self.state.idx_player_active

        # Handle the case where action is None (start a new round)
        # handles errors in benchmark file. all tests running without errors.
        if action is None:
            self.start_new_round()
            return

        # Check input of pos_from and pos_to
        if (action.pos_from is not None and action.pos_from != -1 and
                action.pos_to is not None and action.pos_to != -1):
            # Move a marble
            for idx_marble, marble in enumerate(self.state.list_player[active_player_index].list_marble):
                if marble.pos == action.pos_from:
                    self.state.list_player[active_player_index].list_marble[idx_marble].pos = action.pos_to

                    # Check if the marble is moved out of the kennel
                    if action.pos_from in self.KENNEL_POSITIONS[active_player_index]:
                        self.state.list_player[active_player_index].list_marble[idx_marble].is_save = True

        # Handle card swapping
        elif action.card_swap is not None:
            target_player_idx = (active_player_index + 2) % 4

            # Active player gives their card and the target player receives it
            self.state.list_player[active_player_index].list_card.remove(action.card)
            self.state.list_player[target_player_idx].list_card.append(action.card)

            # Target player gives a random card back
            self.state.list_player[target_player_idx].list_card.remove(action.card_swap)
            self.state.list_player[active_player_index].list_card.append(action.card_swap)

            self.state.bool_card_exchanged = True

        # move played card from hand to discard pile
        if action.card in self.state.list_player[active_player_index].list_card:
            self.state.list_player[active_player_index].list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)

        # Check if all players have finished their hands (end of round)
        if all(len(player.list_card) == 0 for player in self.state.list_player):
            self.start_new_round()



    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the opponent's cards are face down)"""
        # TODO: implement this
        player_view = self.state.model_copy(deep = True)
        return player_view

    def check_move_validity(self, test_state: GameState, active_player_idx: int, marble_idx: int) -> bool:
        """ Check if move is valid """
        marble = test_state.list_player[active_player_idx].list_marble[marble_idx]
        new_pos = marble.pos

        # check that not two marbles of the same color are at the same position
        for player_idx, player in enumerate(test_state.list_player):
                same_color_marbles = [
                    m for m in player.list_marble if m.pos == new_pos
                    ]
                if len(same_color_marbles) > 1:  # Blockade
                    return False

        # Check that the Finish is implemented correctly
        start_pos = self.START_POSITION[active_player_idx]
        kennel_pos = self.KENNEL_POSITIONS[active_player_idx]
        finish_pos = self.FINISH_POSITIONS[active_player_idx]

        # Check that marbles do not start from the kennel
        if new_pos == start_pos:
            if marble.pos in kennel_pos:
                return False

        # Prevent moving out of the kennel if an opponent's marble is at the start position
        if marble.pos in kennel_pos and new_pos == start_pos:
            # Check if any opponent's marble is at the active player's starting position
            for opponent_idx in range(4):  # Assuming 4 players
                if opponent_idx != active_player_idx:
                    opponent_start_pos = self.START_POSITION[opponent_idx]
                    # If an opponent's marble is at the active player's starting position, block the move
                    for opponent_marble in test_state.list_player[opponent_idx].list_marble:
                        if opponent_marble.pos == opponent_start_pos:
                            return False

        # Check that marble do not enter in finish direct from kennel or start
        if new_pos in finish_pos:
            if marble.pos not in kennel_pos or marble.pos == start_pos:
                return False

        # Check that marbles do not go back in kennel
        if new_pos in kennel_pos:
            return False

        # Do not allow positions outside the game
        if new_pos < 0 or new_pos >= 96:
            return False

        return True


class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == '__main__':

    game = Dog()
