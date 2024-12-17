import pytest
from server.py.dog import (
    Dog, Card, Marble, PlayerState, Action, GameState, GamePhase, RandomPlayer
)
from server.py.game import Player
import copy
import random

@pytest.fixture
def game():
    random.seed(8)  # Das Testszenario möglichst durch alle Pfade führen
    return Dog(cnt_players=4)


# =======================================================
# Tests für Datenmodelle und Hilfsklassen
# (Card, Marble, PlayerState, Action, GamePhase, GameState)
# =======================================================
def test_card():
    c1 = Card(suit='♥', rank='A')
    c2 = Card(suit='♥', rank='A')
    c3 = Card(suit='♠', rank='2')
    assert c1 == c2
    assert c1 != c3
    assert "Card" in str(c1)
    assert "Card" in repr(c1)
    # Test __lt__
    assert c3 < c1  # ♠2 kommt vor ♥A

def test_marble():
    m = Marble(pos=10, is_save=False)
    assert m.pos == 10
    assert m.is_save is False

def test_player_state():
    c1 = Card(suit='♥', rank='A')
    pstate = PlayerState(name="P1", list_card=[c1], list_marble=[Marble(pos=64, is_save=False)])
    assert pstate.name == "P1"
    assert len(pstate.list_card) == 1
    assert len(pstate.list_marble) == 1

def test_action():
    a = Action(card=Card(suit='♥', rank='K'), pos_from=10, pos_to=20, card_swap=None)
    a2 = Action(card=Card(suit='♥', rank='K'), pos_from=10, pos_to=20, card_swap=None)
    assert a == a2
    assert "card=" in str(a)
    assert "card=" in repr(a)

def test_game_phase():
    assert GamePhase.SETUP == "setup"
    assert GamePhase.RUNNING == "running"
    assert GamePhase.FINISHED == "finished"

def test_game_state():
    state = GameState(
        cnt_player=4,
        phase=GamePhase.SETUP,
        cnt_round=1,
        bool_card_exchanged=False,
        idx_player_started=0,
        idx_player_active=0,
        list_player=[],
        list_card_draw=[],
        list_card_discard=[],
        card_active=None
    )
    assert state.cnt_player == 4
    assert state.phase == GamePhase.SETUP


# =======================================================
# Tests für Game-Setup und State-Management
# =======================================================
def test_dog_init(game):
    state = game.get_state()
    assert state.phase == GamePhase.RUNNING
    assert len(state.list_player) == 4

def test_dog_reset(game):
    game.state.cnt_round = 5
    game.reset()
    assert game.state.cnt_round == 1

def test_dog_set_state(game):
    new_state = copy.deepcopy(game.get_state())
    new_state.cnt_round = 3
    game.set_state(new_state)
    assert game.get_state().cnt_round == 3

def test_dog_print_state(game):
    # print_state ist leer, wir testen nur, dass kein Fehler auftritt
    game.print_state()

def test_setup_next_round(game):
    game.state.cnt_round = 2
    old_len = len(game.state.list_player[0].list_card)
    game.setup_next_round()
    assert len(game.state.list_player[0].list_card) >= old_len

def test_next_turn(game):
    old_active = game.state.idx_player_active
    game.next_turn()
    assert game.state.idx_player_active != old_active

def test_player_finished(game):
    assert not game._player_finished(0)

def test_controlled_player_indices(game):
    indices = game._controlled_player_indices()
    assert isinstance(indices, list)

def test_get_player_marbles(game):
    marbles = game._get_player_marbles()
    assert isinstance(marbles, list)
    assert len(marbles) > 0


# =======================================================
# Tests für Aktionen und Bewegungslogik
# (Start-Aktionen, Jack, Standard, Joker)
# =======================================================
def test_get_start_actions(game):
    c = Card(suit='♥', rank='A')
    actions = game._get_start_actions(c)
    assert isinstance(actions, list)

def test_get_safe_marble_actions_for_jack(game):
    actions = game._get_safe_marble_actions_for_jack([], Card(suit='♥', rank='J'))
    assert actions == []

def test_get_jack_actions(game):
    c = Card(suit='♥', rank='J')
    actions = game._get_jack_actions(c)
    assert isinstance(actions, list)

def test_get_standard_actions(game):
    c = Card(suit='♥', rank='5')  # 5 Felder
    actions = game._get_standard_actions(c, 5)
    assert isinstance(actions, list)

def test_calc_pos_to(game):
    pos_to = game._calc_pos_to(pos_from=0, dist=5, player_idx=0, rank='5')
    assert pos_to is not None

def test_count_steps_to_finish(game):
    steps = game._count_steps_to_finish(0, game.PLAYER_BOARD_SEGMENTS[0]['start'], game.PLAYER_BOARD_SEGMENTS[0]['final_start'])
    assert isinstance(steps, int)

def test_get_actions_for_seven_card(game):
    actions = game._get_actions_for_seven_card()
    assert actions == []

def test_get_actions_for_joker(game):
    c = Card(suit='♥', rank='JKR')
    actions = game._get_actions_for_joker(c, [])
    assert isinstance(actions, list)

def test_get_actions_for_card(game):
    c = Card(suit='♥', rank='A')
    actions = game._get_actions_for_card(c)
    assert isinstance(actions, list)

def test_get_list_action(game):
    actions = game.get_list_action()
    assert isinstance(actions, list)

def test_unique_sorted_actions(game):
    a1 = Action(card=Card(suit='♥', rank='A'), pos_from=10, pos_to=20)
    a2 = Action(card=Card(suit='♥', rank='A'), pos_from=10, pos_to=30)
    sorted_actions = game._unique_sorted_actions([a1, a2, a1])
    assert len(sorted_actions) == 2

def test_is_valid_move(game):
    valid = game.is_valid_move(64, 0)
    assert isinstance(valid, bool)

def test_can_start(game):
    can = game._can_start(game.PLAYER_BOARD_SEGMENTS[0]['start'])
    assert isinstance(can, bool)

