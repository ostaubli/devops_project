# runcmd: cd ../.. & venv\Scripts\python server/py/dog_template.py

import random
import copy
from typing import List, Optional, ClassVar
from enum import Enum
from pydantic import BaseModel
if __name__ == '__main__':
    from game import Game, Player
else:
    from server.py.game import Game, Player


class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank


class Marble(BaseModel):
    pos: int  # position on board (0 to 95)
    is_save: bool  # true if marble was moved out of kennel and was not yet moved
    start_pos: int  # Kennel Position for sending home


class PlayerState(BaseModel):
    name: str  # name of player [PlayerBlue, PlayerRed, PlayerYellow, PlayerGreen]
    list_card: List[Card]  # list of cards
    list_marble: List[Marble]  # list of marbles
    list_kennel_pos: List[int]
    list_finish_pos: List[int]
    start_pos: int


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
    phase: GamePhase = GamePhase.SETUP  # current phase of the game
    cnt_round: int = 0  # current round
    bool_card_exchanged: bool = False  # true if cards was exchanged in round
    list_swap_card: List[Optional[Card]] = [None]*4 # empty Carddeck for cards to be swapt
    idx_player_started: int = random.randint(0, 3)  # index of player that started the round
    idx_player_active: int = idx_player_started  # index of active player in round
    list_player: List[PlayerState] = []  # list of players
    list_card_draw: List[Card] = LIST_CARD  # list of cards to draw ==> Was list_id_card_draw in given Template
    list_card_discard: List[Card] = []  # list of cards discarded
    card_active: Optional[Card] = None  # active card (for 7 and JKR with sequence of actions)

    def setup_players(self) -> None:  # Kägi
        player_blue = PlayerState(
            name="PlayerBlue",
            list_card=[],
            list_marble=[Marble(pos=64, is_save=True, start_pos=64),
                         Marble(pos=65, is_save=True, start_pos=65),
                         Marble(pos=66, is_save=True, start_pos=66),
                         Marble(pos=67, is_save=True, start_pos=67)],
            list_finish_pos=[68, 69, 70, 71],
            list_kennel_pos=[64, 65, 66, 67],
            start_pos=0
        )
        player_green = PlayerState(
            name="PlayerGreen",
            list_card=[],
            list_marble=[Marble(pos=72, is_save=True, start_pos=72),
                         Marble(pos=73, is_save=True, start_pos=73),
                         Marble(pos=74, is_save=True, start_pos=74),
                         Marble(pos=75, is_save=True, start_pos=75)],
            list_kennel_pos=[72, 73, 74, 75],
            list_finish_pos=[76, 77, 78, 79],
            start_pos=16
        )
        player_red = PlayerState(
            name="PlayerRed",
            list_card=[],
            list_marble=[Marble(pos=80, is_save=True, start_pos=80),
                         Marble(pos=81, is_save=True, start_pos=81),
                         Marble(pos=82, is_save=True, start_pos=82),
                         Marble(pos=83, is_save=True, start_pos=83)],
            list_finish_pos=[84, 85, 86, 87],
            list_kennel_pos=[80, 81, 82, 83],
            start_pos=32
        )
        player_yellow = PlayerState(
            name="PlayerYellow",
            list_card=[],
            list_marble=[Marble(pos=88, is_save=True, start_pos=88),
                         Marble(pos=89, is_save=True, start_pos=89),
                         Marble(pos=90, is_save=True, start_pos=90),
                         Marble(pos=91, is_save=True, start_pos=91)],
            list_kennel_pos=[88, 89, 90, 91],
            list_finish_pos=[92, 93, 94, 95],
            start_pos=48
        )
        self.list_player = [player_blue, player_green, player_red, player_yellow]

    def deal_cards(self) -> None:  # Kägi
        # Check if all players are out of cards.
        for player in self.list_player:
            if not player.list_card:
                continue
            else:
                print(f"{player.name} has still {len(player.list_card)} card's")
                return

        # Go to next Gameround
        self.cnt_round += 1

        # get number of Cards
        cards_per_round = [6, 5, 4, 3, 2]
        num_cards = cards_per_round[(self.cnt_round - 1) % len(cards_per_round)]

        # Check if there are enough cards in the draw deck; if not, add a new card deck.
        if num_cards * 4 > len(self.list_card_draw):
            # reshuffle the Deck
            self.list_card_draw = GameState.LIST_CARD
            self.list_card_discard = []

        # Randomly select cards for players.
        for player in self.list_player:
            player.list_card = random.sample(self.list_card_draw, num_cards)
            for card in player.list_card:
                self.list_card_draw.remove(card)

        # Set Cardexchange
        self.bool_card_exchanged = False

    def can_marble_leave_kennel(self, player: PlayerState) -> int:
        for marble in player.list_marble:
            if int(marble.pos) not in player.list_kennel_pos:
                if not int(marble.pos) == player.start_pos and marble.is_save:
                    return None
                return None
        return marble.pos

    def get_list_possible_action(self) -> List[Action]:  # Nicolas
        list_steps_split_7 = [
            [1, 1, 1, 1, 1, 1, 1],
            [2, 1, 1, 1, 1, 1],
            [2, 2, 1, 1, 1],
            [2, 2, 2, 1],
            [3, 1, 1, 1, 1],
            [3, 2, 1, 1],
            [3, 2, 2],
            [3, 3, 1],
            [4, 1, 1, 1],
            [4, 2, 1],
            [4, 3],
            [5, 2],
            [6, 1],
        ]
        active_player = self.list_player[self.idx_player_active]
        cards = active_player.list_card
        if not cards:
            return []

        marbles = active_player.list_marble
        oponent_players = [oponent for oponent in self.list_player if oponent.name != active_player.name]
        action_list = []


        #  Todo Home Check
        leaving_marble = None
        for marble in marbles:
            if marble.pos in active_player.list_kennel_pos:
                if leaving_marble is None:
                    for card in cards:
                        match card.rank:
                            case 'K':
                                leaving_marble = marble
                                action_list.append(Action(card=card, pos_from=marble.pos, pos_to=active_player.start_pos, card_swap=None))
                            case 'A':
                                leaving_marble = marble
                                action_list.append(Action(card=card, pos_from=marble.pos, pos_to=active_player.start_pos, card_swap=None))
                            case 'JKR':
                                leaving_marble = marble
                                action_list.append(Action(card=card, pos_from=marble.pos, pos_to=active_player.start_pos, card_swap=None))
                            case _:
                                pass
            else:
                for card in cards:
                    match card.rank:
                        case '2':
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 2) % 64, card_swap=None))
                        case '3':
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 3) % 64, card_swap=None))
                        case '4':
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 4) % 64, card_swap=None))
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos - 4) % 64, card_swap=None))
                        case '5':
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 5) % 64, card_swap=None))
                        case '6':
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 6) % 64, card_swap=None))
                        case '7':
                            for steps_split in list_steps_split_7:
                                for i, steps in enumerate(steps_split):
                                    action_list.append(Action(card=card, pos_from=marble.pos,
                                                              pos_to=(marble.pos + steps) % 64, card_swap=None))
                        case '8':
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 8) % 64, card_swap=None))
                        case '9':
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 9) % 64, card_swap=None))
                        case '10':
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 10) % 64, card_swap=None))
                        case 'J':
                            for oponent_player in oponent_players:
                                for oponent_marble in oponent_player.list_marble:
                                    if not oponent_marble.is_save: 
                                        action_list.append(Action(card = card,pos_from = marble.pos,
                                                                  pos_to = oponent_marble.pos, card_swap = None))
                        case 'Q':
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 12) % 64, card_swap=None))
                        case 'K':
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 13) % 64, card_swap=None))
                        case 'A':
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 11) % 64, card_swap=None))
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 1) % 64, card_swap=None))
                        case 'JKR':
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 2) % 64, card_swap=None))
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 3) % 64, card_swap=None))
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 4) % 64, card_swap=None))
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos - 4) % 64, card_swap=None))
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 5) % 64, card_swap=None))
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 6) % 64, card_swap=None))
                            for steps_split in list_steps_split_7:
                                for i, steps in enumerate(steps_split):
                                    action_list.append(Action(card=card, pos_from=marble.pos,
                                                              pos_to=(marble.pos + steps) % 64, card_swap=None))
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 8) % 64, card_swap=None))
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 9) % 64, card_swap=None))
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 10) % 64, card_swap=None))
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 12) % 64, card_swap=None))
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 13) % 64, card_swap=None))
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 11) % 64, card_swap=None))
                            action_list.append(
                                Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 1) % 64, card_swap=None))
                            for oponent_player in oponent_players:
                                for oponent_marble in oponent_player.list_marble:
                                    if not oponent_marble.is_save: 
                                        action_list.append(Action(card = card,pos_from = marble.pos,
                                                                  pos_to = oponent_marble.pos, card_swap = None))
                        case _:
                            pass

            # ist ausführbar?
            # for action in action_list:
            # fun1 (action, marble)
            # fun2
        return action_list

    def set_action_to_game(self, action: Action):  # Kened
        # Get the active player
        active_player = self.list_player[self.idx_player_active]

        #FIXME: It is a Game! Dont raise errors ==> Errors will break the Game!
        #FIXME: Set me in test_dog.py
        # # Ensure the card played is in the player's hand
        # if action.card not in active_player.list_card:
        #     raise ValueError("The card played is not in the active player's hand.")
        #FIXME: Set me in test_dog.py
        # # Ensure pos_from and pos_to are defined
        # if action.pos_from is None or action.pos_to is None:
        #     raise ValueError("Both pos_from and pos_to must be specified for the action.")

        # Find the marble to move based on pos_from 
        marble_to_move = next((m for m in active_player.list_marble if m.pos == str(action.pos_from)), None) # FIXME: Is not working for going out

        #FIXME: Set me in test_dog.py
        # if not marble_to_move:
        #     raise ValueError(f"No marble found at the specified pos_from: {action.pos_from}")

        # Update the marble's position
        marble_to_move.pos = str(action.pos_to)

        # Check if the marble's new position is in a final or safe zone
        self.check_final_pos(pos_to=action.pos_to, pos_from=action.pos_from, marble=marble_to_move)

        # Handle cases where another player's marble occupies the destination
        for player in self.list_player:
            if player != active_player:
                opponent_marble = next((m for m in player.list_marble if m.pos == str(action.pos_to)), None)
                if opponent_marble:
                    self.sending_home(opponent_marble)  # Send the opponent's marble home
        # Discard the played card
        active_player.list_card.remove(action.card)
        self.list_card_discard.append(action.card)

        # Handle special cards
        if action.card.rank == '7':
            # 7 allows multiple movements; the game logic should track additional actions
            self.card_active = action.card
        elif action.card.rank == 'J':
            # J allows swapping marbles (specific logic to be implemented separately)
            pass
        elif action.card.rank == 'JKR':
            # Joker allows flexibility, which may require additional rules
            pass
        else:
            # Reset the active card for regular actions
            self.card_active = None

    def can_leave_kennel(self) -> bool:  # <============= DOPPELT
        if self.card_active is None:
            return False

        if self.card_active.rank in ["A", "K", "JKR"]:
            return True
        return False

    def check_final_pos(self, pos_to: int, pos_from: int, action: Action, marble: Marble) -> None:
        """
        Check whether the final position of the marble is a special position.
        1) The marble is save if it is in one of the four final spots of its color or
        2) if it is newly out of the kennel.
        """
        final_positions: list = [68, 69, 70, 71, 76, 77, 78, 79, 84, 85, 86, 87, 92, 93, 94, 95]
        if action.pos_to in final_positions:
            marble.is_save = True

        last_positions: list = [64, 65, 66, 67, 72, 73, 74, 75, 80, 81, 82, 83, 88, 89, 90, 91]
        if action.pos_from in last_positions:
            marble.is_save = True


    def exchange_cards(self, action_cardswap: Action) -> None:
        # Part Kägi

        # Save selected Card
        self.list_swap_card[self.idx_player_active] = action_cardswap.card
        self.list_player[self.idx_player_active].list_card.remove(action_cardswap.card)

        # Check iff all Player selected a Card, Return if not
        if None in self.list_swap_card:
            return
        
        # Swap Cards with teammember
        for i, player in enumerate(self.list_player):
            opposite_player_index = (i + 2) % 4  # Index des Teammitglieds
            player.list_card.append(self.list_swap_card[opposite_player_index])
        
        # Set global Variables
        self.bool_card_exchanged = True
        self.list_swap_card = [None]*4

        return

        ## ----------- Part Renato -----------
        # player_blue = self.list_player[0]
        # player_red = self.list_player[2]

        # print(f"\n{player_blue.name}, bitte wähle eine Karte zum Tauschen aus:")
        # for idx, card in enumerate(player_blue.list_card):
        #     print(f"{idx + 1}: {card}")

        # blue_choice = int(input("Gib die Nummer der Karte ein, die du tauschen möchtest: ")) - 1
        # card_blue = player_blue.list_card[blue_choice]

        # print(f"\n{player_red.name}, bitte wähle eine Karte zum Tauschen aus:")
        # for idx, card in enumerate(player_red.list_card):
        #     print(f"{idx + 1}: {card}")

        # red_choice = int(input("Gib die Nummer der Karte ein, die du tauschen möchtest: ")) - 1
        # card_red = player_red.list_card[red_choice]

        # player_blue.list_card.remove(card_blue)
        # player_red.list_card.remove(card_red)

        # player_blue.list_card.append(card_red)
        # player_red.list_card.append(card_blue)

        # print(f"{player_blue.name} tauscht {card_blue} mit {player_red.name} für {card_red}")

        # player_yellow = self.list_player[3]
        # player_green = self.list_player[1]

        # print(f"\n{player_yellow.name}, bitte wähle eine Karte zum Tauschen aus:")
        # for idx, card in enumerate(player_yellow.list_card):
        #     print(f"{idx + 1}: {card}")

        # yellow_choice = int(input("Gib die Nummer der Karte ein, die du tauschen möchtest: ")) - 1
        # card_yellow = player_yellow.list_card[yellow_choice]

        # print(f"\n{player_green.name}, bitte wähle eine Karte zum Tauschen aus:")
        # for idx, card in enumerate(player_green.list_card):
        #     print(f"{idx + 1}: {card}")

        # green_choice = int(input("Gib die Nummer der Karte ein, die du tauschen möchtest: ")) - 1
        # card_green = player_green.list_card[green_choice]

        # player_yellow.list_card.remove(card_yellow)
        # player_green.list_card.remove(card_green)

        # player_yellow.list_card.append(card_green)
        # player_green.list_card.append(card_yellow)

        # print(f"{player_yellow.name} tauscht {card_yellow} mit {player_green.name} für {card_green}")


    def discard_invalid_cards(self) -> None:
        # check if player has cards
        if not self.list_player[self.idx_player_active].list_card:
            return
        # discard the player
        self.list_card_discard.extend(self.list_player[self.idx_player_active].list_card)
        self.list_player[self.idx_player_active].list_card = []

    def sending_home(self, marble: Marble, card: Card, action: Action) -> bool:
        # First case: A marble of another player lands exactly on the position of my marble
        for current_player in self.list_player:
            for opponent_marble in current_player.list_marble:
                if opponent_marble.pos == marble.pos and opponent_marble != marble:
                    marble.pos = marble.start_pos
                    marble.is_save = True
                    return True

        # Second case: My marble gets jumped over by a marble with a 7-card
        if action and action.pos_from is not None and action.pos_to is not None:
            if action.pos_from < marble.pos < action.pos_to:
                marble.pos = marble.start_pos
                marble.is_save = True
                return True
        return False

    def marble_switch_jake(self, player_idx: int, opponent_idx: int, player_marble_pos: int,
                           opponent_marble_pos: int):  # Kened
        """
        Handle the marble switch action when the Jake card is played.

        Args:
            player_idx (int): Index of the active player (initiator of the swap).
            opponent_idx (int): Index of the opponent player (target of the swap).
            player_marble_pos (int): Position of the active player's marble to swap.
            opponent_marble_pos (int): Position of the opponent's marble to swap.

        Raises:
            ValueError: If the specified positions do not match any marbles or if the swap is invalid.
        """
        # Get the players
        active_player = self.list_player[player_idx]
        opponent_player = self.list_player[opponent_idx]

        # Find the marbles to swap
        player_marble = next((m for m in active_player.list_marble if m.pos == str(player_marble_pos)), None)
        opponent_marble = next((m for m in opponent_player.list_marble if m.pos == str(opponent_marble_pos)), None)

        # Validate the selected marbles
        if not player_marble:
            raise ValueError(f"No marble found at position {player_marble_pos} for the active player.")
        if not opponent_marble:
            raise ValueError(f"No marble found at position {opponent_marble_pos} for the opponent player.")

        # Perform the swap
        player_marble.pos, opponent_marble.pos = opponent_marble.pos, player_marble.pos

        # Log the swap
        print(
            f"Swapped active player's marble from {player_marble_pos} with opponent's marble at {opponent_marble_pos}.")

        # Mark marbles as no longer in a safe state if applicable
        player_marble.is_save = False
        opponent_marble.is_save = False

    def is_player_finished(self, player: PlayerState) -> bool:
        if not player.list_marble:  # Falls der Spieler keine Murmeln hat
            print(f"{player.name} hat keine Murmeln.")
            return False

        # Überprüfen, ob alle Murmeln des Spielers im Zielbereich sind
        finished = all(marble.pos in player.list_finish_pos for marble in player.list_marble)

        if finished:
            print(f"{player.name} hat alle Murmeln im Ziel und ist fertig!")
        else:
            print(f"{player.name} hat noch nicht alle Murmeln im Ziel.")

        return finished

    def check_game_end(self) -> bool:
        finished_players = 0
        for player in self.state.list_player:
            if self.is_player_finished(player):
                finished_players += 1

        if finished_players >= 2:
            self.state.phase = GamePhase.FINISHED  # Setzt den Status auf 'finished', wenn 2 Spieler fertig sind
            print("Spiel ist zu Ende!")
            return True

        return False


    def init_next_turn(self) -> None: # Kägi
        # Start with the next player
        idx_next_player = (self.idx_player_active +1) %4

        # Loop through players until a player with cards is found or the cycle returns to the active player
        while not self.list_player[idx_next_player].list_card and idx_next_player != self.idx_player_active:
            idx_next_player = (idx_next_player + 1)%4
            
        # Check if a player with cards was found
        if self.list_player[idx_next_player].list_card:
            self.idx_player_active = idx_next_player

        else: #All players are out of cards
            # Move to the next start player
            self.deal_cards()
            self.idx_player_started = (self.idx_player_active +1) %4
            self.idx_player_active = self.idx_player_started


