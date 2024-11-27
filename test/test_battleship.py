import pytest

from server.py.battleship import (
    Battleship,
    Ship,
    BattleshipAction,
    ActionType,
    GamePhase,
    RandomPlayer,
    PlayerState,
)


def test_initialize_game() -> None:
    game = Battleship()
    assert game.state.phase == GamePhase.SETUP
    assert len(game.state.players) == 2
    assert game.state.idx_player_active == 0
    assert game.state.winner is None


def test_validate_ship_placement() -> None:
    game = Battleship()

    # Valid placement
    ship = Ship(name="destroyer", length=2, location=["A1", "A2"])
    assert game.validate_ship_placement(ship)

    # Simulate placing the ship
    game.state.players[0].ships.append(ship)

    # Invalid: Overlapping
    overlapping_ship = Ship(name="submarine", length=3, location=["A2", "A3", "A4"])
    assert not game.validate_ship_placement(overlapping_ship)

    # Invalid: Diagonal placement
    diagonal_ship = Ship(name="cruiser", length=3, location=["A1", "B2", "C3"])
    assert not game.validate_ship_placement(diagonal_ship)

    # Clean up game state after the test
    game.state.players[0].ships = []


def test_validate_shot() -> None:
    game = Battleship()
    assert game.validate_shot("A1")

    # Invalid: Out of bounds
    assert not game.validate_shot("K1")
    assert not game.validate_shot("A11")

    # Invalid: Duplicate shot
    game.state.players[0].shots.append("A1")
    assert not game.validate_shot("A1")


def test_apply_ship_action() -> None:
    game = Battleship()
    action = BattleshipAction(
        action_type=ActionType.SET_SHIP,
        ship_name="destroyer",
        location=["A1", "A2"]
    )
    game.apply_action(action)
    assert len(game.state.players[0].ships) == 1
    assert game.state.idx_player_active == 1


def test_get_list_action() -> None:
    game = Battleship()

    # Setup actions
    actions = game.get_list_action()
    assert len(actions) > 0
    assert all(action.action_type == ActionType.SET_SHIP for action in actions)

    # Transition to shooting phase
    game.state.phase = GamePhase.RUNNING
    shooting_actions = game.get_list_action()
    assert len(shooting_actions) == 100  # 10x10 board


def test_ship_placement_edge_of_board() -> None:
    game = Battleship()
    action = BattleshipAction(
        action_type=ActionType.SET_SHIP,
        ship_name="destroyer",
        location=["J9", "J10"]  # Edge of the board
    )
    game.apply_action(action)
    assert len(game.state.players[0].ships) == 1


def test_invalid_shoot_action() -> None:
    game = Battleship()
    action = BattleshipAction(
        action_type=ActionType.SHOOT,
        location=["Z9"],
        ship_name=None
    )
    with pytest.raises(ValueError):
        game.apply_action(action)


def test_edge_case_placement() -> None:
    game = Battleship()
    # Top-left corner horizontal placement
    action = BattleshipAction(
        action_type=ActionType.SET_SHIP,
        ship_name="destroyer",
        location=["A1", "A2"]
    )
    game.apply_action(action)
    assert len(game.state.players[0].ships) == 1

    # Bottom-right corner vertical placement
    action = BattleshipAction(
        action_type=ActionType.SET_SHIP,
        ship_name="submarine",
        location=["J8", "J9", "J10"]
    )
    game.apply_action(action)
    assert len(game.state.players[0].ships) == 1


def test_invalid_shot_location() -> None:
    game = Battleship()
    with pytest.raises(ValueError):
        action = BattleshipAction(
            action_type=ActionType.SHOOT,
            ship_name=None,
            location=["Z9"]  # Out of board
        )
        game.apply_action(action)

    with pytest.raises(ValueError):
        action = BattleshipAction(
            action_type=ActionType.SHOOT,
            ship_name=None,
            location=["A11"]  # Out of board
        )
        game.apply_action(action)


def test_game_restart() -> None:
    game = Battleship()
    game.state.phase = GamePhase.FINISHED
    game.state.winner = 0
    game.__init__()  # Reinitialize the game
    assert game.state.phase == GamePhase.SETUP
    assert game.state.winner is None
    assert len(game.state.players[0].ships) == 0
    assert len(game.state.players[1].ships) == 0


def test_list_action_invalid_phase() -> None:
    game = Battleship()
    game.state.phase = GamePhase.FINISHED
    actions = game.get_list_action()
    assert len(actions) == 0


def test_get_masked_player_state() -> None:
    game = Battleship()
    game.state.phase = GamePhase.RUNNING
    state = game.get_player_view(idx_player=0)
    assert len(state.players[1].ships) == 0  # Opponent ships should not be visible


def test_random_player_selection() -> None:
    game = Battleship()
    random_player = RandomPlayer()
    game.state.phase = GamePhase.RUNNING
    actions = game.get_list_action()
    action = random_player.select_action(game.state, actions)
    assert action in actions


def test_shoot_already_hit_location() -> None:
    game = Battleship()
    game.state.phase = GamePhase.RUNNING
    game.state.players[0].shots.append("A1")
    game.state.players[0].successful_shots.append("A1")
    action = BattleshipAction(action_type=ActionType.SHOOT, location=["A1"], ship_name=None)
    with pytest.raises(ValueError):
        game.apply_action(action)


def test_invalid_ship_name() -> None:
    """Test ship placement with an invalid ship name."""
    game = Battleship()
    action = BattleshipAction(
        action_type=ActionType.SET_SHIP,
        ship_name="invalid_ship",
        location=["A1", "A2"]
    )
    with pytest.raises(ValueError, match="Invalid ship name"):
        game.apply_action(action)


def test_no_actions_available() -> None:
    """Test behavior when no actions are available."""
    game = Battleship()
    game.state.phase = GamePhase.FINISHED  # No actions in finished phase
    actions = game.get_list_action()
    assert len(actions) == 0


def test_reset_shots() -> None:
    """Test player shot reset."""
    game = Battleship()
    player = game.state.players[0]
    player.shots.extend(["A1", "B2"])
    player.successful_shots.append("C3")

    player.reset_shots()
    assert len(player.shots) == 0
    assert len(player.successful_shots) == 0


def test_player_view_masking() -> None:
    """Test player view masking."""
    game = Battleship()
    game.state.players[1].shots.append("A1")
    game.state.players[1].successful_shots.append("B2")

    state = game.get_player_view(idx_player=0)
    assert len(state.players[1].ships) == 0  # Opponent ships are hidden
    assert state.players[1].successful_shots == ["hit"]  # Hits are masked
    assert state.players[0].ships == game.state.players[0].ships  # Own ships are visible


def test_phase_transition_to_finished() -> None:
    """Test phase transitions from RUNNING to FINISHED."""
    game = Battleship()
    # Setup a finished state
    game.state.phase = GamePhase.RUNNING
    opponent = game.state.players[1]
    opponent.ships = [
        Ship(name="destroyer", length=2, location=["A1", "A2"])
    ]
    game.state.players[0].successful_shots.extend(["A1", "A2"])
    game.check_and_update_phase()
    assert game.state.phase == GamePhase.FINISHED
    assert game.state.winner == 0


def test_count_remaining_ships() -> None:
    """Test counting remaining ships."""
    player = PlayerState(
        name="Player 1",
        ships=[
            Ship(name="destroyer", length=2, location=["A1", "A2"]),
            Ship(name="submarine", length=3, location=["B1", "B2", "B3"]),
        ],
        shots=[],
        successful_shots=["A1", "A2", "B1"]
    )
    assert player.count_remaining_ships() == 1  # Only the submarine remains
