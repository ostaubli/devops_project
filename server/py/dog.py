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
    played_seven_actions: List[Action] = []


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
        for selected_player in self.list_player:
            if not selected_player.list_card:
                continue
            else:
                print(f"{selected_player.name} has still {len(selected_player.list_card)} card's")
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

    def discard_invalid_cards(self) -> None:
        # check if player has cards
        if not self.list_player[self.idx_player_active].list_card:
            return
        # discard the player
        self.list_card_discard.extend(self.list_player[self.idx_player_active].list_card)
        self.list_player[self.idx_player_active].list_card = []


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
            [7]
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
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 2) % 64, card_swap=None)
                            action_list.append(action)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)

                        case '3':
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 3) % 64, card_swap=None)
                            action_list.append(action)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                        case '4':
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 4) % 64, card_swap=None)
                            action_list.append(action)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos -4) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                        case '5':
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +5) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                        case '6':
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +6) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                        case '7':
                            for steps_split in list_steps_split_7:
                                for i, steps in enumerate(steps_split):
                                    action = Action(card=card, pos_from=marble.pos,
                                                              pos_to=(marble.pos + steps) % 64, card_swap=None)
                                    going_final_action_list = self.go_in_final(action)
                                    if going_final_action_list:
                                        action_list.extend(going_final_action_list)
                        case '8':
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +8) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                        case '9':
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +9) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                        case '10':
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +10) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                        case 'J':
                            for oponent_player in oponent_players:
                                for oponent_marble in oponent_player.list_marble:
                                    if not oponent_marble.is_save: 
                                        action_list.append(Action(card = card,pos_from = marble.pos,
                                                                  pos_to = oponent_marble.pos, card_swap = None))
                        case 'Q':
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +12) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                        case 'K':
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +13) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                        case 'A':
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +1) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +11) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)

                        case 'JKR':
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +2) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +3) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +4) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos -4) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +5) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +6) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +8) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +9) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +10) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +1) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +11) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +12) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)
                            action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos +13) % 64,
                                            card_swap=None)
                            going_final_action_list = self.go_in_final(action)
                            if going_final_action_list:
                                action_list.extend(going_final_action_list)

                            for steps_split in list_steps_split_7:
                                for i, steps in enumerate(steps_split):
                                    action = Action(card=card, pos_from=marble.pos,
                                                    pos_to=(marble.pos + steps) % 64, card_swap=None)
                                    going_final_action_list = self.go_in_final(action)
                                    if going_final_action_list:
                                        action_list.extend(going_final_action_list)

                            for oponent_player in oponent_players:
                                for oponent_marble in oponent_player.list_marble:
                                    if not oponent_marble.is_save: 
                                        action_list.append(Action(card = card,pos_from = marble.pos,
                                                                  pos_to = oponent_marble.pos, card_swap = None))
                        case _:
                            pass

        return action_list

    def set_action_to_game(self, action: Action):  # kaegi
        # Action is from the active Player
        # Set Action to the GameState ==> make movement on the "board"
        marble_to_move = next((marble for marble in self.list_player[self.idx_player_active].list_marble if marble.pos == action.pos_from), None)

        # Check if marble comes from kenel
        if marble_to_move.pos == marble_to_move.start_pos:
            marble_to_move.is_save = True

        # Goes in final
        elif action.pos_to > 63:
            marble_to_move.is_save = True
        # Set Action pos to game
        marble_to_move.pos = action.pos_to

        # Send marble on same pos home
        self.sending_home(marble_to_move)
        return

    def exchange_cards(self, action_cardswap: Action) -> None:

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

    def sending_home(self, moved_marble: Marble) -> None:
        """
        Checks if the active marble jumps on another marble. 
        If so, sends the other marble back to its start position.
        """
        for selected_player in self.list_player:
            for p_marble in selected_player.list_marble:
                # Check if the marble occupies the same position but isn't the same marble
                if p_marble.pos == moved_marble.pos and p_marble != moved_marble:
                    p_marble.pos = p_marble.start_pos


    def skip_save_marble(self, action: Action) -> bool:
        """
        Prüft, ob zwischen action.pos_from und action.pos_to sichere Murmeln liegen.
        Gibt False zurück, wenn eine sichere Murmel in diesem Bereich gefunden wird,
        andernfalls True.
        """
        for player in self.list_player:
            for marble in player.list_marble:
                if action.pos_from < marble.pos < action.pos_to and marble.is_save:
                    return False
        return True

    def is_player_finished(self, player: PlayerState) -> bool:
        for marble in player.list_marble:
            if marble.pos not in player.list_finish_pos:
                return False
        return True

    def check_game_end(self) -> None:
        team1 = [self.list_player[0], self.list_player[2]]
        team2 = [self.list_player[1], self.list_player[3]]

        for team in [team1, team2]:
            team_finished = all(self.is_player_finished(player) for player in team)
            if team_finished:
                self.phase = GamePhase.FINISHED
                return

    def go_in_final(self, action_to_check: Action) -> List[Action]:
        """
        Checks if it is possible to go in the final
        Yes, creat the Actions fo that + unchanged action
        No, return Action unchanged
        """
        # Get infos from Gamestate
        active_player = self.list_player[self.idx_player_active]
        final_pos = active_player.list_marble[-1].start_pos+1

        # get positions
        startpos = active_player.start_pos
        pos_from = action_to_check.pos_from
        pos_to = action_to_check.pos_to

        # Calculate the movement for go Final
        if startpos > 0 or pos_from > pos_to:
            steps = pos_to - pos_from
            stepps_to_final = startpos-pos_from
            overlap = abs(abs(steps) - abs(stepps_to_final))
        else:
            steps = 64-pos_to-pos_from
            stepps_to_final = startpos-pos_from
            overlap = abs(abs(steps) - abs(stepps_to_final))

        # when the reminderstps after start are between 1&4 go in final
        if abs(overlap) <5:
            set_pos_to = final_pos + abs(overlap)-1
            new_action = Action(card=action_to_check.card,
                                pos_from=action_to_check.pos_from,
                                pos_to=set_pos_to,
                                card_swap=action_to_check.card_swap)
            return [action_to_check, new_action]

        # If not possible to go in final return given action
        return [action_to_check]

    def init_next_turn(self) -> None:
        """
        Sets the next player with cards to active.
        if there are all cards played it deals new cards
        """

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
        current_player_name = self.state.list_player[self.state.idx_player_active].name

        player_data = {
            player.name: {
                "positions": [marble.pos for marble in player.list_marble],
                "cards": len(player.list_card),
            }
            for player in self.state.list_player
        }
        print(f"We are in round {self.state.cnt_round} and the current player is {current_player_name}")
        for player_name, data in player_data.items():
            print(f"Player {player_name} has positions: {data['positions']} and holds {data['cards']} cards")
        print(f"The actual game phase: {self.state.phase}")

    def get_list_action(self) -> List[Action]:
        """ Get a list of possible actions for the active player """
        # Swap Card Actions
        if self.state.bool_card_exchanged is False:
            action_list = [Action(card=hand_card,pos_from=None, pos_to=None) for hand_card in self.state.list_player[self.state.idx_player_active].list_card]
            return action_list
        
        if self.state.card_active is None:
            action_list = self.state.get_list_possible_action()

        if self.state.card_active.rank == '7':
            played_seven_actions = []




        return action_list

        # else: Logic for card 7

    def apply_action(self, action: Action) -> None:
        """
        Do the movement conected to the Action
        """
        if action is None: # If player can not play any actions
            self.state.discard_invalid_cards()

        # Check if exchange cards is needed
        elif self.state.bool_card_exchanged is False:
            self.state.exchange_cards(action)

        elif action:
            self.state.set_action_to_game(action)

            # Removed played Card from Players Hand
            self.state.list_card_discard.append(action.card)
            self.state.list_player[self.state.idx_player_active].list_card.remove(action.card)

        # Sets the next Player active if there is not a Card active
        if self.state.card_active is None:
            self.state.init_next_turn()

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
        if actions and len(actions) > 0: 
            return random.choice(actions)
        return None