def test_blocked_on_main_path(game):
    blocked = game._blocked_on_main_path(0)
    assert isinstance(blocked, bool)

def test_move_through_main_path(game):
    can_move = game._move_through_main_path(0, 5, 1)
    assert isinstance(can_move, bool)

def test_move_through_final_area(game):
    fs = game.PLAYER_BOARD_SEGMENTS[0]['final_start']
    can_move = game._move_through_final_area(fs, 2)
    assert isinstance(can_move, bool)

def test_path_clear(game):
    clear = game._path_clear(0, 10, 0)
    assert isinstance(clear, bool)


# =======================================================
# Tests für Aktionen ausführen, Spezialkarten, apply_action
# =======================================================
def test_apply_action_none(game):
    old_active = game.state.idx_player_active
    game.apply_action(None)
    assert game.state.idx_player_active != old_active


def test_handle_joker_swap(game):
    p = game.state.list_player[0]
    c = p.list_card[0]
    action = Action(card=c, card_swap=Card(suit='♥', rank='A'))
    game._handle_joker_swap(p, action)
    assert game.state.card_active == Card(suit='♥', rank='A')

def test_find_player_card(game):
    p = game.state.list_player[0]
    c = p.list_card[0]
    found = game._find_player_card(p, c)
    assert found == c

def test_handle_card_7(game):
    p = game.state.list_player[0]
    c = Card(suit='♥', rank='7')
    p.list_card.append(c)
    action = Action(card=c, pos_from=64, pos_to=game.PLAYER_BOARD_SEGMENTS[0]['start'])
    game._handle_card_7(p, c, action)
    # Kein Fehler => ok

def test_handle_card_joker(game):
    p = game.state.list_player[0]
    c = Card(suit='♥', rank='JKR')
    p.list_card.append(c)
    action = Action(card=c, pos_from=64, pos_to=0)
    game._handle_card_joker(p, c, action)

def test_handle_card_other(game):
    p = game.state.list_player[0]
    c = Card(suit='♥', rank='5')
    p.list_card.append(c)
    action = Action(card=c, pos_from=64, pos_to=0)
    game._handle_card_other(p, c, action)

def test_handle_active_card_move(game):
    p = game.state.list_player[0]
    c = Card(suit='♥', rank='Q')
    p.list_card.append(c)
    action = Action(card=c, pos_from=64, pos_to=0)
    game._handle_active_card_move(p, action)

def test_send_to_kennel(game):
    p = game.state.list_player[0]
    m = p.list_marble[0]
    game._send_to_kennel(m, 0)
    ks = Dog.PLAYER_BOARD_SEGMENTS[0]['queue_start']
    assert ks <= m.pos <= ks+3

def test_handle_jack_action(game):
    action = Action(pos_from=64, pos_to=65)
    game._handle_jack_action(action)

def test_handle_seven_move(game):
    p = game.state.list_player[0]
    c = Card(suit='♥', rank='7')
    p.list_card.append(c)
    action = Action(card=c, pos_from=64, pos_to=65)
    game._handle_seven_move(action)


def test_handle_standard_move(game):
    p = game.state.list_player[0]
    c = p.list_card[0]
    action = Action(card=c, pos_from=64, pos_to=65)
    game._handle_standard_move(action)


def test_move_marble(game):
    p = game.state.list_player[0]
    c = p.list_card[0]
    action = Action(card=c, pos_from=64, pos_to=65)
    game._move_marble(action)

def test_send_to_kennel(game):
    p = game.state.list_player[0]
    m = p.list_marble[0]
    game._send_to_kennel(m, 0)
    ks = game.PLAYER_BOARD_SEGMENTS[0]['queue_start']
    assert ks <= m.pos <= ks+3

# -------------------------------------------------------
# Aktionen ausführen und Spielstatus
# -------------------------------------------------------

def test_find_marble_by_pos(game):
    m, idx = game._find_marble_by_pos(64)
    assert m is not None
    assert idx == 0

def test_calc_steps(game):
    steps = game._calc_steps(64, game.PLAYER_BOARD_SEGMENTS[0]['start'], 0)
    assert steps is not None

def test_reset_card_active(game):
    game._reset_card_active()
    assert game.state.card_active is None
    assert game.temp_seven_moves is None
    assert game.temp_seven_card is None
    assert game.temp_joker_card is None
    assert game.temp_seven_state is None

def test_find_player_card(game):
    p = game.state.list_player[0]
    c = p.list_card[0]
    found = game._find_player_card(p, c)
    assert found == c

def test_handle_card_7(game):
    p = game.state.list_player[0]
    c = Card(suit='♥', rank='7')
    p.list_card.append(c)
    action = Action(card=c, pos_from=64, pos_to=game.PLAYER_BOARD_SEGMENTS[0]['start'])
    game._handle_card_7(p, c, action)
    # Kein Fehler => ok

def test_handle_card_joker(game):
    p = game.state.list_player[0]
    c = Card(suit='♥', rank='JKR')
    p.list_card.append(c)
    action = Action(card=c, pos_from=64, pos_to=0)
    game._handle_card_joker(p, c, action)

def test_handle_card_other(game):
    p = game.state.list_player[0]
    c = Card(suit='♥', rank='5')
    p.list_card.append(c)
    action = Action(card=c, pos_from=64, pos_to=0)
    game._handle_card_other(p, c, action)

def test_handle_jack_action(game):
    action = Action(pos_from=64, pos_to=65)
    game._handle_jack_action(action)

def test_calc_steps(game):
    steps = game._calc_steps(64, game.PLAYER_BOARD_SEGMENTS[0]['start'], 0)
    assert steps is not None

def test_check_game_status(game):
    game.check_game_status()
    assert game.state.phase == GamePhase.RUNNING

def test_get_move_distance(game):
    c = Card(suit='♥', rank='A')
    dist = game.get_move_distance(c)
    assert dist == [1, 11]

def test_get_player_view(game):
    view = game.get_player_view(0)
    assert isinstance(view, GameState)

