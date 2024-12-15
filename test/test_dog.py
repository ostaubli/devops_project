from token import EQUAL

import pytest
import random

from Demos.SystemParametersInfo import new_h
from numpy.ma.testutils import assert_not_equal
from pyparsing import NotAny

from pydantic import BaseModel
from typing import List, Optional, Dict

if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.getcwd())

from server.py.dog import Card, Marble, PlayerState, Action, GameState, GamePhase, Dog
from server.py.game import Player


class TestKaegisDogParts:

    def test_setup_players(self) -> None:
        game = Dog()

        # Call the setup_players method
        game.state.setup_players()

        # Retrieve the players
        players = game.state.list_player
        assert len(players) == 4, "There should be 4 players set up"

        # Verify properties for each player
        for idx, player in enumerate(players):
            # Check player names
            expected_names = ["PlayerBlue", "PlayerGreen", "PlayerRed", "PlayerYellow"]
            assert player.name == expected_names[idx], f"Player {idx} should be named {expected_names[idx]}"

            # Check the number of marbles
            assert len(player.list_marble) == 4, f"Player {player.name} should have 4 marbles"

            # Check if marbles are in the correct kennel positions
            for marble, kennel_pos in zip(player.list_marble, player.list_kennel_pos):
                assert marble.pos == kennel_pos, f"Player {player.name} has a marble not in its kennel position"

            # Check if all marbles are safe
            assert all(marble.is_save for marble in
                       player.list_marble), f"All marbles of {player.name} should be marked as safe"

            # Check finish positions
            expected_finish_counts = [4, 4, 4, 4]
            assert len(player.list_finish_pos) == expected_finish_counts[
                idx], f"Player {player.name} should have 4 finish positions"

        print("Completed Test setup_players")

    def test_deal_cards(self) -> None:
        game = Dog()

        state = game.get_state()
        assert state.cnt_round == 1, "First Round"

        for player in state.list_player:
            assert len(player.list_card) == 6, "Should be 6 Cards for each player in firs Round"
            player.list_card = []

        game.state.deal_cards()
        state = game.get_state()
        assert state.cnt_round == 2, "2 Round"
        for player in state.list_player:
            assert len(player.list_card) == 5, "Should be 5 Cards for each player in 2 Round"
            player.list_card = []

        game.state.deal_cards()
        state = game.get_state()
        assert state.cnt_round == 3, "3 Round"
        for player in state.list_player:
            assert len(player.list_card) == 4, "Should be 4 Cards for each player in 3 Round"
            player.list_card = []

        game.state.deal_cards()
        state = game.get_state()
        assert state.cnt_round == 4, "4 Round"
        for player in state.list_player:
            assert len(player.list_card) == 3, "Should be 3 Cards for each player in 4 Round"
            player.list_card = []

        game.state.deal_cards()
        state = game.get_state()
        assert state.cnt_round == 5, "5 Round"
        for player in state.list_player:
            assert len(player.list_card) == 2, "Should be 2 Cards for each player in 5 Round"
            player.list_card = []

        game.state.deal_cards()
        state = game.get_state()
        assert state.cnt_round == 6, "6 Round"
        for player in state.list_player:
            assert len(player.list_card) == 6, "Should be 6 Cards for each player in 6 Round"
            player.list_card = []

        print("Compleeted Test deal_cards")

    def test_init_next_turn(self) -> None:
        game = Dog()

        # Initial state
        state = game.get_state()
        state.idx_player_active = 0
        assert state.idx_player_active == 0, "Initial active player should be player 0"
        assert all(
            len(player.list_card) == 6 for player in state.list_player), "All players should have 6 cards at the start"

        # Simulate a turn where player 0 has no cards
        state.list_player[0].list_card = []
        game.state.init_next_turn()
        state = game.get_state()
        assert state.idx_player_active == 1, "Active player should move to player 1"

        # Simulate turns where multiple players have no cards
        state.list_player[1].list_card = []
        state.list_player[2].list_card = []
        game.state.init_next_turn()
        state = game.get_state()
        assert state.idx_player_active == 3, "Active player should move to player 3"

        # Simulate all players running out of cards
        for player in state.list_player:
            player.list_card = []

        game.state.init_next_turn()
        state = game.get_state()
        assert state.idx_player_active == 0, "Active player should loop back to player 0 after dealing cards"
        assert all(
            len(player.list_card) > 0 for player in state.list_player), "New cards should be dealt to all players"

        print("Completed Test init_next_turn")

    def test_exchange_cards(self) -> None:

        # Initial game setup
        game = Dog()
        state = game.get_state()
        state.bool_card_exchanged = False
        state.list_swap_card = [None]*4
        check_swaped_cards = []

        # Simulate card exchange for all players
        for player_idx in range(4):
            state.idx_player_active = player_idx
            action_list = game.get_list_action()
            assert all(action.card in state.list_player[state.idx_player_active].list_card for action in action_list), f"During the exchange, only cards in Player {player_idx + 1}'s hand should be returned as actions"

            select_action = random.choice(action_list)
            game.apply_action(select_action)
            check_swaped_cards.append(select_action.card)

            if not state.bool_card_exchanged:
                assert state.list_swap_card.count(None) == (3-player_idx), "The exchangecard is not stored"

        # Check if cards are correctly swapped
        state = game.get_state()
        assert state.bool_card_exchanged is True, "Cards should have been exchanged after all selections"

        # Verify the correct exchange of cards between team members
        for i in range(4):
            opposite_player_index = (i + 2) % 4
            assert check_swaped_cards[i] in state.list_player[opposite_player_index].list_card, f"Player {i} should have the card from their team member Player {opposite_player_index}"

        # Reset for next round
        assert all(card is None for card in state.list_swap_card), "Card swap list should be reset after the exchange"

    def test_discard_invalid_cards(self)->None:
        # Initial game setup
        game = Dog()
        state = game.get_state()
        state.idx_player_active = 0
        state.list_card_discard = []
        to_del_cards = state.list_player[state.idx_player_active].list_card
        state.discard_invalid_cards()
        assert not state.list_player[state.idx_player_active].list_card, "The players Handcard should be empty"
        assert all(card in state.list_card_discard for card in to_del_cards), "all the players Handcards should be in the list_card_discard deck"

    def test_go_in_final(self) ->None:
        game = Dog()
        state = game.get_state()


        # Test Player1
        state.idx_player_active = 0
        action1 = Action(card=state.LIST_CARD[10], pos_from=61, pos_to= 3, card_swap=None)
        action_list = state.go_in_final(action1)
        assert len(action_list) == 2, "it is possible to go in final"
        action_list.remove(action1)
        assert action_list[0].pos_to == 70, "should be in final pos 70"

        action1 = Action(card=state.LIST_CARD[10], pos_from=2, pos_to= 62, card_swap=None)
        action_list = state.go_in_final(action1)
        assert len(action_list) == 2, "it is possible to go in final"
        action_list.remove(action1)
        assert action_list[0].pos_to == 69, "should be in final pos 69"

        action1 = Action(card=state.LIST_CARD[10], pos_from=61, pos_to= 6, card_swap=None)
        action_list = state.go_in_final(action1)
        assert len(action_list) == 1, "it is not possible to go in final"


        # Test Player2
        state.idx_player_active = 1
        action1 = Action(card=state.LIST_CARD[10], pos_from=13, pos_to= 19, card_swap=None)
        action_list = state.go_in_final(action1)
        assert len(action_list) == 2, "it is possible to go in final"
        action_list.remove(action1)
        assert action_list[0].pos_to == 78, "should be in final pos 78"

        action1 = Action(card=state.LIST_CARD[10], pos_from=18, pos_to= 14, card_swap=None)
        action_list = state.go_in_final(action1)
        assert len(action_list) == 2, "it is possible to go in final"
        action_list.remove(action1)
        assert action_list[0].pos_to == 77, "should be in final pos 77"

        action1 = Action(card=state.LIST_CARD[10], pos_from=13, pos_to= 22, card_swap=None)
        action_list = state.go_in_final(action1)
        assert len(action_list) == 1, "it is not possible to go in final"


        # Test Player3
        state.idx_player_active = 2
        action1 = Action(card=state.LIST_CARD[10], pos_from=29, pos_to= 35, card_swap=None)
        action_list = state.go_in_final(action1)
        assert len(action_list) == 2, "it is possible to go in final"
        action_list.remove(action1)
        assert action_list[0].pos_to == 86, "should be in final pos 86"

        action1 = Action(card=state.LIST_CARD[10], pos_from=34, pos_to= 30, card_swap=None)
        action_list = state.go_in_final(action1)
        assert len(action_list) == 2, "it is possible to go in final"
        action_list.remove(action1)
        assert action_list[0].pos_to == 85, "should be in final pos 85"

        action1 = Action(card=state.LIST_CARD[10], pos_from=29, pos_to=38, card_swap=None)
        action_list = state.go_in_final(action1)
        assert len(action_list) == 1, "it is not possible to go in final"


        # Test Player4
        state.idx_player_active = 3
        action1 = Action(card=state.LIST_CARD[10], pos_from=45, pos_to=51, card_swap=None)
        action_list = state.go_in_final(action1)
        assert len(action_list) == 2, "it is possible to go in final"
        action_list.remove(action1)
        assert action_list[0].pos_to == 94, "should be in final pos 94"

        action1 = Action(card=state.LIST_CARD[10], pos_from=50, pos_to= 46, card_swap=None)
        action_list = state.go_in_final(action1)
        assert len(action_list) == 2, "it is possible to go in final"
        action_list.remove(action1)
        assert action_list[0].pos_to == 93, "should be in final pos 93"

        action1 = Action(card=state.LIST_CARD[10], pos_from=45, pos_to=54, card_swap=None)
        action_list = state.go_in_final(action1)
        assert len(action_list) == 1, "it is not possible to go in final"

    def test_set_action_to_game(self)->None:
        game_state = GameState()
        player1 = PlayerState(
            list_card=[
                Card(suit='♠',rank="2"),
                Card(suit = '♦', rank="A")],
            list_finish_pos=[],
            list_kennel_pos=[64, 65, 66, 67],
            list_marble=[Marble(pos=0, is_save=True, start_pos=64),
                        Marble(pos=38, is_save=True, start_pos=65)],
            name="Player1",
            start_pos=0,
        )
        player2 = PlayerState(
            list_card=[
                Card(suit='♠',rank="2"),
                Card(suit = '♦', rank="A")],
            list_finish_pos=[],
            list_kennel_pos=[72, 73, 74, 75],
            list_marble=[Marble(pos=22, is_save=True, start_pos=72),
                        Marble(pos=35, is_save=True, start_pos=73)],
            name="Player1",
            start_pos=0,
        )
        game_state.list_player = [player1, player2]
        game_state.idx_player_active = 0

        assert game_state.list_player[game_state.idx_player_active].list_marble[0].pos == 0, "Pos 1 marbel Player 0 is 0"
        assert game_state.list_player[game_state.idx_player_active].list_marble[1].pos == 38, "Pos 2 marbel Player 0 is 38"
        assert game_state.list_player[game_state.idx_player_active+1].list_marble[0].pos == 22, "Pos 1 marbel Player 1 is 22"
        assert game_state.list_player[game_state.idx_player_active+1].list_marble[1].pos == 35, "Pos 2 marbel Player 1 is 35"

        action1 = Action(card=Card(suit='♠',rank="2"), pos_from=0, pos_to=13, card_swap=None)
        game_state.set_action_to_game(action1)
        assert game_state.list_player[game_state.idx_player_active].list_marble[0].pos == 13, "Pos 1 marbel Player 0 is 13"
        assert game_state.list_player[game_state.idx_player_active].list_marble[1].pos == 38, "Pos 2 marbel Player 0 is 38"
        assert game_state.list_player[game_state.idx_player_active+1].list_marble[0].pos == 22, "Pos 1 marbel Player 1 is 22"
        assert game_state.list_player[game_state.idx_player_active+1].list_marble[1].pos == 35, "Pos 2 marbel Player 1 is 35"

        game_state.idx_player_active = 1
        action2 = Action(card=Card(suit='♠',rank="2"), pos_from=35, pos_to=38, card_swap=None)
        game_state.set_action_to_game(action2)
        assert game_state.list_player[game_state.idx_player_active].list_marble[1].pos == 38, "Pos 2 marbel Player 1 is 38"
        assert game_state.list_player[game_state.idx_player_active].list_marble[0].pos == 22, "Pos 1 marbel Player 1 is 22"
        assert game_state.list_player[game_state.idx_player_active-1].list_marble[0].pos == 13, "Pos 1 marbel Player 0 is 13"
        assert game_state.list_player[game_state.idx_player_active-1].list_marble[1].pos == 65, "Pos 2 marbel Player 0 is sent home=> Pos 65"
 

