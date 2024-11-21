# runcmd: cd ../.. & venv\Scripts\python server/py/dog_template.py
import random
from enum import Enum
from typing import List, Optional, ClassVar

from pydantic import BaseModel

from server.py.game import Game, Player


class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank


class Marble(BaseModel):
    pos: str  # position on board (0 to 95)
    is_save: bool  # true if marble was moved out of kennel and was not yet moved


class PlayerState(BaseModel):
    name: str  # name of player
    list_card: List[Card]  # list of cards
    list_marble: List[Marble]  # list of marbles


class Action(BaseModel):
    card: Card  # card to play
    pos_from: Optional[int]  # position to move the marble from
    pos_to: Optional[int]  # position to move the marble to
    card_swap: Optional[Card]  # optional card to swap () # TODO what is this used for? is this even required for Brandi-Dog?!?


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
                                          Card(suit='♠', rank='2'), Card(suit='♥', rank='2'), Card(suit='♦', rank='2'),
                                          Card(suit='♣', rank='2'),
                                          # 3: Move 3 spots forward
                                          Card(suit='♠', rank='3'), Card(suit='♥', rank='3'), Card(suit='♦', rank='3'),
                                          Card(suit='♣', rank='3'),
                                          # 4: Move 4 spots forward or back
                                          Card(suit='♠', rank='4'), Card(suit='♥', rank='4'), Card(suit='♦', rank='4'),
                                          Card(suit='♣', rank='4'),
                                          # 5: Move 5 spots forward
                                          Card(suit='♠', rank='5'), Card(suit='♥', rank='5'), Card(suit='♦', rank='5'),
                                          Card(suit='♣', rank='5'),
                                          # 6: Move 6 spots forward
                                          Card(suit='♠', rank='6'), Card(suit='♥', rank='6'), Card(suit='♦', rank='6'),
                                          Card(suit='♣', rank='6'),
                                          # 7: Move 7 single steps forward
                                          Card(suit='♠', rank='7'), Card(suit='♥', rank='7'), Card(suit='♦', rank='7'),
                                          Card(suit='♣', rank='7'),
                                          # 8: Move 8 spots forward
                                          Card(suit='♠', rank='8'), Card(suit='♥', rank='8'), Card(suit='♦', rank='8'),
                                          Card(suit='♣', rank='8'),
                                          # 9: Move 9 spots forward
                                          Card(suit='♠', rank='9'), Card(suit='♥', rank='9'), Card(suit='♦', rank='9'),
                                          Card(suit='♣', rank='9'),
                                          # 10: Move 10 spots forward
                                          Card(suit='♠', rank='10'), Card(suit='♥', rank='10'),
                                          Card(suit='♦', rank='10'), Card(suit='♣', rank='10'),
                                          # Jake: A marble must be exchanged
                                          Card(suit='♠', rank='J'), Card(suit='♥', rank='J'), Card(suit='♦', rank='J'),
                                          Card(suit='♣', rank='J'),
                                          # Queen: Move 12 spots forward
                                          Card(suit='♠', rank='Q'), Card(suit='♥', rank='Q'), Card(suit='♦', rank='Q'),
                                          Card(suit='♣', rank='Q'),
                                          # King: Start or move 13 spots forward
                                          Card(suit='♠', rank='K'), Card(suit='♥', rank='K'), Card(suit='♦', rank='K'),
                                          Card(suit='♣', rank='K'),
                                          # Ass: Start or move 1 or 11 spots forward
                                          Card(suit='♠', rank='A'), Card(suit='♥', rank='A'), Card(suit='♦', rank='A'),
                                          Card(suit='♣', rank='A'),
                                          # Joker: Use as any other card you want
                                          Card(suit='', rank='JKR'), Card(suit='', rank='JKR'),
                                          Card(suit='', rank='JKR')
                                      ] * 2

    cnt_player: int = 4  # number of players (must be 4)
    phase: GamePhase  # current phase of the game
    cnt_round: int  # current round
    bool_game_finished: bool  # true if game has finished
    bool_card_exchanged: bool  # true if cards was exchanged in round
    idx_player_started: int  # index of player that started the round
    idx_player_active: int  # index of active player in round
    list_player: List[PlayerState]  # list of players
    list_id_card_draw: List[Card]  # list of cards to draw
    list_id_card_discard: List[Card]  # list of cards discarded
    card_active: Optional[Card]  # active card (for 7 and JKR with sequence of actions)

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
            f"Cards to Draw: {len(self.list_id_card_draw)}\n"
            f"Cards Discarded: {len(self.list_id_card_discard)}\n"
            f"Active Card: {self.card_active}\n"
        )


