import pytest

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