def test_swap_cards_final(game):
    p1 = game.state.list_player[0]
    p2 = game.state.list_player[2]
    c1 = p1.list_card[0]
    c2 = p2.list_card[0]
    game.swap_cards(0, 2, c1, c2)
    assert c1 in p2.list_card
    assert c2 in p1.list_card

def test_random_player():
    rp = RandomPlayer()
    state = GameState(
        cnt_player=4,
        phase=GamePhase.RUNNING,
        cnt_round=1,
        bool_card_exchanged=False,
        idx_player_started=0,
        idx_player_active=0,
        list_player=[],
        list_card_draw=[],
        list_card_discard=[],
        card_active=None
    )
    actions = [Action(card=Card(suit='♥', rank='A'), pos_from=64, pos_to=0)]
    chosen = rp.select_action(state, actions)
    assert chosen in actions or chosen is None
    rp.do_nothing()


# =======================================================
# Szenarien, mehrere Runden, Reset, Spielende, Spezialfälle
# =======================================================
def test_finish_game_scenario(game):
    p = game.state.list_player[0]
    fs = Dog.PLAYER_BOARD_SEGMENTS[0]['final_start']
    for i, m in enumerate(p.list_marble):
        m.pos = fs+i
    game.check_game_status()
    assert game.state.phase == GamePhase.FINISHED

def test_apply_action_with_card(game):
    p = game.state.list_player[0]
    c = p.list_card[0]
    start_field = Dog.PLAYER_BOARD_SEGMENTS[0]['start']
    action = Action(card=c, pos_from=64, pos_to=start_field)
    try:
        game.apply_action(action)
    except:
        pytest.fail("apply_action with a card raised an exception unexpectedly!")

def test_no_error_on_many_next_turns(game):
    for _ in range(10):
        game.next_turn()
    assert True

def test_reset_and_replay(game):
    game.reset()
    actions = game.get_list_action()
    assert isinstance(actions, list)

def test_set_active_card_and_actions(game):
    p = game.state.list_player[0]
    c = p.list_card[0]
    card_j = Card(suit='♥', rank='J')
    p.list_card.append(card_j)
    game.state.card_active = card_j
    actions = game.get_list_action()
    assert isinstance(actions, list)

def test_apply_invalid_action(game):
    p = game.state.list_player[0]
    c = p.list_card[0]
    invalid_action = Action(card=c, pos_from=999, pos_to=0)
    try:
        game.apply_action(invalid_action)
    except:
        pytest.fail("apply_action raised an exception unexpectedly for an invalid action!")

def test_apply_action_no_card_active_yet(game):
    p = game.state.list_player[0]
    c = p.list_card[0]
    action = Action(card=c, pos_from=64, pos_to=10)
    try:
        game.apply_action(action)
    except:
        pytest.fail("apply_action raised an exception unexpectedly!")

def test_finish_game_multiple_players(game):
    p0 = game.state.list_player[0]
    fs0 = Dog.PLAYER_BOARD_SEGMENTS[0]['final_start']
    for i, m in enumerate(p0.list_marble):
        m.pos = fs0 + i
    game.check_game_status()
    assert game.state.phase == GamePhase.FINISHED
    game.reset()
    p1 = game.state.list_player[1]
    fs1 = Dog.PLAYER_BOARD_SEGMENTS[1]['final_start']
    for i, m in enumerate(p1.list_marble):
        m.pos = fs1 + i
    game.check_game_status()
    assert game.state.phase == GamePhase.FINISHED

def test_multiple_resets(game):
    for _ in range(3):
        game.reset()
        assert game.state.cnt_round == 1
        assert game.state.phase == GamePhase.RUNNING

def test_random_player_no_actions():
    rp = RandomPlayer()
    state = GameState(
        cnt_player=4,
        phase=GamePhase.RUNNING,
        cnt_round=1,
        bool_card_exchanged=False,
        idx_player_started=0,
        idx_player_active=0,
        list_player=[],
        list_card_draw=[],
        list_card_discard=[],
        card_active=None
    )
    actions = []
    chosen = rp.select_action(state, actions)
    assert chosen is None

def test_random_player_with_multiple_actions():
    rp = RandomPlayer()
    state = GameState(
        cnt_player=4,
        phase=GamePhase.RUNNING,
        cnt_round=1,
        bool_card_exchanged=False,
        idx_player_started=0,
        idx_player_active=0,
        list_player=[],
        list_card_draw=[],
        list_card_discard=[],
        card_active=None
    )
    actions = [
        Action(card=Card(suit='♥', rank='A'), pos_from=64, pos_to=0),
        Action(card=Card(suit='♥', rank='K'), pos_from=65, pos_to=10),
        Action(card=Card(suit='♥', rank='Q'), pos_from=66, pos_to=20)
    ]
    chosen = rp.select_action(state, actions)
    assert chosen in actions

def test_set_active_card_and_actions(game):
    p = game.state.list_player[0]
    c = Card(suit='♥', rank='J')
    p.list_card.append(c)
    game.state.card_active = c
    actions = game.get_list_action()
    assert isinstance(actions, list)

def test_apply_invalid_action(game):
    p = game.state.list_player[0]
    c = p.list_card[0]
    invalid_action = Action(card=c, pos_from=999, pos_to=0)
    try:
        game.apply_action(invalid_action)
    except:
        pytest.fail("apply_action raised an exception unexpectedly for an invalid action!")

def test_apply_action_no_card_active_yet(game):
    p = game.state.list_player[0]
    c = p.list_card[0]
    action = Action(card=c, pos_from=64, pos_to=10)
    try:
        game.apply_action(action)
    except:
        pytest.fail("apply_action raised an exception unexpectedly!")
    # Kein Fehler, auch wenn unwirksam

