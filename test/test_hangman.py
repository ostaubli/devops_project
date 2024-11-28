import pytest
from server.py.hangman import Hangman, HangmanGameState, GamePhase, GuessLetterAction, RandomPlayer


def test_set_state_and_get_state():
    game = Hangman()
    state = HangmanGameState(word_to_guess='devops', guesses=[], incorrect_guesses=[], phase=GamePhase.RUNNING)
    game.set_state(state)
    retrieved_state = game.get_state()
    assert retrieved_state.word_to_guess == 'DEVOPS'
    assert retrieved_state.phase == GamePhase.RUNNING
    assert retrieved_state.guesses == []
    assert retrieved_state.incorrect_guesses == []


def test_get_list_action():
    game = Hangman()
    state = HangmanGameState(word_to_guess='devops', guesses=['A', 'B'], incorrect_guesses=['A', 'B'], phase=GamePhase.RUNNING)
    game.set_state(state)
    actions = game.get_list_action()
    action_letters = [action.letter for action in actions]
    assert 'A' not in action_letters
    assert 'B' not in action_letters
    assert 'C' in action_letters
    assert len(action_letters) == 24


def test_apply_action_correct_guess():
    game = Hangman()
    state = HangmanGameState(word_to_guess='devops', guesses=[], incorrect_guesses=[], phase=GamePhase.RUNNING)
    game.set_state(state)
    game.apply_action(GuessLetterAction(letter='d'))
    retrieved_state = game.get_state()
    assert 'D' in retrieved_state.guesses
    assert 'D' not in retrieved_state.incorrect_guesses
    assert retrieved_state.phase == GamePhase.RUNNING


def test_apply_action_incorrect_guess():
    game = Hangman()
    state = HangmanGameState(word_to_guess='devops', guesses=['A', 'B', 'C', 'D', 'E', 'F', 'G'], incorrect_guesses=['A', 'B', 'C', 'D', 'E', 'F', 'G'], phase=GamePhase.RUNNING)
    game.set_state(state)
    game.apply_action(GuessLetterAction(letter='x'))
    retrieved_state = game.get_state()
    assert 'X' in retrieved_state.incorrect_guesses
    assert retrieved_state.phase == GamePhase.FINISHED
    assert len(retrieved_state.incorrect_guesses) == 8


def test_game_phase_finished_after_max_incorrect_guesses():
    game = Hangman()
    state = HangmanGameState(word_to_guess='xy', guesses=['A', 'B', 'C', 'D', 'E', 'F', 'G'], incorrect_guesses=['A', 'B', 'C', 'D', 'E', 'F', 'G'], phase=GamePhase.RUNNING)
    game.set_state(state)
    game.apply_action(GuessLetterAction(letter='H'))
    retrieved_state = game.get_state()
    assert retrieved_state.phase == GamePhase.FINISHED
    assert len(retrieved_state.incorrect_guesses) == 8


def test_game_phase_finished_after_word_guessed():
    game = Hangman()
    state = HangmanGameState(word_to_guess='xy', guesses=['X'], incorrect_guesses=[], phase=GamePhase.RUNNING)
    game.set_state(state)
    game.apply_action(GuessLetterAction(letter='y'))
    retrieved_state = game.get_state()
    assert retrieved_state.phase == GamePhase.FINISHED


def test_reset_game():
    game = Hangman()
    state = HangmanGameState(word_to_guess='devops', guesses=['D'], incorrect_guesses=['X'], phase=GamePhase.RUNNING)
    game.set_state(state)
    game.reset()
    assert game.state is None


def test_random_player_select_action():
    player = RandomPlayer()
    actions = [GuessLetterAction(letter='A'), GuessLetterAction(letter='B')]
    selected_action = player.select_action(actions)
    assert selected_action in actions


def test_random_player_select_action_no_actions():
    player = RandomPlayer()
    actions = []
    selected_action = player.select_action(actions)
    assert selected_action is None


def test_apply_action_on_running_game_after_finish():
    game = Hangman()
    state = HangmanGameState(word_to_guess='xy', guesses=['X', 'Y'], incorrect_guesses=[], phase=GamePhase.RUNNING)
    game.set_state(state)
    game.apply_action(GuessLetterAction(letter='Z'))
    retrieved_state = game.get_state()
    assert 'Z' in retrieved_state.guesses
    assert retrieved_state.phase == GamePhase.FINISHED


def test_apply_same_letter_twice():
    game = Hangman()
    state = HangmanGameState(word_to_guess='devops', guesses=['D'], incorrect_guesses=[], phase=GamePhase.RUNNING)
    game.set_state(state)
    game.apply_action(GuessLetterAction(letter='D'))
    retrieved_state = game.get_state()
    assert retrieved_state.guesses.count('D') == 1


def test_has_max_incorrect_guesses():
    state = HangmanGameState(word_to_guess='devops', guesses=[], incorrect_guesses=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'], phase=GamePhase.RUNNING)
    assert state.has_max_incorrect_guesses() is True


def test_is_word_guessed():
    state = HangmanGameState(word_to_guess='xy', guesses=['X', 'Y'], incorrect_guesses=[], phase=GamePhase.RUNNING)
    assert state.is_word_guessed() is True


def test_update_phase():
    state = HangmanGameState(word_to_guess='xy', guesses=['X', 'Y'], incorrect_guesses=[], phase=GamePhase.RUNNING)
    state.update_phase()
    assert state.phase == GamePhase.FINISHED


if __name__ == "__main__":
    pytest.main()
