import pytest
from server.py.dog import Dog, Card, Marble, Dog, Action, GameState, GamePhase, GuessLetterAction, RandomPlayer

@pytest.fixture
def game():
    """Fixture to create a new game instance for testing."""
    return Dog()
