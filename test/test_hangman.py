import pytest
import string
from server.py.hangman import Hangman, HangmanGameState, GamePhase, GuessLetterAction, RandomPlayer


def test_apply_action_with_multiple_guesses():
    game = Hangman()
    state = HangmanGameState(word_to_guess='hangman', guesses=['H', 'A'], incorrect_guesses=['B', 'C'], phase=GamePhase.RUNNING)
    game.set_state(state)
    game.apply_action(GuessLetterAction(letter='g'))
    retrieved_state = game.get_state()
    assert 'G' in retrieved_state.guesses
    assert retrieved_state.phase == GamePhase.RUNNING


def test_apply_action_all_correct_guesses():
    game = Hangman()
    state = HangmanGameState(word_to_guess='hello', guesses=['H', 'E', 'L'], incorrect_guesses=['A', 'B'], phase=GamePhase.RUNNING)
    game.set_state(state)
    game.apply_action(GuessLetterAction(letter='o'))
    retrieved_state = game.get_state()
    assert 'O' in retrieved_state.guesses
    assert retrieved_state.phase == GamePhase.FINISHED


def test_restart_game_after_finish():
    game = Hangman()
    state = HangmanGameState(word_to_guess='world', guesses=['W', 'O', 'R', 'L', 'D'], incorrect_guesses=[], phase=GamePhase.FINISHED)
    game.set_state(state)
    game.reset()
    assert game._state is None
    new_state = HangmanGameState(word_to_guess='python', guesses=[], incorrect_guesses=[], phase=GamePhase.RUNNING)
    game.set_state(new_state)
    assert game.get_state().word_to_guess == 'PYTHON'
    assert game.get_state().phase == GamePhase.RUNNING


def test_apply_action_after_reset():
    game = Hangman()
    state = HangmanGameState(word_to_guess='reset', guesses=['R', 'E'], incorrect_guesses=['A', 'B'], phase=GamePhase.RUNNING)
    game.set_state(state)
    game.reset()
    new_state = HangmanGameState(word_to_guess='restart', guesses=[], incorrect_guesses=[], phase=GamePhase.RUNNING)
    game.set_state(new_state)
    game.apply_action(GuessLetterAction(letter='r'))
    retrieved_state = game.get_state()
    assert 'R' in retrieved_state.guesses
    assert retrieved_state.phase == GamePhase.RUNNING


def test_guess_vowel():
    action = GuessLetterAction(letter='a')
    assert action.is_vowel() is True


def test_guess_consonant():
    action = GuessLetterAction(letter='b')
    assert action.is_vowel() is False


def test_game_phase_description():
    phase = GamePhase.RUNNING
    assert phase.describe() == "Current phase: running"


def test_game_phase_finished():
    phase = GamePhase.FINISHED
    assert phase.is_finished() is True

def test_random_player_selects_action():
    game = Hangman()
    state = HangmanGameState(word_to_guess='hangman', guesses=['H', 'A'], incorrect_guesses=['B', 'C'], phase=GamePhase.RUNNING)
    game.set_state(state)
    player = RandomPlayer()
    actions = game.get_list_action()
    action = player.select_action(state, actions)
    assert action in actions


def test_actions_when_game_finished():
    game = Hangman()
    state = HangmanGameState(word_to_guess='finished', guesses=['F', 'I', 'N', 'I', 'S', 'H', 'E', 'D'], incorrect_guesses=[], phase=GamePhase.FINISHED)
    game.set_state(state)
    actions = game.get_list_action()
    assert len(actions) == 27 - state.guesses.__len__()


def test_reset_guesses():
    state = HangmanGameState(word_to_guess='testing', guesses=['T', 'E', 'S'], incorrect_guesses=['A', 'B'], phase=GamePhase.RUNNING)
    state.reset_guesses()
    assert state.guesses == []
    assert state.incorrect_guesses == []


def test_hangman_initial_state():
    game = Hangman()
    assert game._state is None
    assert game.max_attempts == 8


