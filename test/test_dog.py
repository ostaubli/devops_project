import pytest

from pydantic import BaseModel
from typing import List, Optional, Dict

from server.py.dog import Card, Marble, PlayerState, Action, GameState, GamePhase, Dog

class TestKaegisDogParts:

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
 

class TestGameActions:
    @pytest.fixture
    def setup_game(self):
        # Mock the game state, players, and marbles
        class Marble:
            def __init__(self, pos, is_save=True):
                self.pos = str(pos)
                self.is_save = is_save

        class Player:
            def __init__(self, marbles):
                self.list_marble = [Marble(pos) for pos in marbles]

        class Game:
            def __init__(self):
                self.list_player = [
                    Player([1, 2, 3]),  # Player 1 marbles
                    Player([4, 5, 6])   # Player 2 marbles
                ]

            def marble_switch_jake(self, player_idx, opponent_idx, player_marble_pos, opponent_marble_pos):
                # Paste the marble_switch_jake code here
                pass

        return Game()

    def test_marble_switch_valid(self, setup_game):
        game = setup_game

        # Call the marble_switch_jake function
        game.marble_switch_jake(player_idx=0, opponent_idx=1, player_marble_pos=1, opponent_marble_pos=4)

        # Assert that marbles are swapped
        assert game.list_player[0].list_marble[0].pos == "4"  # Player 1's marble moved to 4
        assert game.list_player[1].list_marble[0].pos == "1"  # Player 2's marble moved to 1

    def test_marble_switch_invalid_player_marble(self, setup_game):
        game = setup_game

        # Attempt to switch a non-existent marble for the player
        with pytest.raises(ValueError, match="No marble found at position 10 for the active player."):
            game.marble_switch_jake(player_idx=0, opponent_idx=1, player_marble_pos=10, opponent_marble_pos=4)

    def test_marble_switch_invalid_opponent_marble(self, setup_game):
        game = setup_game

        # Attempt to switch a non-existent marble for the opponent
        with pytest.raises(ValueError, match="No marble found at position 10 for the opponent player."):
            game.marble_switch_jake(player_idx=0, opponent_idx=1, player_marble_pos=1, opponent_marble_pos=10)



def test_apply_action_valid_move(setup_game):
    game = setup_game

    class Action:
        def __init__(self, card, pos_from, pos_to):
            self.card = card
            self.pos_from = pos_from
            self.pos_to = pos_to

    class Card:
        def __init__(self, rank):
            self.rank = rank

    # Add mock card to active player's hand
    active_player = game.list_player[0]
    card = Card(rank="5")
    active_player.list_card = [card]

    # Define a valid action
    action = Action(card=card, pos_from=1, pos_to=3)

    # Call apply_action
    game.apply_action(action)

    # Assert the marble has moved
    assert active_player.list_marble[0].pos == "3"

    # Assert the card was removed from the player's hand and discarded
    assert card not in active_player.list_card
    assert card in game.list_card_discard

def test_apply_action_invalid_card(setup_game):
    game = setup_game

    class Action:
        def __init__(self, card, pos_from, pos_to):
            self.card = card
            self.pos_from = pos_from
            self.pos_to = pos_to

    class Card:
        def __init__(self, rank):
            self.rank = rank

    # Define a card not in the player's hand
    card = Card(rank="5")

    # Define an action with the invalid card
    action = Action(card=card, pos_from=1, pos_to=3)

    with pytest.raises(ValueError, match="The card played is not in the active player's hand."):
        game.apply_action(action)

def test_apply_action_invalid_marble_position(setup_game):
    game = setup_game

    class Action:
        def __init__(self, card, pos_from, pos_to):
            self.card = card
            self.pos_from = pos_from
            self.pos_to = pos_to

    class Card:
        def __init__(self, rank):
            self.rank = rank

    # Add mock card to active player's hand
    active_player = game.list_player[0]
    card = Card(rank="5")
    active_player.list_card = [card]

    # Define an action with an invalid starting position
    action = Action(card=card, pos_from=10, pos_to=3)

    with pytest.raises(ValueError, match="No marble found at the specified pos_from: 10"):
        game.apply_action(action)



@pytest.fixture
def game_state():    # Keneds marble switch test
    game_state = GameState()
    game_state.setup_players()
    return game_state