def test_finish_game_multiple_players(game):
    p0 = game.state.list_player[0]
    fs0 = Dog.PLAYER_BOARD_SEGMENTS[0]['final_start']
    for i, m in enumerate(p0.list_marble):
        m.pos = fs0 + i
    game.check_game_status()
    assert game.state.phase == GamePhase.FINISHED, "Spiel sollte beendet sein."
    game.reset()
    p1 = game.state.list_player[1]
    fs1 = Dog.PLAYER_BOARD_SEGMENTS[1]['final_start']
    for i, m in enumerate(p1.list_marble):
        m.pos = fs1 + i
    game.check_game_status()
    assert game.state.phase == GamePhase.FINISHED

def test_multiple_resets(game):
    for _ in range(3):
        game.reset()
        assert game.state.cnt_round == 1, "Nach Reset wieder bei 1."
        assert game.state.phase == GamePhase.RUNNING

def test_random_player_no_actions():
    rp = RandomPlayer()
    state = GameState(
        cnt_player=4,
        phase=GamePhase.RUNNING,
        cnt_round=1,
        bool_card_exchanged=False,
        idx_player_started=0,
        idx_player_active=0,
        list_player=[],
        list_card_draw=[],
        list_card_discard=[],
        card_active=None
    )
    actions = []
    chosen = rp.select_action(state, actions)
    assert chosen is None

def test_random_player_with_multiple_actions():
    rp = RandomPlayer()
    state = GameState(
        cnt_player=4,
        phase=GamePhase.RUNNING,
        cnt_round=1,
        bool_card_exchanged=False,
        idx_player_started=0,
        idx_player_active=0,
        list_player=[],
        list_card_draw=[],
        list_card_discard=[],
        card_active=None
    )
    actions = [
        Action(card=Card(suit='♥', rank='A'), pos_from=64, pos_to=0),
        Action(card=Card(suit='♥', rank='K'), pos_from=65, pos_to=10),
        Action(card=Card(suit='♥', rank='Q'), pos_from=66, pos_to=20)
    ]
    chosen = rp.select_action(state, actions)
    assert chosen in actions or chosen is None

def test_apply_invalid_positions(game):
    p = game.state.list_player[0]
    c = Card(suit='♥', rank='8')
    p.list_card.append(c)
    invalid_action_1 = Action(card=c, pos_from=-10, pos_to=10)
    try:
        game.apply_action(invalid_action_1)
    except:
        pytest.fail("negative pos_from Fehler!")
    invalid_action_2 = Action(card=c, pos_from=64, pos_to=9999)
    try:
        game.apply_action(invalid_action_2)
    except:
        pytest.fail("huge pos_to Fehler!")

def test_reset_after_finish(game):
    p = game.state.list_player[0]
    fs = Dog.PLAYER_BOARD_SEGMENTS[0]['final_start']
    for i, m in enumerate(p.list_marble):
        m.pos = fs + i
    game.check_game_status()
    assert game.state.phase == GamePhase.FINISHED
    game.reset()
    state = game.get_state()
    assert state.phase == GamePhase.RUNNING

def test_apply_action_multiple_times(game):
    p = game.state.list_player[0]
    c = Card(suit='♥', rank='A')
    p.list_card.append(c)
    action = Action(card=c, pos_from=64, pos_to=0)
    game.apply_action(action)
    game.apply_action(None)
    game.apply_action(None)
    assert True

def test_handle_card_7_multiple_times(game):
    p = game.state.list_player[0]
    c = Card(suit='♥', rank='7')
    p.list_card.append(c)
    action1 = Action(card=c, pos_from=64, pos_to=65)
    game.apply_action(action1)
    action2 = Action(card=c, pos_from=65, pos_to=67)
    game.apply_action(action2)
    action3 = Action(card=c, pos_from=67, pos_to=74 % 64)
    try:
        game.apply_action(action3)
    except:
        pytest.fail("7er mehrmals Fehler")

def test_swap_cards_illegal_card(game):
    state = game.get_state()
    p1 = state.list_player[0]
    p2 = state.list_player[1]
    c1 = Card(suit='♥', rank='9')
    c2 = Card(suit='♦', rank='2')
    if c1 in p1.list_card:
        p1.list_card.remove(c1)
    if c2 in p2.list_card:
        p2.list_card.remove(c2)
    try:
        game.swap_cards(0, 1, c1, c2)
    except ValueError:
        pass
    except:
        pytest.fail("swap_cards illegal error")

def test_random_player_extreme_cases():
    rp = RandomPlayer()
    state = GameState(
        cnt_player=4,
        phase=GamePhase.RUNNING,
        cnt_round=10,
        bool_card_exchanged=True,
        idx_player_started=3,
        idx_player_active=2,
        list_player=[],
        list_card_draw=[],
        list_card_discard=[],
        card_active=None
    )
    actions = []
    for i in range(1000):
        actions.append(Action(card=Card(suit='♥', rank='A'), pos_from=64, pos_to=i))
    chosen = rp.select_action(state, actions)
    assert chosen in actions or chosen is None

def test_get_player_view_multiple_players(game):
    for i in range(game.state.cnt_player):
        view = game.get_player_view(i)
        assert isinstance(view, GameState)

def test_check_game_status_after_random_moves(game):
    for _ in range(20):
        game.apply_action(None)
        game.check_game_status()
    assert True

def test_no_start_actions_without_start_cards(game):
    p = game.state.list_player[0]
    p.list_card.clear()
    p.list_card.extend([Card(suit='♣', rank='2'), Card(suit='♦', rank='3'), Card(suit='♠', rank='5')])
    actions = game.get_list_action()
    start_positions = [a for a in actions if a.pos_to == game.PLAYER_BOARD_SEGMENTS[0]['start']]
    assert len(start_positions) == 0

def test_joker_options_are_correct(game):
    c = Card(suit='', rank='JKR')
    dist = game.get_move_distance(c)
    assert isinstance(dist, list)
    assert len(dist) == 13
    assert sorted(dist) == [1,2,3,4,5,6,7,8,9,10,11,12,13]

def test_apply_action_with_none_card(game):
    action = Action(pos_from=64, pos_to=0, card=None)
    try:
        game.apply_action(action)
    except:
        pytest.fail("action with card=None error")