class TestGameState:


    def test_sending_home(self) -> None:
        # Arrange
        game_state = GameState()
        player1 = PlayerState(
            list_card=[],
            list_finish_pos=[],
            list_kennel_pos=[],
            list_marble=[],
            name="Player1",
            start_pos=0,
        )
        player2 = PlayerState(
            list_card=[],
            list_finish_pos=[],
            list_kennel_pos=[],
            list_marble=[],
            name="Player2",
            start_pos=0,
        )

        marble1 = Marble(pos=5, start_pos=64, is_save=False)  # Moved marble
        marble2 = Marble(pos=5, start_pos=65, is_save=False)  # Marble at same position
        marble3 = Marble(pos=3, start_pos=72, is_save=False)  # Unaffected marble
        marble4 = Marble(pos=8, start_pos=73, is_save=False)  # Unaffected marble

        player1.list_marble = [marble1, marble3]
        player2.list_marble = [marble2, marble4]
        game_state.list_player = [player1, player2]

        # Act
        game_state.sending_home(marble1)

        # Assert
        assert marble2.pos == marble2.start_pos  # Check marble2 is sent home
        assert marble1.pos == 5  # marble1 remains in its position
        assert marble3.pos == 3  # Unaffected marble stays in place
        assert marble4.pos == 8  # Unaffected marble stays in place


    def test_skip_save_marble(self) -> None:
        # Arrange
        game_state = GameState()

        # Initialisierung der Spieler
        player1 = PlayerState(
            list_card=[],
            list_finish_pos=[],
            list_kennel_pos=[],
            list_marble=[],
            name="Player1",
            start_pos=0,
        )
        player2 = PlayerState(
            list_card=[],
            list_finish_pos=[],
            list_kennel_pos=[],
            list_marble=[],
            name="Player2",
            start_pos=0,
        )

        # Initialisiere Murmeln
        marble1 = Marble(pos=0, start_pos=0, is_save=False)  # Gehört zu player1
        marble2 = Marble(pos=15, start_pos=15, is_save=True)  # Gehört zu player1
        marble3 = Marble(pos=5, start_pos=5, is_save=False)  # Gehört zu player2
        marble4 = Marble(pos=10, start_pos=10, is_save=True)  # Gehört zu player2

        # Füge Murmeln den Spielern hinzu
        player1.list_marble.append(marble1)
        player1.list_marble.append(marble2)
        player2.list_marble.append(marble3)
        player2.list_marble.append(marble4)

        # Füge Spieler zum GameState hinzu
        game_state.list_player.extend([player1, player2])

        # Test 1: Keine Murmel blockiert (bereich 3-8, keine sichere Murmel im Weg)
        card = Card(suit="hearts", rank="5")
        result = game_state.skip_save_marble(Action(pos_from=3, pos_to=8, card=card))
        assert result is True

        # Test 2: Blockiert durch Murmel eines fremden Spielers (marble4, pos=10, is_save=True)
        result = game_state.skip_save_marble(Action(pos_from=8, pos_to=13, card=card))
        assert result is False

        # Test 3: Blockiert durch eigene Murmel (marble2, pos=15, is_save=True)
        result = game_state.skip_save_marble(Action(pos_from=13, pos_to=18, card=card))
        assert result is False


    def test_is_player_finished(self) -> None:
        # Arrange
        game_state = GameState()

        # Initialisierung der Spieler
        player1 = PlayerState(
            list_card=[],
            list_finish_pos=[68, 69, 70, 71],
            list_kennel_pos=[],
            list_marble=[],
            name="Player1",
            start_pos=0,
        )
        player2 = PlayerState(
            list_card=[],
            list_finish_pos=[76, 77, 78, 79],
            list_kennel_pos=[],
            list_marble=[],
            name="Player2",
            start_pos=0,
        )

        player3 = PlayerState(
            list_card=[],
            list_finish_pos=[84, 85, 86, 87],
            list_kennel_pos=[],
            list_marble=[],
            name="Player3",
            start_pos=0,
        )

        # Initialisiere Murmeln
        marble11 = Marble(pos=68, start_pos=0, is_save=True)
        marble12 = Marble(pos=69, start_pos=0, is_save=True)
        marble13 = Marble(pos=70, start_pos=0, is_save=True)
        marble14 = Marble(pos=71, start_pos=0, is_save=True)
        marble21 = Marble(pos=76, start_pos=16, is_save=True)
        marble22 = Marble(pos=77, start_pos=16, is_save=True)
        marble23 = Marble(pos=78, start_pos=16, is_save=True)
        marble24 = Marble(pos=80, start_pos=16, is_save=False)
        marble31 = Marble(pos=22, start_pos=32, is_save=False)
        marble32 = Marble(pos=23, start_pos=32, is_save=False)
        marble33 = Marble(pos=24, start_pos=32, is_save=False)
        marble34 = Marble(pos=25, start_pos=32, is_save=False)

        # Füge Murmeln den Spielern hinzu
        player1.list_marble.extend([marble11, marble12, marble13, marble14])
        player2.list_marble.extend([marble21, marble22, marble23, marble24])
        player3.list_marble.extend([marble31, marble32, marble33, marble34])

        # Füge Spieler zum GameState hinzu
        game_state.list_player.extend([player1, player2, player3])

        # Test 1: Active player is player1. All marbles in final position. Expect True
        game_state.idx_player_active = 0  # Spieler 1 ist aktiv
        result = game_state.is_player_finished(player1)
        assert result is True

        # Test 2: Active player is player2. Three out of four in final position. Expect False
        game_state.idx_player_active = 1  # Spieler 2 ist aktiv
        result = game_state.is_player_finished(player2)
        assert result is False

        # Test 3: Active player is player3. No marble in final position. Expect False
        game_state.idx_player_active = 2  # Spieler 3 ist aktiv
        result = game_state.is_player_finished(player3)
        assert result is False


    def test_check_game_end(self) -> None:
        # Arrange
        game_state = GameState()

        # Initialisierung der Spieler
        player1 = PlayerState(
            list_card=[],
            list_finish_pos=[68, 69, 70, 71],
            list_kennel_pos=[],
            list_marble=[],
            name="Player1",
            start_pos=0,
        )
        player2 = PlayerState(
            list_card=[],
            list_finish_pos=[76, 77, 78, 79],
            list_kennel_pos=[],
            list_marble=[],
            name="Player2",
            start_pos=0,
        )
        player3 = PlayerState(
            list_card=[],
            list_finish_pos=[84, 85, 86, 87],
            list_kennel_pos=[],
            list_marble=[],
            name="Player3",
            start_pos=0,
        )

        player4 = PlayerState(
            list_card=[],
            list_finish_pos=[92, 93, 94, 95],
            list_kennel_pos=[],
            list_marble=[],
            name="Player4",
            start_pos=0,
        )
        # Initialisiere Murmeln
        marble11 = Marble(pos=68, start_pos=0, is_save=True)
        marble12 = Marble(pos=69, start_pos=0, is_save=True)
        marble13 = Marble(pos=70, start_pos=0, is_save=True)
        marble14 = Marble(pos=71, start_pos=0, is_save=True)
        marble21 = Marble(pos=76, start_pos=16, is_save=True)
        marble22 = Marble(pos=77, start_pos=16, is_save=True)
        marble23 = Marble(pos=78, start_pos=16, is_save=True)
        marble24 = Marble(pos=79, start_pos=16, is_save=True)
        marble31 = Marble(pos=84, start_pos=32, is_save=True)
        marble32 = Marble(pos=85, start_pos=32, is_save=True)
        marble33 = Marble(pos=86, start_pos=32, is_save=True)
        marble34 = Marble(pos=87, start_pos=32, is_save=True)
        marble41 = Marble(pos=92, start_pos=32, is_save=True)
        marble42 = Marble(pos=93, start_pos=32, is_save=True)
        marble43 = Marble(pos=94, start_pos=32, is_save=True)
        marble44 = Marble(pos=22, start_pos=32, is_save=False)

        # Füge Murmeln den Spielern hinzu
        player1.list_marble.extend([marble11, marble12, marble13, marble14])
        player2.list_marble.extend([marble21, marble22, marble23, marble24])
        player3.list_marble.extend([marble31, marble32, marble33, marble34])
        player4.list_marble.extend([marble41, marble42, marble43, marble44])

        game_state.list_player.extend([player1, player2, player3, player4])

        # Prüfe, ob das Spiel fertig ist
        game_state.check_game_end()
        assert game_state.phase == GamePhase.FINISHED

