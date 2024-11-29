import pytest
from server.py.battleship import Battleship, BattleshipGameState, GamePhase, BattleshipAction, ActionType, PlayerState, Ship

def test_initial_state():
    game = Battleship()
    assert game.state.phase == GamePhase.SETUP
    assert game.state.idx_player_active == 0
    assert len(game.state.players) == 2

def test_set_state_method():
    game = Battleship()
    state = BattleshipGameState(
        idx_player_active=0,
        phase=GamePhase.SETUP,
        players=[
            PlayerState(name="Player 1"),
            PlayerState(name="Player 2"),
        ]
    )
    game.set_state(state)
    retrieved_state = game.get_state()
    assert state.idx_player_active == retrieved_state.idx_player_active
    assert state.phase == retrieved_state.phase
    assert state.players == retrieved_state.players

def test_set_ship():
    game = Battleship()
    game.state.players[0].ships.append(Ship(name="Destroyer", length=2, location=["A1", "A2"]))
    assert len(game.state.players[0].ships) == 1
    assert game.state.players[0].ships[0].name == "Destroyer"
    assert game.state.players[0].ships[0].location == ["A1", "A2"]

def test_apply_action_set_ship():
    game = Battleship()
    action = BattleshipAction(action_type=ActionType.SET_SHIP, ship_name="Destroyer", location=["A1", "A2"])
    game.apply_action(action)
    assert len(game.state.players[0].ships) == 1
    assert game.state.players[0].ships[0].name == "Destroyer"
    assert game.state.players[0].ships[0].location == ["A1", "A2"]

def test_apply_action_shoot():
    game = Battleship()
    game.state.phase = GamePhase.RUNNING
    game.state.players[1].ships.append(Ship(name="Destroyer", length=2, location=["A1", "A2"]))
    action = BattleshipAction(action_type=ActionType.SHOOT, location=["A1"])
    game.apply_action(action)
    assert "A1" in game.state.players[0].successful_shots

def test_check_winner():
    game = Battleship()
    game.state.players[1].ships.append(Ship(name="Destroyer", length=2, location=["A1", "A2"]))
    action1 = BattleshipAction(action_type=ActionType.SHOOT, location=["A1"])
    action2 = BattleshipAction(action_type=ActionType.SHOOT, location=["A2"])
    game.apply_action(action1)
    game.apply_action(action2)
    assert game.check_winner() == 0

def test_is_game_over():
    game = Battleship()
    game.state.players[1].ships.append(Ship(name="Destroyer", length=2, location=["A1", "A2"]))
    action1 = BattleshipAction(action_type=ActionType.SHOOT, location=["A1"])
    action2 = BattleshipAction(action_type=ActionType.SHOOT, location=["A2"])
    game.apply_action(action1)
    game.apply_action(action2)
    assert game.is_game_over() is True

def test_apply_action_correct_guess():
    game = Battleship()
    state = BattleshipGameState(
        idx_player_active=0,
        phase=GamePhase.RUNNING,
        players=[
            PlayerState(name="Player 1", ships=[Ship(name="Carrier", length=5, location=["A1", "A2", "A3", "A4", "A5"])], shots=[], successful_shots=[]),
            PlayerState(name="Player 2", ships=[], shots=[], successful_shots=[]),
        ]
    )
    game.set_state(state)
    action = BattleshipAction(action_type=ActionType.SHOOT, location=["A1"])
    game.apply_action(action)
    assert "A1" in game.state.players[0].successful_shots
    assert game.state.players[0].ships[0].location == ["A2", "A3", "A4", "A5"]

def test_apply_action_incorrect_guess():
    game = Battleship()
    state = BattleshipGameState(
        idx_player_active=0,
        phase=GamePhase.RUNNING,
        players=[
            PlayerState(name="Player 1", ships=[Ship(name="Carrier", length=5, location=["A1", "A2", "A3", "A4", "A5"])], shots=[], successful_shots=[]),
            PlayerState(name="Player 2", ships=[], shots=[], successful_shots=[]),
        ]
    )
    game.set_state(state)
    action = BattleshipAction(action_type=ActionType.SHOOT, location=["B1"])
    game.apply_action(action)
    assert "B1" in game.state.players[0].shots
    assert game.state.players[0].ships[0].location == ["A1", "A2", "A3", "A4", "A5"]

def test_print_state(capsys):
    game = Battleship()
    game.print_state()
    captured = capsys.readouterr()
    assert "Game Phase: GamePhase.SETUP" in captured.out
    assert "Active Player: 1" in captured.out
    assert "Player 1:" in captured.out
    assert "Player 2:" in captured.out

def test_set_state():
    game = Battleship()
    state = BattleshipGameState(
        idx_player_active=1,
        phase=GamePhase.RUNNING,
        players=[
            PlayerState(name="Player 1"),
            PlayerState(name="Player 2"),
        ]
    )
    game.set_state(state)
    assert game.state.idx_player_active == 1
    assert game.state.phase == GamePhase.RUNNING
    assert game.state.players[0].name == "Player 1"
    assert game.state.players[1].name == "Player 2"

def test_get_state():
    game = Battleship()
    state = game.get_state()
    assert state.idx_player_active == 0
    assert state.phase == GamePhase.SETUP
    assert len(state.players) == 2

def test_get_list_action_setup():
    game = Battleship()
    game.state.phase = GamePhase.SETUP
    actions = game.get_list_action()
    assert len(actions) > 0
    for action in actions:
        assert action.action_type == ActionType.SET_SHIP

def test_get_list_action_running():
    game = Battleship()
    game.state.phase = GamePhase.RUNNING
    game.state.players[0].shots = ["A1", "A2"]
    actions = game.get_list_action()
    assert len(actions) > 0
    for action in actions:
        assert action.action_type == ActionType.SHOOT
        assert action.location[0] not in ["A1", "A2"]

def test_draw_board(capsys):
    game = Battleship()
    game.draw_board()
    captured = capsys.readouterr()
    assert "Board:" in captured.out
    assert len(captured.out.splitlines()) > 0

def test_draw_card():
    game = Battleship()
    game.state.phase = GamePhase.RUNNING
    game.state.list_id_card_draw = [BattleshipAction(action_type=ActionType.SHOOT, location=["A1"])]
    game.draw_card()
    assert len(game.state.list_id_card_draw) == 0
    assert len(game.state.players[0].shots) == 1

def test_get_player_view():
    game = Battleship()
    view = game.get_player_view(0)
    assert view.idx_player_active == game.state.idx_player_active
    assert view.phase == game.state.phase
    assert len(view.players) == len(game.state.players)