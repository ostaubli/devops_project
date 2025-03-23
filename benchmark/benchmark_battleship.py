from typing import List
import sys
import string
from benchmark import Benchmark
from server.py.battleship import BattleshipGameState, PlayerState, Ship, BattleshipAction, ActionType, GamePhase


class BattleshipBenchmark(Benchmark):

    VALID_LOCATIONS = [x_name + str(y_name) for x_name in list(string.ascii_uppercase)[:10] for y_name in range(1, 11)]

    def play_first_n_rounds(self, num_rounds: int) -> None:
        self.game_server.reset()
        for _ in range(num_rounds):
            game_state = self.game_server.get_state()
            if game_state.phase == GamePhase.FINISHED:
                break
            action = self.game_server.select_action()
            self.game_server.apply_action(action)

    def test_initial_game_state_structure(self) -> None:
        """Test 001: Validate structure of initial game state [1 points]"""
        self.game_server.reset()
        state = self.game_server.get_state()
        assert len(state.players) == 2, f"Error: There is/are {len(state.players)} players, should be 2"
        for player in state.players:
            assert player.shots == [], f"Error: Shots of '{player.name}' are not empty"
            for ship in  player.ships:
                assert ship.location is None, f"Error: Ship '{ship.name}' of player '{player.name}' is already set"

    def test_set_state_method(self) -> None:
        """Test 002: Set/get methods work properly [1 point]"""
        self.game_server.reset()
        ship = Ship(name='destroyer', length=2, location=['A1','A2'])
        player0 = PlayerState(name='Player 1', ships=[ship], shots=[], successful_shots=[])
        player1 = PlayerState(name='Player 2', ships=[], shots=[], successful_shots=[])
        state = BattleshipGameState(idx_player_active=1, phase=GamePhase.SETUP, winner=None, players=[player0, player1])
        self.game_server.set_state(state)
        game_state = self.game_server.get_state()
        hint = "Applying 'set_state' and then 'get_state' returns a different state"
        assert state.idx_player_active == game_state.idx_player_active, hint
        assert state.phase == game_state.phase, hint
        assert state.winner == game_state.winner, hint
        assert state.players[0].name == game_state.players[0].name, hint
        assert len(state.players[0].ships) == len(game_state.players[0].ships), hint
        assert state.players[0].ships[0].name == game_state.players[0].ships[0].name, hint
        assert state.players[0].ships[0].length == game_state.players[0].ships[0].length, hint
        assert state.players[0].ships[0].location == game_state.players[0].ships[0].location, hint
        assert state.players[0].shots == game_state.players[0].shots, hint
        assert state.players[0].successful_shots == game_state.players[0].successful_shots, hint
        assert state.players[1].name == game_state.players[1].name, hint
        assert len(state.players[1].ships) == len(game_state.players[1].ships), hint
        assert state.players[1].shots == game_state.players[1].shots, hint
        assert state.players[1].successful_shots == game_state.players[1].successful_shots, hint

    def test_apply_ship_placement_action(self) -> None:
        """Test 003: Apply set ship action works correctly [1 point]"""
        self.game_server.reset()
        ship = Ship(name='destroyer', length=2, location=['A1','A2'])
        player0 = PlayerState(name='Player 1', ships=[ship], shots=[], successful_shots=[])
        player1 = PlayerState(name='Player 2', ships=[], shots=[], successful_shots=[])
        state = BattleshipGameState(idx_player_active=1, phase=GamePhase.SETUP, winner=None, players=[player0, player1])
        self.game_server.set_state(state)
        action = BattleshipAction(action_type=ActionType.SET_SHIP, ship_name='submarine', location=["C5","D5","E5"])
        self.game_server.apply_action(action)
        game_state = self.game_server.get_state()
        assert game_state.idx_player_active == 0, "After apply_action, the 'idx_player_active' should change"
        assert state.phase == GamePhase.SETUP, "State attribute 'phase' should be SETUP"
        assert state.winner is None, "State attribute 'winner' doesn't work correctly"
        hint_player_changed = "Only the state of the active player should change!"
        assert state.players[0].name == game_state.players[0].name, hint_player_changed
        assert len(state.players[0].ships) == len(game_state.players[0].ships), hint_player_changed
        assert state.players[0].ships[0].name == game_state.players[0].ships[0].name, hint_player_changed
        assert state.players[0].ships[0].length == game_state.players[0].ships[0].length, hint_player_changed
        assert state.players[0].ships[0].location == game_state.players[0].ships[0].location, hint_player_changed
        assert state.players[0].shots == game_state.players[0].shots, hint_player_changed
        assert state.players[0].successful_shots == game_state.players[0].successful_shots, hint_player_changed
        assert state.players[1].name == game_state.players[1].name, "Player name should not change"
        hint_apply_error = "Set ship action not correctly applied"
        assert len(game_state.players[1].ships) == 1, hint_apply_error
        assert game_state.players[1].ships[0].name == 'submarine', hint_apply_error
        assert game_state.players[1].ships[0].length == 3, hint_apply_error
        assert game_state.players[1].ships[0].location == ["C5","D5","E5"], hint_apply_error
        assert state.players[1].shots == game_state.players[1].shots, hint_apply_error
        assert state.players[1].successful_shots == game_state.players[1].successful_shots, hint_apply_error

    def test_ships_locations(self) -> None:
        """Test 004: Correct ship location names [1 point]"""
        for _ in range(10):
            self.play_first_n_rounds(10)
            state = self.game_server.get_state()
            for player in state.players:
                assert len(player.ships) == 5, f"Error: Player '{player.name}' doesn't have 5 ships"
                for ship in  player.ships:
                    for field in ship.location:
                        assert field in self.VALID_LOCATIONS, f"Error: '{field}' is not a valid location"

    def test_ships_length(self) -> None:
        """Test 005: Ships with correct length [3 point]"""
        self.game_server.reset()
        self.play_first_n_rounds(10)
        state = self.game_server.get_state()
        for player in state.players:
            ship_lengths = sorted([ship.length for ship in player.ships])
            assert ship_lengths == [2,3,3,4,5], "Error: There have to be ships with exactly these lengths: 2,3,3,4,5"

    def test_ships_not_overlapping(self) -> None:
        """Test 006: Ships are not overlapping [2 point]"""
        for _ in range(10):
            self.play_first_n_rounds(10)
            state = self.game_server.get_state()
            for player in state.players:
                locations = [loc for ship in player.ships for loc in ship.location]
                assert len(locations) == len(set(locations)), "Error: Some ship locations are overlapping"

    def test_ships_vertical_and_horizontal(self) -> None:
        """Test 007: Ships are located vertical and horizontal [1 point]"""
        vertical = False
        horizontal = False
        for _ in range(10):
            self.play_first_n_rounds(10)
            state = self.game_server.get_state()
            for player in state.players:
                for ship in player.ships:
                    x_coord = set(field[0] for field in ship.location)
                    y_coord = set(field[1:] for field in ship.location)
                    if len(x_coord) == 1:
                        horizontal = True
                    elif len(y_coord) == 1:
                        vertical = True
        assert horizontal, "Error: Ships are only located vertically"
        assert vertical, "Error: Ships are only located horizontally"

    def test_ships_placements_changing(self) -> None:
        """Test 008: Location of ships is different on each run [1 point]"""
        states: List[BattleshipGameState] = []
        equals = 0
        for _ in range(10):
            self.play_first_n_rounds(10)
            state = self.game_server.get_state()
            state.idx_player_active = 0
            for past_state in states:
                if past_state == state:
                    equals += 1
            states.append(state)
        assert equals < 3, "Error: Location of ships does not change"

    def test_ships_all_set_after_10_rounds(self) -> None:
        """Test 009: After the first 10 rounds all ships are located [1 point]"""
        self.play_first_n_rounds(10)
        state = self.game_server.get_state()
        for player in state.players:
            for ship in player.ships:
                assert ship.location is not None, f"Ship {ship.name} is not located after the first 10 rounds"
        assert state.phase == GamePhase.RUNNING, "After setting all ships, game shoud be in RUNNING phase"

    def test_shots_no_shots_first_10_rounds(self) -> None:
        """Test 010: No shots fired in the first 10 rounds [1 point]"""
        self.play_first_n_rounds(10)
        state = self.game_server.get_state()
        for player in state.players:
            assert len(player.shots) == 0, f"Player '{player.name}' fired too soon!"

    def test_shots_correct_actions(self) -> None:
        """Test 011: Correct shoot options [1 point]"""
        self.play_first_n_rounds(10)
        options = []
        for action in self.game_server.game.get_list_action():
            assert action.action_type == 'shoot', "After 10 rounds, game should return shoot actions"
            assert action.ship_name is None, "A shoot action, cannot have a ship name"
            assert len(action.location) == 1, "Shoot actions must have a single location"
            options.extend(action.location)
        assert len(set(options).symmetric_difference(set(self.VALID_LOCATIONS))) == 0, "Invalid shoot locations"

    def test_apply_shoot_action(self) -> None:
        """Test 012: Apply shoot action works correctly [1 point]"""
        self.game_server.reset()
        ships = [
            Ship(name="carrier", length=5, location=["A1", "A2", "A3", "A4", "A5"]),
            Ship(name="battleship", length=4, location=["B1", "B2", "B3", "B4"]),
            Ship(name="cruiser", length=3, location=["C1", "C2", "C3"]),
            Ship(name="submarine", length=3, location=["D1", "D2", "D3"]),
            Ship(name="destroyer", length=2, location=["E1", "E2"]),
        ]
        player0 = PlayerState(name='Player 1', ships=ships, shots=["A8"], successful_shots=[])
        player1 = PlayerState(name='Player 2', ships=ships, shots=[], successful_shots=[])
        state = BattleshipGameState(idx_player_active=1, phase=GamePhase.RUNNING, winner=None, players=[player0, player1])
        self.game_server.set_state(state)
        action = BattleshipAction(action_type=ActionType.SHOOT, ship_name=None, location=["A2"])
        self.game_server.apply_action(action)
        game_state = self.game_server.get_state()
        assert game_state.idx_player_active == 0, "After apply_action, the 'idx_player_active' should change"
        assert state.phase == GamePhase.RUNNING, "State attribute 'phase' should be RUNNING"
        assert state.winner is None, "State attribute 'winner' doesn't work correctly"
        hint_player_changed = "Only the state of the active player should change!"
        assert state.players[0].name == game_state.players[0].name, hint_player_changed
        assert len(state.players[0].ships) == len(game_state.players[0].ships), hint_player_changed
        assert state.players[0].shots == game_state.players[0].shots, hint_player_changed
        assert state.players[0].successful_shots == game_state.players[0].successful_shots, hint_player_changed
        assert state.players[1].name == game_state.players[1].name, "Player name should not change"
        assert len(game_state.players[1].ships) == 5, "Shoot action should not change ships"
        assert state.players[1].shots == ["A2"], "Shoot action not correctly registered"
        assert state.players[1].successful_shots == ["A2"], "Shoot action not correctly registered"

    def test_shots_remember_targets(self) -> None:
        """Test 013: Remember areas already targeted [1 point]"""
        self.play_first_n_rounds(210)
        state = self.game_server.get_state()
        for player in state.players:
            assert len(set(player.shots)) == len(player.shots), "One target location has already been fired at once"


if __name__ == '__main__':

    benchmark = BattleshipBenchmark(sys.argv)
    benchmark.run_tests()
