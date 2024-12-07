import pytest
from server.py.hangman import Hangman, HangmanGameState, GamePhase, GuessLetterAction, RandomPlayer

@pytest.fixture
def game():
    """Fixture to create a new game instance for testing."""
    return Hangman()

def test_initialization(game):
    """Test the game initializes with the correct default state."""
    state = game.get_state()
    assert state.word_to_guess == ''
    assert state.phase == GamePhase.SETUP
    assert state.guesses == []
    assert state.incorrect_guesses == []

def test_set_state(game):
    """Test setting a new game state."""
    new_state = HangmanGameState(
        word_to_guess='PYTHON',
        phase=GamePhase.SETUP,
        guesses=[],
        incorrect_guesses=[]
    )
    game.set_state(new_state)
    state = game.get_state()
    assert state.word_to_guess == 'PYTHON'
    assert state.phase == GamePhase.SETUP

def test_apply_action_correct_guess(game):
    """Test applying a correct guess action."""
    game.set_state(HangmanGameState(
        word_to_guess='PYTHON',
        phase=GamePhase.RUNNING,
        guesses=[],
        incorrect_guesses=[]
    ))
    action = GuessLetterAction(letter='P')
    game.apply_action(action)
    state = game.get_state()
    assert 'P' in state.guesses
    assert len(state.incorrect_guesses) == 0

def test_apply_action_incorrect_guess(game):
    """Test applying an incorrect guess action."""
    game.set_state(HangmanGameState(
        word_to_guess='PYTHON',
        phase=GamePhase.RUNNING,
        guesses=[],
        incorrect_guesses=[]
    ))
    action = GuessLetterAction(letter='Z')
    game.apply_action(action)
    state = game.get_state()
    assert 'Z' in state.incorrect_guesses
    assert len(state.guesses) == 1

def test_win_condition(game):
    """Test the game correctly transitions to FINISHED on win."""
    game.set_state(HangmanGameState(
        word_to_guess='PYTHON',
        phase=GamePhase.RUNNING,
        guesses=['P', 'Y', 'T', 'H', 'O', 'N'],
        incorrect_guesses=[]
    ))
    action = GuessLetterAction(letter='N')
    game.apply_action(action)
    state = game.get_state()
    assert state.phase == GamePhase.FINISHED

def test_loss_condition(game):
    """Test the game correctly transitions to FINISHED on loss."""
    game.set_state(HangmanGameState(
        word_to_guess='PYTHON',
        phase=GamePhase.RUNNING,
        guesses=[],
        incorrect_guesses=['A', 'B', 'C', 'D', 'E', 'F', 'G']
    ))
    action = GuessLetterAction(letter='I')
    game.apply_action(action)
    state = game.get_state()
    assert state.phase == GamePhase.FINISHED

def test_random_player_action_selection(game):
    """Test the RandomPlayer selects a valid action."""
    game.set_state(HangmanGameState(
        word_to_guess='PYTHON',
        phase=GamePhase.RUNNING,
        guesses=['P', 'Y'],
        incorrect_guesses=[]
    ))
    player = RandomPlayer()
    actions = game.get_list_action()
    action = player.select_action(game.get_state(), actions)
    assert action.letter not in ['P', 'Y']
    assert action.letter in [a.letter for a in actions]