class Dog(Game):

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """
        # print("Starting up DOG")
        self.state = GameState()
        self.state.setup_players()
        self.state.phase = GamePhase.RUNNING
        self.state.deal_cards()  # deal first cards to players

    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        self.state = state

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        return self.state

    def print_state(self) -> None:
        """ Print the current game state """
        print(self.state)
        pass

    def get_list_action(self) -> List[Action]:
        """ Get a list of possible actions for the active player """
        # Swap Card Actions
        if self.state.bool_card_exchanged is False:
            action_list = [Action(card=hand_card,pos_from=None, pos_to=None) for hand_card in self.state.list_player[self.state.idx_player_active].list_card]
            return action_list
        
        # get possible Actions
        action_list = self.state.get_list_possible_action()

        if not action_list:
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
                            actions.append(Action(
                                card=card,
                                pos_from=64,
                                pos_to=0,
                                card_swap=None
                            ))
            return actions
        
        return action_list

    def apply_action(self, action: Action) -> None:
        """
        Apply the given action to the game state.
        Moves the marble from pos_from to pos_to based on the action,
        and handles special cases like sending marbles home and marking marbles as safe.
        Apply the given action to the game
        Aktion auf das spielbrett übertragen ==> Gamestate verändern
        Logiken:
        1.1 Normaler Zug von ausgangspos zu zielpos gilt für alle karte ausser JKR, 7 und Jack
        1.2 7 spezialkarte welche 7 x einen schritt machen kann
        1.3 Jack tauscht zwei kugeln miteinander NOTE: Muss eine davon eine eigene Kugel sein?
        1.4 JKR kann alle logiken von 1 bis und mit 3 aufweisen NOTE: Idee für umsetzung?

        2. Wenn Zug abgeschlossen Aktiver spieler weitergeben
        """
        # Check if exchange cards is needed
        if action is None:
            # Move to next player
            self.state.idx_player_active = (self.state.idx_player_active + 1) % 4

            # If we've gone through all players
            if self.state.idx_player_active == self.state.idx_player_started:
                # Move to next round
                self.state.cnt_round += 1
                self.state.idx_player_started = (self.state.idx_player_started + 1) % 4
                self.state.bool_card_exchanged = False

                # Determine the number of cards to deal based on the current round
                if 1 <= self.state.cnt_round <= 5:
                    cards_per_player = 7 - self.state.cnt_round  # 6,5,4,3,2
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
                self.state.idx_player_active = (self.state.idx_player_started + 1) % 4

    def get_player_view(self, idx_player: int) -> GameState:
        """Returns the masked game state for the other players."""
        masked_state = copy.deepcopy(self.state) # Start with the full state

        # Mask the cards of the other players.
        for i in range(4):
            if i != idx_player:
                masked_state.list_player[i].list_card = [Card(suit="", rank="X")] * len(
                    masked_state.list_player[i].list_card)
        return masked_state

class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == '__main__':
    idx_player_you = 0
    game = Dog()
    player = RandomPlayer()
    debug_counter = 0

    while True:

        state = game.get_state()
        if state.phase == GamePhase.FINISHED:
            break

        # game.print_state()

        if state.idx_player_active == idx_player_you:

            player_state = game.get_player_view(idx_player_you)
            list_action = game.get_list_action()
            dict_state = player_state.model_dump()  # <=== Method of BaseModel !!
            dict_state['idx_player_you'] = idx_player_you
            dict_state['list_action'] = [action.model_dump() for action in list_action]
            data = {'type': 'update', 'state': dict_state}
            # await websocket.send_json(data)
            #print(data)

            if len(list_action) == 0:
                game.state.discard_invalid_cards()
                continue
                
            else:
                action = random.choice(list_action)  # data =
                # data = await websocket.receive_json()
                if isinstance(action, Action):
                    # action = Dog.model_validate(data['action']) # Checks if Action is Valid (only Valid aktion for
                    # our game?
                    game.apply_action(action)
                    print(action)

            state = game.get_player_view(idx_player_you)
            dict_state = state.model_dump()
            dict_state['idx_player_you'] = idx_player_you
            dict_state['list_action'] = []

            data = {'type': 'update', 'state': dict_state}
            # print(data)
            # await websocket.send_json(data)

        else:
            list_action = game.get_list_action()
            if not list_action:
                game.state.discard_invalid_cards()
                continue

            action = player.select_action(game.state, list_action)
            if action is not None:
                print(f"Player {game.state.idx_player_active} is playing")
                # await asyncio.sleep(1)
                print(action)
            game.apply_action(action)
            player_state = game.get_player_view(idx_player_you)  # Abbildung für Person zeigen
            dict_state = player_state.model_dump()
            dict_state['idx_player_you'] = idx_player_you
            dict_state['list_action'] = []
            data = {'type': 'update', 'state': dict_state}
            # print(data)
            # await websocket.send_json(data)
        
        print("old Player Active: ", game.state.idx_player_active)
        game.state.init_next_turn()
        print("New Player Active: ", game.state.idx_player_active)
        print("Exchanged? ",game.state.bool_card_exchanged)
        print("*"*50)


        if debug_counter >4:
            print("-"*50,"> break becaus of counter")
            break
        debug_counter+=1