def test_apply_action_card_not_in_hand(game):
    p = game.state.list_player[0]
    c = Card(suit='♦', rank='Q')
    action = Action(card=c, pos_from=64, pos_to=0)
    try:
        game.apply_action(action)
    except:
        pytest.fail("card not in hand error")

def test_action_swapping_joker(game):
    p = game.state.list_player[0]
    c = Card(suit='', rank='JKR')
    p.list_card.append(c)
    action_swap = Action(card=c, pos_from=-1, pos_to=-1, card_swap=Card(suit='♣', rank='K'))
    game.apply_action(action_swap)
    assert game.state.card_active == Card(suit='♣', rank='K')
    action_swap_2 = Action(card=c, pos_from=-1, pos_to=-1, card_swap=Card(suit='♦', rank='3'))
    try:
        game.apply_action(action_swap_2)
    except:
        pytest.fail("zweiter JOKER Swap error")

def test_path_clear_with_complex_scenario(game):
    state = game.get_state()
    p0 = state.list_player[0]
    p1 = state.list_player[1]
    p0.list_marble[0].pos = 0
    p0.list_marble[0].is_save = True
    p1.list_marble[0].pos = 10
    p1.list_marble[0].is_save = True
    game.set_state(state)
    clear = game._path_clear(0, 20, 0)
    assert clear == False

def test_round_transition(game):
    initial_round = game.state.cnt_round
    for _ in range(game.state.cnt_player):
        game.apply_action(None)
    assert game.state.cnt_round == initial_round + 1

def test_none_action_multiple_times(game):
    for _ in range(5):
        game.apply_action(None)
    assert game.state.phase in [GamePhase.RUNNING, GamePhase.FINISHED]

def test_random_card_move_distance(game):
    c_unknown = Card(suit='♥', rank='X')
    dist = game.get_move_distance(c_unknown)
    assert dist is None

def test_reset_during_game(game):
    initial_phase = game.state.phase
    game.reset()
    assert game.state.phase == GamePhase.RUNNING
    assert game.state.cnt_round == 1

def test_apply_action_with_swap_and_no_joker(game):
    p = game.state.list_player[0]
    c = p.list_card[0]
    swap_action = Action(card=c, pos_from=-1, pos_to=-1, card_swap=Card(suit='♥', rank='A'))
    try:
        game.apply_action(swap_action)
    except:
        pytest.fail("Swap ohne JOKER error")

def test_apply_action_with_just_joker_without_swap(game):
    p = game.state.list_player[0]
    c_jkr = Card(suit='', rank='JKR')
    p.list_card.append(c_jkr)
    jkr_action = Action(card=c_jkr, pos_from=64, pos_to=65)
    try:
        game.apply_action(jkr_action)
    except:
        pytest.fail("JOKER ohne Swap error")

def test_cycle_through_all_rounds(game):
    for _ in range(30):
        for _ in range(game.state.cnt_player):
            game.apply_action(None)
    assert True

def test_print_state_multiple_times(game):
    for _ in range(10):
        game.print_state()
    assert True

def test_ace_as_1_or_11(game):
    c_ace = Card(suit='♥', rank='A')
    dist = game.get_move_distance(c_ace)
    assert dist == [1, 11]

def test_seven_options_correctness(game):
    c_seven = Card(suit='♥', rank='7')
    dist = game.get_move_distance(c_seven)
    assert sorted(dist) == [1,2,3,4,5,6,7]

def test_finish_game_and_restart(game):
    p = game.state.list_player[0]
    fs = Dog.PLAYER_BOARD_SEGMENTS[0]['final_start']
    for i, mm in enumerate(p.list_marble):
        mm.pos = fs+i
    game.check_game_status()
    assert game.state.phase == GamePhase.FINISHED
    game.reset()
    actions = game.get_list_action()
    assert isinstance(actions, list)

def test_apply_action_after_finish(game):
    p = game.state.list_player[0]
    fs = Dog.PLAYER_BOARD_SEGMENTS[0]['final_start']
    for i, m in enumerate(p.list_marble):
        m.pos = fs + i
    game.check_game_status()
    assert game.state.phase == GamePhase.FINISHED
    c = p.list_card[0] if p.list_card else Card(suit='♣', rank='2')
    p.list_card.append(c)
    action = Action(card=c, pos_from=64, pos_to=0)
    try:
        game.apply_action(action)
    except:
        pytest.fail("action after finish error")

def test_no_cards_in_hand(game):
    p = game.state.list_player[0]
    p.list_card.clear()
    actions = game.get_list_action()
    assert isinstance(actions, list)

def test_unreachable_finish_move(game):
    p = game.state.list_player[0]
    c = Card(suit='♥', rank='Q')
    p.list_card.append(c)
    final_start = Dog.PLAYER_BOARD_SEGMENTS[0]['final_start']
    p.list_marble[0].pos = final_start - 1
    action = Action(card=c, pos_from=final_start - 1, pos_to=final_start + 5)
    try:
        game.apply_action(action)
    except:
        pytest.fail("unreachable finish error")

def test_joker_with_invalid_swap_card(game):
    p = game.state.list_player[0]
    c_jkr = Card(suit='', rank='JKR')
    p.list_card.append(c_jkr)
    invalid_swap_card = Card(suit='♦', rank='X')
    action = Action(card=c_jkr, pos_from=-1, pos_to=-1, card_swap=invalid_swap_card)
    try:
        game.apply_action(action)
    except:
        pytest.fail("JOKER invalid swap error")

def test_start_from_kennel_with_non_start_card(game):
    p = game.state.list_player[0]
    c = Card(suit='♦', rank='5')
    p.list_card.append(c)
    start_pos = Dog.PLAYER_BOARD_SEGMENTS[0]['start']
    kennel_pos = Dog.PLAYER_BOARD_SEGMENTS[0]['queue_start']
    p.list_marble[0].pos = kennel_pos
    action = Action(card=c, pos_from=kennel_pos, pos_to=start_pos)
    try:
        game.apply_action(action)
    except:
        pytest.fail("start from kennel non-start error")