#    def marble_switch_jake

class TestListPossibleAction:
        
    def test_get_list_possible_action1(self) -> None:
        game_state = GameState()
        player1 = PlayerState(  #Player1 for test inside kennel, only movement should be going out
            list_card=[
                Card(suit='♠',rank="2"),
                Card(suit = '♦', rank="A")],
            list_finish_pos=[],
            list_kennel_pos=[64, 65, 66, 67],
            list_marble=[Marble(pos=64, is_save=True, start_pos=64),
                        Marble(pos=65, is_save=True, start_pos=65)],
            name="Player1",
            start_pos=0,
        )

        game_state = GameState(
            list_player=[player1],
            idx_player_active=0)

        result = game_state.get_list_possible_action()
        assert len(result) > 0, 'No Actions althought Cards and Marbles are present'

        assert not any(
            action.card.rank == "2" and action.pos_from == 0 and action.pos_to == 2
            for action in result
        ), 'Actions were generated althought Marbles are in Kennel'

        assert not any(
            action.card.rank == 7
            for action in result
        ), 'Actions were generated althought Marbles are in Kennel'

        kennel_actions = [action for action in result if action.pos_from == 64]
        assert len(kennel_actions) == 1, "Going out of Kennel is the only action"
        assert kennel_actions[0].pos_to == player1.start_pos, "Movement from kennel to Board is false"


        game_state = GameState()
        player2 = PlayerState(  # Player2 for test on board with 3 and Ace
            list_card=[
                Card(suit='♠',rank="3"),
                Card(suit = '♦', rank="A")],
            list_finish_pos=[],
            list_kennel_pos=[64, 65, 66, 67],
            list_marble=[Marble(pos=15, is_save=False, start_pos=66),
                        Marble(pos=67, is_save=False, start_pos=67)],
            name="Player2",
            start_pos=48)

        game_state = GameState(
            list_player=[player2],
            idx_player_active=0)

        result2 = game_state.get_list_possible_action()
        assert any(
            action.card.rank == "3" and action.pos_from == 15 and action.pos_to == 18
            for action in result2
        ), 'Actions were not genererated althought Marbles are on Board'

        kennel_actions = [action for action in result if action.pos_from == 64]
        assert len(kennel_actions) == 1, "Going out of Kennel is the only action"
        assert kennel_actions[0].pos_to == player1.start_pos, "Movement from kennel to Board is false"

        kennel_actions2 = [action for action in result2 if action.pos_from == 15]
        assert len(kennel_actions2) == 3, "There should be 3 movements for Marble on 15."

        game_state = GameState()
        player3 = PlayerState(  # Player3 for test to return multiple actions (however one marble cant move)
            list_card=[
                Card(suit='♠', rank="2"),
                Card(suit='♦', rank="4"),
                Card(suit='♦', rank='9')],
            list_finish_pos=[],
            list_kennel_pos=[64, 65, 66, 67],
            list_marble=[Marble(pos=15, is_save=False, start_pos=66),
                        Marble(pos=22, is_save=False, start_pos=67),
                        Marble(pos=13, is_save=False, start_pos=65 ),
                        Marble(pos=64, is_save=False, start_pos=64)],
            name="Player3",
            start_pos=48)

        game_state = GameState(
            list_player=[player3],
            idx_player_active=0)

        result3 = game_state.get_list_possible_action()
        movement_actions = [action for action in result3]
        assert len(movement_actions) == 12, "There should be 4 movements for the three Marbles each."

        game_state = GameState()
        player4 = PlayerState(  # Player4 for test to overstep the 64 rule
            list_card=[
                Card(suit='♠', rank="10"),
                Card(suit='♦', rank="4"),
                Card(suit='♦', rank='8')],
            list_finish_pos=[],
            list_kennel_pos=[64, 65, 66, 67],
            list_marble=[Marble(pos=60, is_save=False, start_pos=66)],
            name="Player4",
            start_pos=48)

        game_state = GameState(
            list_player=[player4],
            idx_player_active=0)

        result4 = game_state.get_list_possible_action()
        assert any(
            action.card.rank == "10" and action.pos_to == 6
            for action in result4), 'card moved to invalid position'

        game_state = GameState()
        player5 = PlayerState(  # Player4 for test to not go negative with -4
            list_card=[
                Card(suit='♠', rank="10"),
                Card(suit='♦', rank="4"),
                Card(suit='♦', rank='8')],
            list_finish_pos=[],
            list_kennel_pos=[64, 65, 66, 67],
            list_marble=[Marble(pos=2, is_save=False, start_pos=66)],
            name="Player5",
            start_pos=48)

        game_state = GameState(
            list_player=[player5],
            idx_player_active=0)

        result5 = game_state.get_list_possible_action()

        assert (
            action.card.rank == "4" and (action.pos_to == 62 and action.pos_to == 6)
            for action in result5), 'card moved to invalid position'

