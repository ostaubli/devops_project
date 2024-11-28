import string
import random
from typing import List, Optional
from enum import Enum
from server.py.game import Game, Player


class GuessLetterAction:
    def __init__(self, letter: str) -> None:
        self.letter = letter.upper()

    def describe(self) -> str:
        return f"Guessing letter: {self.letter}"

    def is_vowel(self) -> bool:
        return self.letter in 'AEIOU'


class GamePhase(str, Enum):
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'

    def describe(self) -> str:
        return f"Current phase: {self.value}"

    def is_finished(self) -> bool:
        return self == GamePhase.FINISHED


class HangmanGameState:
    def __init__(
        self,
        word_to_guess: str,
        phase: GamePhase,
        guesses: Optional[List[str]] = None,
        incorrect_guesses: Optional[List[str]] = None
    ) -> None:
        self.word_to_guess = word_to_guess.upper()
        self.phase = phase
        self.guesses = [guess.upper() for guess in (guesses or [])]
        self.incorrect_guesses = [guess.upper() for guess in (incorrect_guesses or [])]

    def is_word_guessed(self) -> bool:
        return all(letter in self.guesses for letter in self.word_to_guess)

    def has_max_incorrect_guesses(self) -> bool:
        return len(self.incorrect_guesses) >= 8

    def update_phase(self) -> None:
        if self.has_max_incorrect_guesses() or self.is_word_guessed():
            self.phase = GamePhase.FINISHED

    def describe(self) -> str:
        masked_word = ''.join([letter if letter in self.guesses else '_' for letter in self.word_to_guess])
        return (
            f"Word to guess: {masked_word}, Phase: {self.phase}, "
            f"Guesses: {self.guesses}, Incorrect guesses: {self.incorrect_guesses}"
        )

    def reset_guesses(self) -> None:
        self.guesses.clear()
        self.incorrect_guesses.clear()


class Hangman(Game):
    def __init__(self) -> None:
        """ Important: Game initialization also requires a set_state call to set the 'word_to_guess' """
        super().__init__()
        self._state: Optional[HangmanGameState] = None
        self.max_attempts = 8

    def reset(self) -> None:
        self._state = None

    def set_state(self, state: HangmanGameState) -> None:
        # Normalize and clean the guesses and incorrect guesses
        all_guesses = [guess.upper() for guess in state.guesses]
        correct_guesses = [
            guess for guess in all_guesses
            if guess in state.word_to_guess
        ]
        incorrect_guesses = [
            guess for guess in all_guesses
            if guess not in state.word_to_guess
        ]

        state.guesses = correct_guesses + incorrect_guesses
        state.incorrect_guesses = incorrect_guesses

        # Update game phase
        state.update_phase()

        self._state = state

    def get_state(self) -> HangmanGameState:
        if self._state is None:
            raise ValueError("Game state is not set.")
        return self._state

    def print_state(self) -> None:
        if self._state is None:
            raise ValueError("Game state is not set.")
        print(self._state.describe())

    def get_list_action(self) -> List[GuessLetterAction]:
        if self._state is None:
            raise ValueError("Game state is not set.")
        guessed_letters = set(self._state.guesses + self._state.incorrect_guesses)
        unused_letters = set(string.ascii_uppercase) - guessed_letters
        return [GuessLetterAction(letter) for letter in unused_letters]

    def apply_action(self, action: GuessLetterAction) -> None:
        if self._state is None:
            raise ValueError("Game state is not set.")
        if self._state.phase != GamePhase.RUNNING:
            return

        guessed_letter = action.letter.upper()

        if guessed_letter in self._state.guesses or guessed_letter in self._state.incorrect_guesses:
            return  # Skip if letter has already been guessed

        self._state.guesses.append(guessed_letter)

        if guessed_letter not in self._state.word_to_guess:
            self._state.incorrect_guesses.append(guessed_letter)

        # Update the game phase if needed
        self._state.update_phase()

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """ Get the masked state for the active player (e.g. the opponent's cards are face down) """
        if self._state is None:
            raise ValueError("Game state is not set.")
        # In this simple game, player view is the same as the full state
        return self._state


class RandomPlayer(Player):
    def __init__(self) -> None:
        super().__init__()
        self.name = "RandomPlayer"

    def select_action(self, state: HangmanGameState, actions: List[GuessLetterAction]) -> Optional[GuessLetterAction]:
        """ Given masked game state and possible actions, select the next action """
        if actions:
            return random.choice(actions)
        return None

    def describe(self) -> str:
        return f"Player name: {self.name}"


if __name__ == "__main__":
    game = Hangman()
    game_state = HangmanGameState(word_to_guess='DevOps', phase=GamePhase.RUNNING)
    game.set_state(game_state)
    game.print_state()

    # Apply action for lowercase letter test
    game.apply_action(GuessLetterAction(letter='x'))
    game.print_state()

    # Use RandomPlayer to play the game
    player = RandomPlayer()
    while not game.get_state().phase.is_finished():
        possible_actions = game.get_list_action()
        selected_action = player.select_action(game.get_state(), possible_actions)
        if selected_action:
            game.apply_action(selected_action)
            game.print_state()
