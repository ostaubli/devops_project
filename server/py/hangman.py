import string
import random
from enum import Enum
from typing import List, Optional


class GamePhase(str, Enum):
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'

    def describe(self) -> str:
        return f"Current phase: {self.value}"

    def is_finished(self) -> bool:
        return self == GamePhase.FINISHED


class GuessLetterAction:
    def __init__(self, letter: str) -> None:
        self.letter = letter.upper()

    def describe(self) -> str:
        return f"Guessing letter: {self.letter}"

    def is_vowel(self) -> bool:
        return self.letter in 'AEIOU'


class HangmanGameState:
    def __init__(
        self,
        word_to_guess: str,
        guesses: List[str],
        incorrect_guesses: List[str],
        phase: GamePhase,
    ) -> None:
        self.word_to_guess = word_to_guess.upper()
        self.guesses = [guess.upper() for guess in guesses]
        self.incorrect_guesses = [guess.upper() for guess in incorrect_guesses]
        self.phase = phase

    def is_word_guessed(self) -> bool:
        return all(letter in self.guesses for letter in self.word_to_guess)

    def has_max_incorrect_guesses(self) -> bool:
        return len(self.incorrect_guesses) >= 8

    def update_phase(self) -> None:
        if self.has_max_incorrect_guesses():
            self.phase = GamePhase.FINISHED
        elif self.is_word_guessed():
            self.phase = GamePhase.FINISHED

    def describe(self) -> str:
        return (
            f"Word to guess: {self.word_to_guess}, Phase: {self.phase}, "
            f"Guesses: {self.guesses}, Incorrect guesses: {self.incorrect_guesses}"
        )

    def reset_guesses(self) -> None:
        self.guesses.clear()
        self.incorrect_guesses.clear()


class Hangman:
    def __init__(self) -> None:
        self.state: Optional[HangmanGameState] = None
        self.max_attempts = 8

    def reset(self) -> None:
        self.state = None

    def set_state(self, game_state: HangmanGameState) -> None:
        # Normalize and clean the guesses and incorrect guesses
        correct_guesses = [
            guess.upper() for guess in game_state.guesses
            if guess.upper() in game_state.word_to_guess
        ]
        incorrect_guesses = [
            guess.upper() for guess in game_state.guesses
            if guess.upper() not in game_state.word_to_guess
        ]

        game_state.guesses = correct_guesses
        game_state.incorrect_guesses.extend(incorrect_guesses)

        # Update game phase
        if all(letter in game_state.guesses for letter in game_state.word_to_guess):
            game_state.phase = GamePhase.FINISHED
        elif len(game_state.incorrect_guesses) >= self.max_attempts:
            game_state.phase = GamePhase.FINISHED
        else:
            game_state.phase = GamePhase.RUNNING

        self.state = game_state

    def get_state(self) -> HangmanGameState:
        if self.state is None:
            raise ValueError("Game state is not set.")
        return self.state

    def get_list_action(self) -> List[GuessLetterAction]:
        if self.state is None:
            return []
        guessed_letters = set(self.state.guesses + self.state.incorrect_guesses)
        unused_letters = set(string.ascii_uppercase) - guessed_letters
        return [GuessLetterAction(letter) for letter in unused_letters]

    def apply_action(self, guess_action: GuessLetterAction) -> None:
        if self.state is None:
            return
        if self.state.phase != GamePhase.RUNNING:
            return

        guessed_letter = guess_action.letter

        if guessed_letter in self.state.guesses + self.state.incorrect_guesses:
            return  # Skip if letter has already been guessed

        if guessed_letter in self.state.word_to_guess:
            self.state.guesses.append(guessed_letter)
        else:
            self.state.incorrect_guesses.append(guessed_letter)

        # Update game phase
        if all(letter in self.state.guesses for letter in self.state.word_to_guess):
            self.state.phase = GamePhase.FINISHED
        elif len(self.state.incorrect_guesses) >= self.max_attempts:
            self.state.phase = GamePhase.FINISHED

        letter = guess_action.letter
        if letter not in self.state.guesses:
            self.state.guesses.append(letter)
            if letter not in self.state.word_to_guess:
                self.state.incorrect_guesses.append(letter)
                if len(self.state.incorrect_guesses) >= 8:
                    self.state.phase = GamePhase.FINISHED

        # Update the game phase if needed
        self.state.update_phase()

        letter = guess_action.letter
        if letter not in self.state.guesses:
            self.state.guesses.append(letter)
            if letter not in self.state.word_to_guess:
                self.state.incorrect_guesses.append(letter)

        # Update the game phase if needed
        self.state.update_phase()


class RandomPlayer:
    def __init__(self) -> None:
        self.name = "RandomPlayer"

    def select_action(self, possible_actions: List[GuessLetterAction]) -> Optional[GuessLetterAction]:
        if len(possible_actions) > 0:
            return random.choice(possible_actions)
        return None

    def describe(self) -> str:
        return f"Player name: {self.name}"


if __name__ == "__main__":
    game_server = Hangman()
    # Example usage of the game
    state = HangmanGameState(word_to_guess='devops', guesses=[], incorrect_guesses=[], phase=GamePhase.RUNNING)
    game_server.set_state(state)
    print(game_server.get_state().word_to_guess)
    actions = game_server.get_list_action()
    for action in actions:
        print(action.letter)
    game_server.apply_action(GuessLetterAction(letter='d'))
    print(game_server.get_state().guesses)