class TestDog:

# Marc: Platzhalter 2

# Marc: Platzhalter 1

    def test_print_state(self, capfd):
        # Arrange
        game = Dog()  # Erstelle eine Instanz
        new_state = GameState()  # Erstelle ein neues GameState-Objekt
        new_state.cnt_round = 3
        new_state.phase = GamePhase.RUNNING
        new_state.idx_player_active = 0  # Aktueller Spieler ist der erste in der Liste

        # Füge Spieler und Murmeln hinzu
        player1 = PlayerState(
            list_card=[Card(suit='♠', rank="5"), Card(suit='♥', rank="6")],
            list_finish_pos=[],
            list_kennel_pos=[],
            list_marble=[
                Marble(pos=5, start_pos=64, is_save=False),
                Marble(pos=10, start_pos=65, is_save=False),
            ],
            name="Player1",
            start_pos=0,
        )
        player2 = PlayerState(
            list_card=[Card(suit='♠', rank="10")],
            list_finish_pos=[],
            list_kennel_pos=[],
            list_marble=[
                Marble(pos=20, start_pos=72, is_save=False),
                Marble(pos=25, start_pos=73, is_save=False),
            ],
            name="Player2",
            start_pos=32,
        )
        new_state.list_player.extend([player1, player2])  # Direkter Zugriff auf `list_player`
        game.set_state(new_state)  # Setze den Zustand im Spiel

        # Act
        game.print_state()

        # Capture output
        captured = capfd.readouterr()

        # Assert: Überprüfe die Konsolenausgabe
        assert "We are in round 3 and the current player is Player1" in captured.out
        assert "Player Player1 has positions: [5, 10] and holds 2 cards" in captured.out
        assert "Player Player2 has positions: [20, 25] and holds 1 cards" in captured.out
        assert "The actual game phase: GamePhase.RUNNING" in captured.out

    def test_get_player_view(self):
        # Arrange
        game = Dog()  # Erstelle eine Instanz
        game.state = GameState()  # Erstelle ein neues GameState-Objekt

        player1 = PlayerState(
            list_card=[Card(suit='♠', rank="5"), Card(suit='♥', rank="6")],
            list_finish_pos=[],
            list_kennel_pos=[],
            list_marble=[
                Marble(pos=5, start_pos=64, is_save=False),
                Marble(pos=10, start_pos=65, is_save=False),
            ],
            name="Player1",
            start_pos=0,
        )
        player2 = PlayerState(
            list_card=[Card(suit='♠', rank="10")],
            list_finish_pos=[],
            list_kennel_pos=[],
            list_marble=[
                Marble(pos=20, start_pos=72, is_save=False),
                Marble(pos=25, start_pos=73, is_save=False),
            ],
            name="Player2",
            start_pos=16,
        )

        player3 = PlayerState(
            list_card=[Card(suit='♠', rank="10"), Card(suit='♥', rank = "JKR"), Card(suit='♥', rank = "4")],
            list_finish_pos=[],
            list_kennel_pos=[],
            list_marble=[
                Marble(pos=52, start_pos=80, is_save=False),
                Marble(pos=53, start_pos=81, is_save=False),
            ],
            name="Player3",
            start_pos=32,
        )
        player4 = PlayerState(
            list_card=[Card(suit='♠', rank="4"), Card(suit='♥', rank = "A"), Card(suit='♥', rank = "9")],
            list_finish_pos=[],
            list_kennel_pos=[],
            list_marble=[
                Marble(pos=15, start_pos=88, is_save=False),
                Marble(pos=6, start_pos=89, is_save=False),
            ],
            name="Player3",
            start_pos=48,
        )

        game.state.list_player.extend([player1, player2, player3, player4])

        # Act
        # Wir holen die Sicht für player1 (Index 0)
        masked_state = game.get_player_view(idx_player=0)

        # Assert
        # Player1 (Index 0) sollte seine eigenen Karten unverändert sehen
        assert masked_state.list_player[0].list_card[0].rank == "5"
        assert masked_state.list_player[0].list_card[1].rank == "6"

        # Player2 (Index 1), Player3 (Index 2), Player4 (Index 3) sollten maskierte Karten haben
        # Sie sollten jetzt nur noch Karten mit rank="X" haben.
        for i in [1, 2, 3]:
            for card in masked_state.list_player[i].list_card:
                assert card.rank == "X"
                assert card.suit == ""

        # Zusätzlich kannst du prüfen, ob die Marble-Positionen unverändert sind
        assert masked_state.list_player[0].list_marble[0].pos == 5
        assert masked_state.list_player[0].list_marble[1].pos == 10
        assert masked_state.list_player[1].list_marble[0].pos == 20
        assert masked_state.list_player[1].list_marble[1].pos == 25
        assert masked_state.list_player[2].list_marble[0].pos == 52
        assert masked_state.list_player[2].list_marble[1].pos == 53
        assert masked_state.list_player[3].list_marble[0].pos == 15
        assert masked_state.list_player[3].list_marble[1].pos == 6