class Dog(Game):
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
            phase=GamePhase.SETUP,
            cnt_round=0,
            bool_game_finished=False,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=[PlayerState(name=f"Player {i + 1}", list_card=[], list_marble=[]) for i in range(4)],
            list_id_card_draw=GameState.LIST_CARD.copy(),
            list_id_card_discard=[],
            card_active=None
        )
        random.shuffle(self._state.list_id_card_draw)

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
        to_positions = []
        active_player = self._state.list_player[self._state.idx_player_active]
        for card in active_player.list_card:
            for marble in active_player.list_marble:
                # TODO Go through all cards and marbles and return the possible positions.
                if card.rank.isdigit() and card.rank not in ['7', '4']:
                    to_positions = self._calculate_position_to(int(marble.pos), card, self._state.idx_player_active)

                # TODO Add more logic for all the other cards LATIN-35
                if card.rank == '7':
                    # can be split into multiple marbles. if takes over, reset other marble
                    # to_positions = ...
                    pass

                # checks for each possible position if the way is blocked. if it is not blocked, we add it to action.
                for pos_to in to_positions:
                    if not self._is_way_blocked(
                            pos_to, int(marble.pos), self._get_all_safe_marbles()):
                        actions.append(Action(card=card, pos_from=marble.pos, pos_to=pos_to,
                                              card_swap=None))  # TODO add logic for card_swap (once we know what this is used for) LATIN-37

        return actions

    # TODO LATIN-27
    def apply_action(self, action: Action) -> None:
        """ Apply the given action to the game """
        active_player = self._state.list_player[self._state.idx_player_active]
        if action.card in active_player.list_card:
            # removing card from players hand and putting it to discarded stack
            active_player.list_card.remove(action.card)
            self._state.list_id_card_discard.append(action.card)

            # Example logic to update the game state based on the action
            if action.pos_from is not None and action.pos_to is not None:
                # TODO Move marble logic LATIN-38
                pass
            # TODO Add more logic for other actions

        # calculate the next player (after 4, comes 1 again). not sure if needed here or somewhere else
        # example: (4+1)%4=1 -> after player 4, it's player 1's turn again
        self._state.idx_player_active = (self._state.idx_player_active + 1) % self._state.cnt_player

    # TODO LATIN-28 check if logic is actually what we need it to be
    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the opponent's cards are face down) """
        masked_state: GameState = self._state.copy()
        for i, player in enumerate(masked_state.list_player):
            if i != idx_player:
                player.list_card = [Card(suit='?', rank='?')] * len(player.list_card)
        return masked_state

    ##################################################### PRIVATE METHODS #############################################

    # TODO in case the way is blocked (marble on 0/16/32/48 of the player with correct index?). LATIN-36
    def _is_way_blocked(self, pos_to: int, pos_from: int, safe_marbles : List[Marble]) -> bool:
        """ Check if the way is blocked between from  & to by any safe marble """
        pass

    # TODO complete method LATIN-34
    def _calculate_position_to(self, pos_from: int, card: Card, active_player_indx: int) -> List[int]:
        """ Calculate the final possible_positions based on the card """

        active_player_fields = self.PLAYER_POSITIONS[active_player_indx]
        start = active_player_fields['start']
        queue_start = active_player_fields['queue_start']
        final_start = active_player_fields['final_start']
        possible_positions = []

        if card.rank.isdigit() and card.rank not in ['7', '4']:
            # Calculate next position
            next_position = (pos_from + int(card.rank)) % self.TOTAL_STEPS

            # Checking if the player is crossing his "start"
            if pos_from < queue_start and next_position >= queue_start:
                next_position = final_start + (next_position - queue_start) - 1

            possible_positions.append(next_position)


        elif card.rank == '4':
            # TODO refactor this logic. deals just as an example (it works probably, but still, refactor it maybe)

            # Calculate next position
            next_position = (pos_from + 4) % self.TOTAL_STEPS

            # Checking if the player is crossing his "start"
            if pos_from < queue_start and next_position >= queue_start:
                next_position = final_start + (next_position - queue_start) - 1

            possible_positions.append(next_position)

            ####################################################### separator of logic for +4 & -4

            # Calculate next position
            if pos_from == 0:
                next_position = self.TOTAL_STEPS - 4
            else:
                next_position = (pos_from - 4) % self.TOTAL_STEPS

            # Checking if the player is crossing his "start"
            if pos_from < queue_start and next_position >= queue_start:
                next_position = final_start + (next_position - queue_start) - 1

            possible_positions.append(next_position)

        elif card.rank == '7':
            # TODO add logic
            # remember that if you overtake with this card, the marble which was overtaken will be sent back to kennel. even your own marbles
            # cannot overtake blocked fields
            pass

        elif card.rank == 'J':
            # TODO add logic
            pass

        # TODO Add more logic for other special cards (K, A, Joker)

        return possible_positions

    # TODO LATIN-41
    def _get_all_safe_marbles(self) -> List[Marble]:
        # use marble.is_save

        pass


class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == '__main__':
    game = Dog()