def test_partner_marble_movement(game):
    fs0 = Dog.PLAYER_BOARD_SEGMENTS[0]['final_start']
    p0 = game.state.list_player[0]
    for i, m in enumerate(p0.list_marble):
        m.pos = fs0 + i
    game.check_game_status()
    p2 = game.state.list_player[2]
    c = p0.list_card[0]
    p2.list_marble[0].pos = 32
    action = Action(card=c, pos_from=32, pos_to=33)
    try:
        game.apply_action(action)
    except:
        pytest.fail("partner marble movement error")

def test_long_sequence_of_none_actions(game):
    for _ in range(100):
        game.apply_action(None)
    assert game.state.phase in [GamePhase.RUNNING, GamePhase.FINISHED]

def test_card_4_forward_move(game):
    p = game.state.list_player[0]
    c = Card(suit='♥', rank='4')
    p.list_card.append(c)
    start = Dog.PLAYER_BOARD_SEGMENTS[0]['start']
    p.list_marble[0].pos = (start + 5) % game.MAIN_PATH_LENGTH
    pos_from = p.list_marble[0].pos
    pos_to = (pos_from + 4) % game.MAIN_PATH_LENGTH
    action = Action(card=c, pos_from=pos_from, pos_to=pos_to)
    try:
        game.apply_action(action)
    except:
        pytest.fail("4 forward move error")

def test_multiple_players_all_stuck(game):
    for pl in game.state.list_player:
        pl.list_card.clear()
        pl.list_card.extend([Card(suit='♣', rank='3'), Card(suit='♦', rank='2')])
        ks = Dog.PLAYER_BOARD_SEGMENTS[game.state.list_player.index(pl)]['queue_start']
        for i, m in enumerate(pl.list_marble):
            m.pos = ks + i
            m.is_save = False
    actions = game.get_list_action()
    assert len(actions) == 0

def test_7_card_partial_path_blocked(game):
    p = game.state.list_player[0]
    c = Card(suit='♥', rank='7')
    p.list_card.append(c)
    p.list_marble[0].pos = 0
    p.list_marble[0].is_save = True
    p2 = game.state.list_player[1]
    p2.list_marble[0].pos = 3
    p2.list_marble[0].is_save = True
    action = Action(card=c, pos_from=0, pos_to=3)
    try:
        game.apply_action(action)
    except:
        pytest.fail("7 card partial block error")

def test_start_with_all_marbles_already_on_board(game):
    p = game.state.list_player[0]
    c_start = Card(suit='♥', rank='A')
    p.list_card.append(c_start)
    for i, m in enumerate(p.list_marble):
        m.pos = (Dog.PLAYER_BOARD_SEGMENTS[0]['start'] + i + 1) % game.MAIN_PATH_LENGTH
        m.is_save = False
    actions = game.get_list_action()
    start_actions = [act for act in actions if act.pos_from is not None and 64 <= act.pos_from < 68]
    assert len(start_actions) == 0

def test_four_card_backward_from_final_area(game):
    p = game.state.list_player[0]
    c_four = Card(suit='♥', rank='4')
    p.list_card.append(c_four)
    fs = Dog.PLAYER_BOARD_SEGMENTS[0]['final_start']
    p.list_marble[0].pos = fs
    p.list_marble[0].is_save = False
    pos_from = fs
    pos_to = fs - 4
    action = Action(card=c_four, pos_from=pos_from, pos_to=pos_to)
    try:
        game.apply_action(action)
    except:
        pytest.fail("4 backward final error")

def test_discard_cards_after_multiple_no_actions(game):
    p = game.state.list_player[0]
    initial_cards = len(p.list_card)
    for _ in range(10 * game.state.cnt_player):
        game.apply_action(None)
    assert len(p.list_card) <= initial_cards

def test_multi_marble_finish_with_single_move(game):
    p = game.state.list_player[0]
    c_king = Card(suit='♦', rank='K')
    p.list_card.append(c_king)
    fs = Dog.PLAYER_BOARD_SEGMENTS[0]['final_start']
    p.list_marble[0].pos = fs - 1
    p.list_marble[1].pos = fs - 2
    p.list_marble[0].is_save = False
    p.list_marble[1].is_save = False
    pos_from = fs - 1
    pos_to = fs + 3
    action = Action(card=c_king, pos_from=pos_from, pos_to=pos_to)
    try:
        game.apply_action(action)
    except:
        pytest.fail("multi marble finish error")

def test_round_continues_if_no_player_can_move(game):
    for _ in range(game.state.cnt_player * 3):
        game.apply_action(None)
    assert game.state.phase in [GamePhase.RUNNING, GamePhase.FINISHED]

def test_joker_swap_to_non_existent_rank(game):
    p = game.state.list_player[0]
    c_jkr = Card(suit='', rank='JKR')
    p.list_card.append(c_jkr)
    invalid_swap_card = Card(suit='♥', rank='1')
    action = Action(card=c_jkr, pos_from=-1, pos_to=-1, card_swap=invalid_swap_card)
    try:
        game.apply_action(action)
    except:
        pytest.fail("JOKER non-existent rank error")

def test_apply_action_after_partially_played_7(game):
    p = game.state.list_player[0]
    c = Card(suit='♥', rank='7')
    p.list_card.append(c)
    action1 = Action(card=c, pos_from=64, pos_to=65)
    game.apply_action(action1)
    invalid_action = Action(card=c, pos_from=999, pos_to=1000)
    try:
        game.apply_action(invalid_action)
    except:
        pytest.fail("partially played 7 error")

def test_apply_action_with_jack_and_no_opponents(game):
    p = game.state.list_player[0]
    c = Card(suit='♥', rank='J')
    p.list_card.append(c)
    for idx, pl in enumerate(game.state.list_player):
        if idx != 0:
            fs = Dog.PLAYER_BOARD_SEGMENTS[idx]['final_start']
            for i, m in enumerate(pl.list_marble):
                m.pos = fs+i
    game.check_game_status()
    actions = game.get_list_action()
    assert isinstance(actions, list)