if __name__ == '__main__':
    # Tests für TestKaegisDogParts
    testKaegisDogParts = TestKaegisDogParts()
    testKaegisDogParts.test_setup_players()
    testKaegisDogParts.test_deal_cards()
    testKaegisDogParts.test_init_next_turn()
    testKaegisDogParts.test_exchange_cards()
    testKaegisDogParts.test_discard_invalid_cards()
    testKaegisDogParts.test_go_in_final()
    testKaegisDogParts.test_set_action_to_game()

    # Tests für TestGameState
    testGameState = TestGameState()
    # testGameState.test_can_leave_kennel_no_card()
    # testGameState.test_can_leave_kennel_valid_card()
    # testGameState.test_can_leave_kennel_invalid_card()
    # testGameState.get_list_action_no_start_cards()
    # testGameState.test_check_final_pos_valid_pos_to()
    # testGameState.test_check_final_pos_valid_pos_from()
    # testGameState.test_check_final_pos_invalid_positions()
    # testGameState.test_check_final_pos_both_valid()
    testGameState.test_sending_home()
    testGameState.test_skip_save_marble()
    testGameState.test_check_game_end()
    testGameState.test_is_player_finished()

    actionlist = TestListPossibleAction()
    actionlist.test_get_list_possible_action1()







# test_set_state
# test get_state
# test print_state
# test get_player_view