def test_marble_switch_jake_valid_swap(game_state):
    # Arrange
    player_idx = 0
    opponent_idx = 1
    player_marble_pos = 64
    opponent_marble_pos = 72

    # Act
    game_state.marble_switch_jake(player_idx, opponent_idx, player_marble_pos, opponent_marble_pos)

    # Assert
    assert game_state.list_player[player_idx].list_marble[0].pos == 72
    assert game_state.list_player[opponent_idx].list_marble[0].pos == 64
    assert not game_state.list_player[player_idx].list_marble[0].is_save
    assert not game_state.list_player[opponent_idx].list_marble[0].is_save

def test_marble_switch_jake_no_player_marble(game_state):
    # Arrange
    player_idx = 0
    opponent_idx = 1
    player_marble_pos = 99  # Invalid position
    opponent_marble_pos = 72

    # Act & Assert
    with pytest.raises(ValueError, match=f"No marble found at position {player_marble_pos} for the active player."):
        game_state.marble_switch_jake(player_idx, opponent_idx, player_marble_pos, opponent_marble_pos)

def test_marble_switch_jake_no_opponent_marble(game_state):
    # Arrange
    player_idx = 0
    opponent_idx = 1
    player_marble_pos = 64
    opponent_marble_pos = 99  # Invalid position

    # Act & Assert
    with pytest.raises(ValueError, match=f"No marble found at position {opponent_marble_pos} for the opponent player."):
        game_state.marble_switch_jake(player_idx, opponent_idx, player_marble_pos, opponent_marble_pos)

    @pytest.fixture
    def game_state():   # Keneds print_state test
        game_state = GameState()
        game_state.setup_players()
        return game_state

    def print_state(self) -> None:
        """ Print the current game state """
        print(self.state)
        pass

    def test_print_state(game_state, capsys):
        game_state.print_state()
        captured = capsys.readouterr()
        assert "GameState" in captured.out



# Keneds test for set_action_to_game
@pytest.fixture
def game_state():
    game_state = GameState()
    game_state.setup_players()
    return game_state

def card_not_in_hand_raises_error(game_state):
    action = Action(card=Card(suit='♠', rank='2'), pos_from=64, pos_to=65)
    with pytest.raises(ValueError, match="The card played is not in the active player's hand."):
        game_state.set_action_to_game(action)

def pos_from_or_pos_to_not_defined_raises_error(game_state):
    action = Action(card=game_state.list_player[0].list_card[0], pos_from=None, pos_to=65)
    with pytest.raises(ValueError, match="Both pos_from and pos_to must be specified for the action."):
        game_state.set_action_to_game(action)

def marble_not_found_at_pos_from_raises_error(game_state):
    action = Action(card=game_state.list_player[0].list_card[0], pos_from=99, pos_to=65)
    with pytest.raises(ValueError, match="No marble found at the specified pos_from: 99"):
        game_state.set_action_to_game(action)

def valid_action_updates_marble_position(game_state):
    action = Action(card=game_state.list_player[0].list_card[0], pos_from=64, pos_to=65)
    game_state.set_action_to_game(action)
    assert game_state.list_player[0].list_marble[0].pos == '65'

def opponent_marble_at_destination_is_sent_home(game_state):
    action = Action(card=game_state.list_player[0].list_card[0], pos_from=64, pos_to=72)
    game_state.set_action_to_game(action)
    assert game_state.list_player[1].list_marble[0].pos == '0'

def played_card_is_discarded(game_state):
    action = Action(card=game_state.list_player[0].list_card[0], pos_from=64, pos_to=65)
    game_state.set_action_to_game(action)
    assert action.card not in game_state.list_player[0].list_card
    assert action.card in game_state.list_card_discard

def special_card_7_sets_card_active(game_state):
    action = Action(card=Card(suit='♠', rank='7'), pos_from=64, pos_to=65)
    game_state.list_player[0].list_card.append(action.card)
    game_state.set_action_to_game(action)
    assert game_state.card_active == action.card

def special_card_j_does_not_set_card_active(game_state):
    action = Action(card=Card(suit='♠', rank='J'), pos_from=64, pos_to=65)
    game_state.list_player[0].list_card.append(action.card)
    game_state.set_action_to_game(action)
    assert game_state.card_active is None

def special_card_jkr_does_not_set_card_active(game_state):
    action = Action(card=Card(suit='', rank='JKR'), pos_from=64, pos_to=65)
    game_state.list_player[0].list_card.append(action.card)
    game_state.set_action_to_game(action)
    assert game_state.card_active is None