def test_set_state_updates_phase():
    game = Hangman()
    state = HangmanGameState(word_to_guess='phase', guesses=['P', 'H', 'A'], incorrect_guesses=['X', 'Y'], phase=GamePhase.RUNNING)
    game.set_state(state)
    retrieved_state = game.get_state()
    assert retrieved_state.phase == GamePhase.RUNNING
    game.apply_action(GuessLetterAction(letter='s'))
    game.apply_action(GuessLetterAction(letter='e'))
    assert retrieved_state.phase == GamePhase.FINISHED


def test_max_incorrect_guesses():
    game = Hangman()
    state = HangmanGameState(word_to_guess='python', guesses=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'I'], incorrect_guesses=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'I'], phase=GamePhase.RUNNING)
    game.set_state(state)
    retrieved_state = game.get_state()
    print(state.incorrect_guesses)
    assert retrieved_state.has_max_incorrect_guesses() is True
    assert retrieved_state.phase == GamePhase.FINISHED


def test_apply_already_guessed_letter():
    game = Hangman()
    state = HangmanGameState(word_to_guess='python', guesses=['P'], incorrect_guesses=['A'], phase=GamePhase.RUNNING)
    game.set_state(state)
    game.apply_action(GuessLetterAction(letter='p'))  # Guessing 'P' again
    retrieved_state = game.get_state()
    assert retrieved_state.guesses.count('P') == 1  # Should still be only one 'P'


def test_game_state_description():
    state = HangmanGameState(word_to_guess='python', guesses=['P', 'Y'], incorrect_guesses=['A', 'B'], phase=GamePhase.RUNNING)
    description = state.describe()
    assert description == "Word to guess: PY____, Phase: GamePhase.RUNNING, Guesses: ['P', 'Y'], Incorrect guesses: ['A', 'B']"


def test_empty_word_to_guess():
    game = Hangman()
    state = HangmanGameState(word_to_guess='', guesses=[], incorrect_guesses=[], phase=GamePhase.RUNNING)
    game.set_state(state)
    retrieved_state = game.get_state()
    assert retrieved_state.is_word_guessed() is True
    assert retrieved_state.phase == GamePhase.FINISHED


def test_game_without_setting_state():
    game = Hangman()
    with pytest.raises(ValueError, match="Game state is not set."):
        game.print_state()
    with pytest.raises(ValueError, match="Game state is not set."):
        game.get_list_action()
    with pytest.raises(ValueError, match="Game state is not set."):
        game.apply_action(GuessLetterAction(letter='A'))


def test_game_phase_after_incorrect_action():
    game = Hangman()
    state = HangmanGameState(word_to_guess='python', guesses=[], incorrect_guesses=['A'], phase=GamePhase.RUNNING)
    game.set_state(state)
    game.apply_action(GuessLetterAction(letter='b'))  # Incorrect guess
    retrieved_state = game.get_state()
    assert retrieved_state.phase == GamePhase.RUNNING


def test_game_state_description_no_guesses():
    state = HangmanGameState(word_to_guess='python', guesses=[], incorrect_guesses=[], phase=GamePhase.RUNNING)
    description = state.describe()
    assert description == "Word to guess: ______, Phase: GamePhase.RUNNING, Guesses: [], Incorrect guesses: []"


def test_reset_game_after_multiple_actions():
    game = Hangman()
    state = HangmanGameState(word_to_guess='python', guesses=['P', 'Y'], incorrect_guesses=['A', 'B'], phase=GamePhase.RUNNING)
    game.set_state(state)
    game.reset()
    assert game._state is None

def test_random_player_no_actions():
    game = Hangman()
    state = HangmanGameState(word_to_guess='test', guesses=list(string.ascii_uppercase), incorrect_guesses=[], phase=GamePhase.RUNNING)
    game.set_state(state)
    player = RandomPlayer()
    actions = game.get_list_action()
    action = player.select_action(state, actions)
    assert action is None


def test_game_only_incorrect_guesses():
    game = Hangman()
    state = HangmanGameState(word_to_guess='java', guesses=['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'], incorrect_guesses=['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'], phase=GamePhase.RUNNING)
    game.set_state(state)
    retrieved_state = game.get_state()
    assert retrieved_state.has_max_incorrect_guesses() is True
    assert retrieved_state.phase == GamePhase.FINISHED

if __name__ == "__main__":
    pytest.main()