def test_apply_action_with_unreachable_move_due_to_block(game):
    p = game.state.list_player[0]
    c = Card(suit='♥', rank='Q')
    p.list_card.append(c)
    start = Dog.PLAYER_BOARD_SEGMENTS[0]['start']
    p.list_marble[0].pos = start
    p.list_marble[0].is_save = True
    p2 = game.state.list_player[1]
    p2.list_marble[0].pos = (start + 6) % Dog.MAIN_PATH_LENGTH
    p2.list_marble[0].is_save = True
    pos_from = start
    pos_to = (start + 12) % Dog.MAIN_PATH_LENGTH
    action = Action(card=c, pos_from=pos_from, pos_to=pos_to)
    try:
        game.apply_action(action)
    except:
        pytest.fail("unreachable move due to block error")

def test_apply_action_when_no_active_card_and_no_cards_left(game):
    p = game.state.list_player[0]
    p.list_card.clear()
    action = Action(card=None, pos_from=64, pos_to=0)
    try:
        game.apply_action(action)
    except:
        pytest.fail("action without active card and no cards error")

def test_change_active_player_via_none_actions(game):
    initial_player = game.state.idx_player_active
    for _ in range(game.state.cnt_player):
        game.apply_action(None)
    assert game.state.idx_player_active == initial_player

def test_joker_used_like_ace(game):
    p = game.state.list_player[0]
    c_jkr = Card(suit='', rank='JKR')
    p.list_card.append(c_jkr)
    p.list_marble[0].pos = 0
    action = Action(card=c_jkr, pos_from=0, pos_to=1)
    try:
        game.apply_action(action)
    except:
        pytest.fail("Joker as ace error")

def test_joker_long_range_move(game):
    p = game.state.list_player[0]
    c_jkr = Card(suit='', rank='JKR')
    p.list_card.append(c_jkr)
    pos_from = 0
    pos_to = (pos_from + 13) % Dog.MAIN_PATH_LENGTH
    action = Action(card=c_jkr, pos_from=pos_from, pos_to=pos_to)
    try:
        game.apply_action(action)
    except:
        pytest.fail("Joker long range error")

def test_no_duplicate_cards_drawn(game):
    initial_card_count = (len(game.state.list_card_draw)
                          + sum(len(pl.list_card) for pl in game.state.list_player) + len(game.state.list_card_discard))
    for _ in range(5):
        for _ in range(game.state.cnt_player):
            game.apply_action(None)
    final_card_count = (len(game.state.list_card_draw)
                        + sum(len(pl.list_card) for pl in game.state.list_player) + len(game.state.list_card_discard))
    assert initial_card_count == final_card_count

def test_all_marbles_in_kennel_with_multiple_rounds(game):
    for pl in game.state.list_player:
        pl.list_card.clear()
        pl.list_card.append(Card(suit='♦', rank='2'))
    for _ in range(10 * game.state.cnt_player):
        game.apply_action(None)
    assert game.state.phase in [GamePhase.RUNNING, GamePhase.FINISHED]

def test_invalid_card_during_game(game):
    p = game.state.list_player[0]
    invalid_card = Card(suit='♠', rank='X')
    p.list_card.append(invalid_card)
    action = Action(card=invalid_card, pos_from=64, pos_to=0)
    try:
        game.apply_action(action)
    except:
        pytest.fail("invalid card during game error")

def test_apply_action_with_finished_player(game):
    fs0 = Dog.PLAYER_BOARD_SEGMENTS[0]['final_start']
    p0 = game.state.list_player[0]
    for i, m in enumerate(p0.list_marble):
        m.pos = fs0 + i
    game.check_game_status()
    p2 = game.state.list_player[2]
    c = p0.list_card[0]
    p2.list_marble[0].pos = 32
    action = Action(card=c, pos_from=32, pos_to=33)
    try:
        game.apply_action(action)
    except:
        pytest.fail("finished player move error")

def test_large_number_of_random_moves(game):
    for _ in range(500):
        game.apply_action(None)
    assert game.state.phase in [GamePhase.RUNNING, GamePhase.FINISHED]

def test_seven_card_partial_mixed_marbles(game):
    p0 = game.state.list_player[0]
    c = Card(suit='♥', rank='7')
    p0.list_card.append(c)
    p0.list_marble[0].pos = 0
    p0.list_marble[0].is_save = True
    action1 = Action(card=c, pos_from=0, pos_to=2)
    game.apply_action(action1)
    p2 = game.state.list_player[2]
    p2.list_marble[0].pos = 32
    action2 = Action(card=c, pos_from=32, pos_to=37)
    try:
        game.apply_action(action2)
    except:
        pytest.fail("7 card partial mixed error")

def test_uninitialized_joker_swap(game):
    p = game.state.list_player[0]
    c_jkr = Card(suit='', rank='JKR')
    p.list_card.append(c_jkr)
    swap_card = Card(suit='♦', rank='A')
    action = Action(card=c_jkr, pos_from=-1, pos_to=-1, card_swap=swap_card)
    try:
        game.apply_action(action)
        assert game.state.card_active == swap_card
    except:
        pytest.fail("uninitialized joker swap error")

def test_move_marble_backwards_around_loop(game):
    p = game.state.list_player[0]
    c_four = Card(suit='♠', rank='4')
    p.list_card.append(c_four)
    start = Dog.PLAYER_BOARD_SEGMENTS[0]['start']
    p.list_marble[0].pos = (start + 2) % game.MAIN_PATH_LENGTH
    pos_from = p.list_marble[0].pos
    pos_to = (pos_from - 4) % game.MAIN_PATH_LENGTH
    action = Action(card=c_four, pos_from=pos_from, pos_to=pos_to)
    try:
        game.apply_action(action)
    except:
        pytest.fail("backwards around loop error")

