"""Hangman game implementation module.

Implements the classic Hangman word guessing game with features including:
- Game state management
- Letter guessing mechanics
- Win/loss condition tracking
- ASCII art visualization
"""

from typing import List, Optional
import random
from enum import Enum
from dataclasses import dataclass

# Hangman ASCII art representations for different game stages
HANGMAN_ART = [
        """
       ------
            |
            |
            |
            |
            |
    =========
    """,
    """
       ------
       |    |
            |
            |
            |
            |
    =========
    """,
    """
       ------
       |    |
       O    |
            |
            |
            |
    =========
    """,
    """
       ------
       |    |
       O    |
       |    |
            |
            |
    =========
    """,
    """
       ------
       |    |
       O    |
      /|    |
            |
            |
    =========
    """,
    """
       ------
       |    |
       O    |
      /|\\   |
            |
            |
    =========
    """,
    """
       ------
       |    |
       O    |
      /|\\   |
      /     |
            |
    =========
    """,
    """
       ------
       |    |
       O    |
      /|\\   |
      / \\   |
            |
    =========
    """
]


@dataclass
class GuessLetterAction:
    """Represents a single guess action by a player."""
    letter: str


class GamePhase(str, Enum):
    """Type of possible game phases."""
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'


@dataclass
class HangmanGameState:
    """Represents the state of the Hangman game at any given time."""

    word_to_guess: str
    phase: GamePhase
    guesses: List[str]
    incorrect_guesses: List[str]

    def __post_init__(self) -> None:
        """Post-initialization processing."""
        self.word_to_guess = self.word_to_guess.upper()


class Hangman:
    """The main Hangman game logic."""

    MAX_INCORRECT_GUESSES: int = 8

    def __init__(self) -> None:
        """Initialize a new Hangman game instance."""
        self.state: Optional[HangmanGameState] = None
        self.display_word: List[str] = []

    def get_state(self) -> Optional[HangmanGameState]:
        """Retrieve the current game state."""
        return self.state

    def set_state(self, state: HangmanGameState) -> None:
        """Set up the initial state of the game and prepare the display word."""
        self.state = state

        if state and state.word_to_guess:
            self.display_word = [
                char if char.upper() in [guess.upper() for guess in state.guesses]
                else "_" for char in state.word_to_guess
            ]

            state.guesses = list(set(state.guesses))
            incorrect_guesses_set = set(state.incorrect_guesses)
            incorrect_guesses_set.update(
                [guess for guess in state.guesses
                 if guess.upper() not in state.word_to_guess.upper()]
            )
            state.incorrect_guesses = list(incorrect_guesses_set)

        if "_" not in self.display_word:
            self.state.phase = GamePhase.FINISHED
            return

        if len(self.state.incorrect_guesses) >= self.MAX_INCORRECT_GUESSES:
            self.state.phase = GamePhase.FINISHED

    def print_state(self) -> None:
        """Print current game state to console."""
        if not self.state:
            print("No game state available.")
            return
        revealed_word = " ".join(self.display_word)
        print(f"Word: {revealed_word}")
        print(f"Guesses: {', '.join(self.state.guesses)}")
        print(f"Incorrect guesses: {', '.join(self.state.incorrect_guesses)}")
        print(f"Game Phase: {self.state.phase}")

    def get_list_action(self) -> List[GuessLetterAction]:
        """Get a list of possible actions for the active player."""
        if self.state is None or self.state.phase != GamePhase.RUNNING:
            return []

        guessed_letters = set(self.state.guesses + self.state.incorrect_guesses)
        return [
            GuessLetterAction(letter)
            for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            if letter not in guessed_letters
        ]

    def apply_action(self, action: GuessLetterAction) -> None:
        """Process a player's guess and update the game state."""
        if not self.state or self.state.phase != GamePhase.RUNNING:
            return

        guess = action.letter.upper()

        if guess in self.state.guesses or guess in self.state.incorrect_guesses:
            return

        self.state.guesses.append(guess)

        if guess in self.state.word_to_guess.upper():
            for idx, char in enumerate(self.state.word_to_guess):
                if char.upper() == guess:
                    self.display_word[idx] = char
        else:
            self.state.incorrect_guesses.append(guess)

        if "_" not in self.display_word:
            self.state.phase = GamePhase.FINISHED
            return

        if len(self.state.incorrect_guesses) >= self.MAX_INCORRECT_GUESSES:
            self.state.phase = GamePhase.FINISHED

    def get_player_view(self) -> HangmanGameState:
        """Get the game state from a player's perspective."""
        if not self.state:
            raise ValueError("Game state is not initialized")
        masked_word = "".join(
            char if char in self.state.guesses else "_"
            for char in self.state.word_to_guess
        )
        return HangmanGameState(
            word_to_guess=masked_word,
            phase=self.state.phase,
            guesses=self.state.guesses,
            incorrect_guesses=self.state.incorrect_guesses,
        )


class RandomPlayer:
    """Implementation of a player that makes random guesses."""

    def __init__(self) -> None:
        """Initialize random player."""
        self.past_guesses: set[str] = set()

    def select_action(
        self, actions: List[GuessLetterAction]
    ) -> Optional[GuessLetterAction]:
        """Select a random valid action."""
        valid_actions = [
            action for action in actions if action.letter.upper() not in self.past_guesses
        ]
        if valid_actions:
            chosen_action = random.choice(valid_actions)
            self.past_guesses.add(chosen_action.letter.upper())
            return chosen_action
        return None

    def reset_guesses(self) -> None:
        """Reset the player's past guesses."""
        self.past_guesses.clear()

    def get_past_guesses(self) -> set:
        """Return the set of past guesses."""
        return self.past_guesses


if __name__ == "__main__":
    game = Hangman()
