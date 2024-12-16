import pytest
from server.py.dog import (
    Dog, Card, Marble, PlayerState, Action, GameState, GamePhase, RandomPlayer
)
from server.py.game import Player
import copy


@pytest.fixture
def game():
    # Erstellt ein Dog-Spiel mit der Standardanzahl von 4 Spielern
    return Dog(cnt_players=4)

# -------------------------------------------------------
# Modell- und Datenklassen-Tests (Card, Marble, PlayerState, Action)
# -------------------------------------------------------


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


# -------------------------------------------------------
# GamePhase und GameState Tests
# -------------------------------------------------------


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


# -------------------------------------------------------
# Dog-Game Grundfunktionalitäten
# -------------------------------------------------------


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
    # Runde künstlich verändern
    game.state.cnt_round = 2
    old_len = len(game.state.list_player[0].list_card)
    game.setup_next_round()
    assert len(game.state.list_player[0].list_card) >= old_len


def test_next_turn(game):
    old_active = game.state.idx_player_active
    game.next_turn()
    assert game.state.idx_player_active != old_active


def test_player_finished(game):
    # Niemand sollte am Anfang fertig sein.
    assert not game._player_finished(0)


def test_controlled_player_indices(game):
    indices = game._controlled_player_indices()
    assert isinstance(indices, list)


def test_get_player_marbles(game):
    marbles = game._get_player_marbles()
    assert isinstance(marbles, list)
    assert len(marbles) > 0


# -------------------------------------------------------
# Kartenaktionen und Hilfsfunktionen
# -------------------------------------------------------


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
    c = Card(suit='♥', rank='5')  # 5 = 5 Felder
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

# -------------------------------------------------------
# Aktionen ausführen, spezielle Kartenbewegungen (Joker, 7er, Jack)
# -------------------------------------------------------
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


def test_handle_active_card_move(game):
    p = game.state.list_player[0]
    c = Card(suit='♥', rank='Q')
    p.list_card.append(c)
    action = Action(card=c, pos_from=64, pos_to=0)
    game._handle_active_card_move(p, action)


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