if __name__ == '__main__':
    print("*"*30, "- START GAME -", "*"*30)

    idx_player_you = 0
    game = Dog()
    player = RandomPlayer()
    debug_counter = 0

    while True:

        state = game.get_state()
        if state.phase == GamePhase.FINISHED:
            break

        print("Is Player Active?: ", game.state.idx_player_active)
        print("Number of Cards: ", len(game.state.list_player[game.state.idx_player_active].list_card))

        # game.print_state()

        if state.idx_player_active == idx_player_you:

            player_state = game.get_player_view(idx_player_you)
            list_action = game.get_list_action()
            
            # await websocket.send_json(data)
            #print(data)

            if list_action is not None:
                print("You are playing")

                dict_state = player_state.model_dump()  # <=== Method of BaseModel !!
                dict_state['idx_player_you'] = idx_player_you
                dict_state['list_action'] = [action.model_dump() for action in list_action]
                data = {'type': 'update', 'state': dict_state}

            else: # if not: delet all cards for this round
                print("You don't have any possible Actions")

            # FIXME: Needs to get Choos from Server (real Player)
            action = player.select_action(game.state, list_action)  # Random Select an Action for debug
            
            print(f"Action from Player{state.idx_player_active} is",action)
            # Apply Action to Game
            game.apply_action(action)

            state = game.get_player_view(idx_player_you)
            dict_state = state.model_dump()
            dict_state['idx_player_you'] = idx_player_you
            dict_state['list_action'] = []

            data = {'type': 'update', 'state': dict_state}
            # print(data)
            # await websocket.send_json(data)

        else:

            list_action = game.get_list_action()
            action = player.select_action(game.state, list_action)  # Random Select an Action

            # If there are possible actions, choose one
            if action is not None:
                print(f"Player {game.state.idx_player_active} is playing")
                # await asyncio.sleep(1)
                print(f"Action from Player{state.idx_player_active} is",action)
            else:# if not: delet all cards for this round
                print(f"Player {game.state.idx_player_active} has no possible actions.")

            # Apply Action to Game
            game.apply_action(action)

            player_state = game.get_player_view(idx_player_you)  # Abbildung für Person zeigen
            dict_state = player_state.model_dump()
            dict_state['idx_player_you'] = idx_player_you
            dict_state['list_action'] = []
            data = {'type': 'update', 'state': dict_state}
            # print(data)
            # await websocket.send_json(data)

        print("Exchanged? ",game.state.bool_card_exchanged)
        print("Speciality? card_active? ", game.state.card_active)
        print("*"*50)


        # Keeps game away from infinityloop
        if debug_counter >30:
            print("-"*50,"> break becaus of counter")
            break
        debug_counter+=1
