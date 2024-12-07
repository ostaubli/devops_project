import pytest
from server.py.dog import Dog, GameState, GamePhase, Action, Card

@pytest.fixture
def game_instance():
    """Fixture to create a fresh instance of the Dog game."""
    return Dog()

def test_initial_game_state(game_instance):
    """Test if the game initializes correctly."""
    state = game_instance.get_state()
    assert state.phase == GamePhase.RUNNING
    assert len(state.list_player) == 4
    assert len(state.list_card_draw) > 0
    assert all(len(player.list_card) == 6 for player in state.list_player)
    assert all(len(player.list_marble) == 4 for player in state.list_player)

