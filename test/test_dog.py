import pytest
from server.py.dog import Dog, Card, Marble, PlayerState, GamePhase, Action


def test_game_initialization():
    game = Dog()
    assert game.state.cnt_player == 4
    assert len(game.state.list_player) == 4
    assert game.state.phase == GamePhase.RUNNING
    assert len(game.state.list_card_draw) > 0
    assert len(game.state.list_card_discard) == 0
    assert all(len(player.list_marble) == 4 for player in game.state.list_player)


def test_marble_movement():
    game = Dog()
    player = game.state.list_player[0]
    marble = player.list_marble[0]

    marble.pos = 10
    marble.is_save = True

    card = Card(suit='♠', rank='5')
    action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 5) % game.CIRCULAR_PATH_LENGTH)

    game.apply_action(action)
    assert marble.pos == (10 + 5) % game.CIRCULAR_PATH_LENGTH


def test_king_card_action():
    game = Dog()
    player = game.state.list_player[0]

    marble = player.list_marble[0]
    marble.pos = game.KENNEL_POSITIONS[0][0]
    marble.is_save = False

    card = Card(suit='♣', rank='K')
    action = Action(card=card, pos_from=marble.pos, pos_to=game.board["start_positions"][0][0])

    game.apply_action(action)
    assert marble.pos == game.board["start_positions"][0][0]
    assert marble.is_save


def test_ace_card_action():
    game = Dog()
    player = game.state.list_player[0]

    marble = player.list_marble[0]
    marble.pos = 30
    marble.is_save = True

    card = Card(suit='♥', rank='A')
    action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 1) % game.CIRCULAR_PATH_LENGTH)

    game.apply_action(action)
    assert marble.pos == (30 + 1) % game.CIRCULAR_PATH_LENGTH


def test_protected_marble_behavior():
    game = Dog()
    player = game.state.list_player[0]
    marble = player.list_marble[0]

    marble.pos = game.board["start_positions"][0][0]
    marble.is_save = True

    assert game.is_protected_marble(marble)


def test_overtake_marble():
    game = Dog()
    player1 = game.state.list_player[0]
    player2 = game.state.list_player[1]

    marble1 = player1.list_marble[0]
    marble2 = player2.list_marble[0]

    marble1.pos = 10
    marble2.pos = 10
    marble2.is_save = True

    game.overtake_marble(10)
    assert marble2.pos in game.KENNEL_POSITIONS[1]


def test_apply_action_with_joker():
    game = Dog()
    player = game.state.list_player[0]

    marble = player.list_marble[0]
    marble.pos = 10
    marble.is_save = True

    card = Card(suit='', rank='JKR')
    action = Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 5) % game.CIRCULAR_PATH_LENGTH)

    game.apply_action(action)
    assert marble.pos == (10 + 5) % game.CIRCULAR_PATH_LENGTH


def test_get_actions_for_card():
    game = Dog()
    player = game.state.list_player[0]

    marble = player.list_marble[0]
    marble.pos = 10
    marble.is_save = True

    card = Card(suit='♠', rank='4')
    actions = game.get_actions_for_card(card, player)
    assert len(actions) > 0


def test_finish_area_behavior():
    game = Dog()
    player = game.state.list_player[0]
    marble = player.list_marble[0]

    marble.pos = game.board["start_positions"][0][0] + 60
    marble.is_save = True

    game.move_to_finish(marble, 0, 4)
    assert marble.pos in game.board["finish_positions"][0]


def test_reshuffle_discard_pile():
    game = Dog()
    game.state.list_card_draw = []
    game.state.list_card_discard = [Card(suit='♠', rank='5')]

    game.reshuffle_discard_pile()
    assert len(game.state.list_card_draw) > 0
    assert len(game.state.list_card_discard) == 0


def test_invalid_action():
    game = Dog()
    player = game.state.list_player[0]
    marble = player.list_marble[0]

    marble.pos = game.KENNEL_POSITIONS[0][0]  # Marble in kennel
    marble.is_save = False

    with pytest.raises(ValueError):
        game.apply_simple_move(marble, marble.pos + 5)


def test_card_seven_split():
    game = Dog()
    player = game.state.list_player[0]
    marble1 = player.list_marble[0]
    marble2 = player.list_marble[1]

    marble1.pos = 10
    marble2.pos = 20
    marble1.is_save = True
    marble2.is_save = True

    card = Card(suit='♥', rank='7')
    player.list_card = [card]

    actions = game.get_actions_for_card(card, player)
    assert len(actions) > 0  # Ensure actions are generated for splitting moves


def test_move_marble_to_invalid_position():
    game = Dog()
    player = game.state.list_player[0]
    marble = player.list_marble[0]

    marble.pos = 100  # Invalid position outside the board
    card = Card(suit='♦', rank='4')
    action = Action(card=card, pos_from=marble.pos, pos_to=10)

    with pytest.raises(ValueError):
        game.apply_action(action)


def test_game_finish():
    game = Dog()
    player = game.state.list_player[0]

    # Move all marbles to finish
    for marble in player.list_marble:
        marble.pos = game.board["finish_positions"][0][0]
        marble.is_save = False

    assert game.is_game_finished()  # Game should be finished
    assert game.get_winner() == player.index


def test_protected_marble_behavior():
    game = Dog()
    player = game.state.list_player[0]
    marble = player.list_marble[0]

    marble.pos = game.board["start_positions"][0][0]  # Protected start position
    marble.is_save = True

    with pytest.raises(ValueError):
        game.overtake_marble(marble.pos)


def test_card_seven_partial_steps():
    game = Dog()
    player = game.state.list_player[0]
    marble1 = player.list_marble[0]
    marble2 = player.list_marble[1]

    marble1.pos = 10
    marble2.pos = 20
    marble1.is_save = True
    marble2.is_save = True

    game.state.card_active = Card(suit='♥', rank='7')
    game.steps_for_7_remaining = 5

    actions = game.get_actions_for_active_7(game.state.card_active, player)
    assert len(actions) > 0  # Partial steps should generate actions


def test_empty_player_marble_list():
    game = Dog()
    player = game.state.list_player[0]
    player.list_marble = []  # No marbles for the player

    card = Card(suit='♠', rank='4')
    actions = game.get_actions_for_card(card, player)
    assert len(actions) == 0  # No actions should be possible


def test_king_card_no_valid_moves():
    game = Dog()
    player = game.state.list_player[0]

    for marble in player.list_marble:
        marble.pos = game.board["finish_positions"][0][0]
        marble.is_save = False

    card = Card(suit='♣', rank='K')
    player.list_card = [card]

    actions = game.get_actions_for_card(card, player)
    assert len(actions) == 0  # No valid moves


def test_move_to_finish_area():
    game = Dog()
    player = game.state.list_player[0]
    marble = player.list_marble[0]

    marble.pos = game.board["start_positions"][0][0] + 60
    marble.is_save = True

    game.move_to_finish(marble, 0, 4)
    assert marble.pos in game.board["finish_positions"][0]

    with pytest.raises(ValueError):
        game.apply_simple_move(marble, marble.pos + 1)


def test_invalid_action_raises():
    game = Dog()
    player = game.state.list_player[0]

    with pytest.raises(ValueError):
        game.apply_action(None)  # No action provided


def test_proceed_to_next_player():
    game = Dog()
    initial_player = game.state.idx_player_active

    game.proceed_to_next_player()
    assert game.state.idx_player_active == (initial_player + 1) % game.state.cnt_player
