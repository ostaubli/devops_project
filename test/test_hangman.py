import pytest

from server.py.hangman import (
    Hangman,
    GuessLetterAction,
    HangmanGameState,
    GamePhase,
    RandomPlayer,
)

def test_initialize_game() -> None:
    """Test initializing the Hangman game."""
    game = Hangman()
    assert game.state is None
    assert game.display_word == []


def test_set_state() -> None:
    """Test setting the game state."""
    game = Hangman()
    state = HangmanGameState(
        word_to_guess="PYTHON",
        phase=GamePhase.RUNNING,
        guesses=[],
        incorrect_guesses=[]
    )
    game.set_state(state)
    assert game.state == state
    assert game.display_word == ["_", "_", "_", "_", "_", "_"]


def test_apply_action_correct_guess() -> None:
    """Test applying a correct guess action."""
    game = Hangman()
    state = HangmanGameState(
        word_to_guess="PYTHON",
        phase=GamePhase.RUNNING,
        guesses=[],
        incorrect_guesses=[]
    )
    game.set_state(state)
    action = GuessLetterAction("P")
    game.apply_action(action)
    assert game.state.guesses == ["P"]
    assert game.display_word == ["P", "_", "_", "_", "_", "_"]


def test_apply_action_incorrect_guess() -> None:
    """Test applying an incorrect guess action."""
    game = Hangman()
    state = HangmanGameState(
        word_to_guess="PYTHON",
        phase=GamePhase.RUNNING,
        guesses=[],
        incorrect_guesses=[]
    )
    game.set_state(state)
    action = GuessLetterAction("X")
    game.apply_action(action)
    assert game.state.incorrect_guesses == ["X"]
    assert game.display_word == ["_", "_", "_", "_", "_", "_"]


def test_apply_action_game_won() -> None:
    """Test transitioning to FINISHED phase on game win."""
    game = Hangman()
    state = HangmanGameState(
        word_to_guess="PYTHON",
        phase=GamePhase.RUNNING,
        guesses=["P", "Y", "T", "H", "O"],
        incorrect_guesses=[]
    )
    game.set_state(state)
    action = GuessLetterAction("N")
    game.apply_action(action)
    assert game.state.phase == GamePhase.FINISHED
    assert game.display_word == ["P", "Y", "T", "H", "O", "N"]

def test_apply_action_game_lost() -> None:
    """Test transitioning to FINISHED phase on game loss."""
    game = Hangman()
    state = HangmanGameState(
        word_to_guess="PYTHON",
        phase=GamePhase.RUNNING,
        guesses=[],
        incorrect_guesses=["A", "B", "C", "D", "E", "F", "G"]
    )
    game.set_state(state)

    # Add a guess to reach MAX_INCORRECT_GUESSES
    action = GuessLetterAction("X")
    game.apply_action(action)

    # Assert phase transition
    assert len(game.state.incorrect_guesses) == 8
    assert game.state.phase == GamePhase.FINISHED

def test_get_state() -> None:
    """Test retrieving the current game state."""
    game = Hangman()
    state = HangmanGameState(
        word_to_guess="PYTHON",
        phase=GamePhase.RUNNING,
        guesses=["P", "Y"],
        incorrect_guesses=["A", "B"]
    )
    game.set_state(state)
    retrieved_state = game.get_state()
    assert retrieved_state == state

def test_set_state_word_already_guessed() -> None:
    """Test setting the state where the word is already fully guessed."""
    game = Hangman()
    state = HangmanGameState(
        word_to_guess="PYTHON",
        phase=GamePhase.RUNNING,
        guesses=["P", "Y", "T", "H", "O", "N"],
        incorrect_guesses=[]
    )
    game.set_state(state)
    assert game.state.phase == GamePhase.FINISHED

def test_random_player_selection() -> None:
    """Test random player making a valid guess."""
    game = Hangman()
    state = HangmanGameState(
        word_to_guess="PYTHON",
        phase=GamePhase.RUNNING,
        guesses=["P"],
        incorrect_guesses=["X"]
    )
    game.set_state(state)
    actions = game.get_list_action()
    random_player = RandomPlayer()
    action = random_player.select_action(actions)
    assert action is not None
    assert action.letter not in state.guesses + state.incorrect_guesses


def test_reset_guesses_random_player() -> None:
    """Test resetting guesses for the random player."""
    random_player = RandomPlayer()
    random_player.past_guesses.update(["P", "Y", "X"])
    random_player.reset_guesses()
    assert random_player.get_past_guesses() == set()