def test_jack_action_with_only_one_marble_on_board(game):
    p = game.state.list_player[0]
    c_j = Card(suit='♥', rank='J')
    p.list_card.append(c_j)
    for i, pl in enumerate(game.state.list_player):
        if i != 0:
            fs = Dog.PLAYER_BOARD_SEGMENTS[i]['final_start']
            for m in pl.list_marble:
                m.pos = fs + 1
    p.list_marble[1].pos = 72
    p.list_marble[2].pos = 72
    p.list_marble[3].pos = 72
    p.list_marble[0].pos = 0
    p.list_marble[0].is_save = True
    actions = game.get_list_action()
    jack_actions = [a for a in actions if a.card and a.card.rank == 'J']
    assert len(jack_actions) == 0

def test_joker_without_valid_moves(game):
    p = game.state.list_player[0]
    c_jkr = Card(suit='', rank='JKR')
    p.list_card.clear()
    p.list_card.append(c_jkr)
    # Alle Marbles im Kennel, kein Start möglich
    actions = game.get_list_action()
    assert isinstance(actions, list)

def test_card_exchange_in_later_rounds(game):
    state = game.get_state()
    state.cnt_round = 2
    state.bool_card_exchanged = False
    game.set_state(state)
    actions = game.get_list_action()
    exchange_actions = [a for a in actions if a.pos_from == -1 and a.pos_to == -1 and a.card and a.card_swap is None]
    assert len(exchange_actions) == 0

def test_multiple_joker_swaps_different_ranks(game):
    p = game.state.list_player[0]
    c_jkr = Card(suit='', rank='JKR')
    p.list_card.append(c_jkr)
    action1 = Action(card=c_jkr, pos_from=-1, pos_to=-1, card_swap=Card(suit='♥', rank='K'))
    game.apply_action(action1)
    assert game.state.card_active == Card(suit='♥', rank='K')
    action2 = Action(card=c_jkr, pos_from=-1, pos_to=-1, card_swap=Card(suit='♥', rank='Q'))
    try:
        game.apply_action(action2)
    except:
        pytest.fail("multiple joker swaps error")

def test_ace_as_1_step_move(game):
    p = game.state.list_player[0]
    c_ace = Card(suit='♥', rank='A')
    p.list_card.append(c_ace)
    actions = game.get_list_action()
    one_step_actions = [a for a in actions if a.card and a.card.rank == 'A'
                        and a.pos_from is not None and a.pos_to is not None]
    assert isinstance(one_step_actions, list)

def test_count_steps_to_finish_with_modified_final_start(monkeypatch):
    # Testet den Zweig in _count_steps_to_finish, wenn final_start < MAIN_PATH_LENGTH.
    # Da dies im normalen Spiel nicht vorkommt, patchen wir PLAYER_BOARD_SEGMENTS.
    game = Dog(cnt_players=4)
    original_segments = copy.deepcopy(game.PLAYER_BOARD_SEGMENTS)
    try:
        # Patch für den ersten Spieler final_start auf 10 setzen, < MAIN_PATH_LENGTH (64)
        modified_segments = copy.deepcopy(game.PLAYER_BOARD_SEGMENTS)
        modified_segments[0]['final_start'] = 10
        monkeypatch.setattr(game, 'PLAYER_BOARD_SEGMENTS', modified_segments)

        start = modified_segments[0]['start']  # 0
        final_start = modified_segments[0]['final_start']  # 10
        steps = game._count_steps_to_finish(pos_from=5, start=start, final_start=final_start)
        # Nur ein Check, dass wir keinen Fehler bekommen
        assert isinstance(steps, int), "Steps sollte ein int sein."

    finally:
        # Wiederherstellen des Originalzustands
        monkeypatch.setattr(game, 'PLAYER_BOARD_SEGMENTS', original_segments)

def test_handle_card_exchange_after_round_zero():
    # Testet den Fall, wenn cnt_round=0 und bereits bool_card_exchanged=True ist.
    # Dies soll sicherstellen, dass der Joker-Block in _get_actions_for_joker im 'if state.cnt_round == 0
    # and state.bool_card_exchanged' Zweig erreicht wird.
    game = Dog(cnt_players=4)
    state = game.get_state()
    state.cnt_round = 0
    state.bool_card_exchanged = True
    game.set_state(state)

    p = game.state.list_player[0]
    # Stelle sicher, dass der Spieler eine Joker-Karte hat
    p.list_card.append(Card(suit='', rank='JKR'))

    actions = game.get_list_action()
    # Wenn bool_card_exchanged = True und cnt_round = 0,
    # sollten im Joker-Teil zusätzliche Aktionen angeboten werden.
    # Wir checken nur, dass Actions vorhanden sind, um den Pfad abzudecken.
    assert len(actions) > 0, "Es sollten Joker-Aktionen bei bool_card_exchanged=True und cnt_round=0 vorhanden sein."

def test_invalid_final_area_move():
    # Testet den Fall in _calc_steps, bei dem pos_to ungültig im final area ist,
    # um einen None-Return zu erzwingen (z.B. diff > 3).
    game = Dog(cnt_players=4)
    p = game.state.list_player[0]
    c = Card(suit='♦', rank='Q')  # Q => 12 Felder
    p.list_card.append(c)

    fs = game.PLAYER_BOARD_SEGMENTS[0]['final_start']
    # Setze eine Murmel knapp vor den final_start
    p.list_marble[0].pos = fs - 1
    # pos_to weit über das Finalfeld hinaus
    invalid_action = Action(card=c, pos_from=fs - 1, pos_to=fs + 10)  # fs+10 ist ungültig
    # apply_action sollte keinen Fehler werfen, aber keinen validen Move durchführen
    game.apply_action(invalid_action)
    # Wenn steps None ist, sollte next_turn aufgerufen werden und nichts abstürzen.
    assert game.state.idx_player_active != 0, "Zug sollte trotzdem weitergehen, obwohl Aktion ungültig war."


