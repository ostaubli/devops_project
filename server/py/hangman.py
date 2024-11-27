from typing import List, Optional
import random
from enum import Enum

# Hangman Art (constant global variable)
hangman_art = [
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

class GuessLetterAction:
    """
    Represents a single guess action by a player.
    Attributes:
        letter (str): The letter guessed by the player.
    """
    def __init__(self, letter: str) -> None:
        self.letter = letter


class GamePhase(str, Enum):
    """
    Enum to represent the current phase of the game.
    Phases:
        SETUP: Before the game starts.
        RUNNING: While the game is ongoing.
        FINISHED: After the game ends.
    """
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'


class HangmanGameState:
    """
    Represents the state of the Hangman game at any given time.
    Attributes:
        word_to_guess (str): The word the player is trying to guess.
        phase (GamePhase): The current phase of the game (SETUP, RUNNING, or FINISHED).
        guesses (List[str]): A list of all guessed letters (both correct and incorrect).
        incorrect_guesses (List[str]): A list of all incorrect guesses.
    """
    def __init__(self, word_to_guess: str, phase: GamePhase, guesses: List[str], incorrect_guesses: List[str]) -> None:
        self.word_to_guess = word_to_guess.upper()  # Always store the word in uppercase for consistency
        self.phase = phase
        self.guesses = guesses
        self.incorrect_guesses = incorrect_guesses


class Hangman:
    """
    The main Hangman game logic.
    This class handles setting up the game, processing guesses, and managing the game state.
    """
    def __init__(self) -> None:
        """
        Initializes the Hangman game.
        Note: The game requires a call to `set_state` to start.
        """
        self.state = None  # Stores the game state.
        self.display_word = []  # Represents the word as it appears to the player (with "_" for unguessed letters).

    def get_state(self) -> HangmanGameState:
        """
        Retrieve the current game state.
        Returns:
            HangmanGameState: The current game state.
        """
        return self.state

    def set_state(self, state: HangmanGameState) -> None:
        """
        Set up the initial state of the game and prepare the display word.
        Parameters:
            state (HangmanGameState): The initial state of the game.
        """
        self.state = state
        """ used for debugging
        print(f"Set state called:")
        print(f"Word to guess: {state.word_to_guess}")
        print(f"Initial guesses: {state.guesses}")
        print(f"Initial incorrect guesses: {state.incorrect_guesses}")
        print(f"Phase: {state.phase}")"""

        # Initialize the display word with "_" for unguessed letters
        if state and state.word_to_guess:
            self.display_word = [
                char if char.upper() in [guess.upper() for guess in state.guesses] else "_"
                for char in state.word_to_guess
            ]

            # Remove duplicate guesses and synchronize incorrect guesses
            state.guesses = list(dict.fromkeys(state.guesses))
            incorrect_guesses_set = set(state.incorrect_guesses)
            incorrect_guesses_set.update(
                [g for g in state.guesses if g.upper() not in state.word_to_guess.upper()]
            )
            state.incorrect_guesses = list(incorrect_guesses_set)

        # Evaluate win/lose conditions
        if "_" not in self.display_word:
            print("Win condition triggered during set_state: Word guessed!")
            self.state.phase = GamePhase.FINISHED
            return

        if len(self.state.incorrect_guesses) >= 8:
            print("Lose condition triggered during set_state: Too many incorrect guesses!")
            self.state.phase = GamePhase.FINISHED

    def print_state(self) -> None:
        """
        Print the current state of the game for debugging or user information.
        """
        if not self.state:
            print("No game state available.")
            return
        revealed_word = " ".join(self.display_word)
        print(f"Word: {revealed_word}")
        print(f"Guesses: {', '.join(self.state.guesses)}")
        print(f"Incorrect guesses: {', '.join(self.state.incorrect_guesses)}")
        print(f"Game Phase: {self.state.phase}")

    def get_list_action(self) -> List[GuessLetterAction]:
        """
        Get a list of possible actions (valid guesses) for the player.
        Returns:
            List[GuessLetterAction]: A list of all valid letters that have not been guessed.
        """
        if self.state is None or self.state.phase != GamePhase.RUNNING:
            return []

        guessed_letters = set(self.state.guesses + self.state.incorrect_guesses)
        return [
            GuessLetterAction(letter)
            for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            if letter not in guessed_letters
        ]

    def apply_action(self, action: GuessLetterAction) -> None:
        """
        Process a player's guess and update the game state.
        Parameters:
            action (GuessLetterAction): The player's guess.
        """
        if not self.state or self.state.phase != GamePhase.RUNNING:
            return

        guess = action.letter.upper()  # Convert guess to uppercase for consistency

        # Ignore duplicate guesses
        if guess in self.state.guesses or guess in self.state.incorrect_guesses:
            return

        # Add the guessed letter
        self.state.guesses.append(guess)
        self.state.guesses = list(dict.fromkeys(self.state.guesses))  # Remove duplicates

        # Check if the guess is correct
        if guess in self.state.word_to_guess.upper():
            # Update the display word for correct guesses
            for i, char in enumerate(self.state.word_to_guess):
                if char.upper() == guess:
                    self.display_word[i] = char
        else:
            # Add incorrect guesses
            self.state.incorrect_guesses.append(guess)

        # Check win condition
        if "_" not in self.display_word:
            self.state.phase = GamePhase.FINISHED
            return

        # Check lose condition
        if len(self.state.incorrect_guesses) >= 8:
            self.state.phase = GamePhase.FINISHED

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """
        Get the masked state for the player (replaces unguessed letters with "_").
        Parameters:
            idx_player (int): Player index (not used here but kept for extensibility).
        Returns:
            HangmanGameState: The player's view of the game state.
        """
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
    """
    A simple player that makes random guesses.
    """
    def select_action(self, state: HangmanGameState, actions: List[GuessLetterAction]) -> Optional[GuessLetterAction]:
        """Select a random action from the available actions."""
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == "__main__":
    # List of words for random word generation
    word_list = ["PYTHON", "DEVELOPER", "HANGMAN", "ARTIFICIAL", "INTELLIGENCE", "DEVOPS", "COMPUTER", "SCIENCE"]

    # Select a random word
    random_word = random.choice(word_list)

    # Initialize Hangman game and state
    game = Hangman()
    game_state = HangmanGameState(word_to_guess=random_word, phase=GamePhase.RUNNING, guesses=[], incorrect_guesses=[])
    game.set_state(game_state)

    # Main game loop
    while game.state.phase == GamePhase.RUNNING:
        print("\nWord:", " ".join(game.display_word))
        print(f"Incorrect guesses left: {8 - len(game.state.incorrect_guesses)}")

        # Ensure Hangman art doesn't exceed its bounds
        art_index = min(len(game.state.incorrect_guesses), len(hangman_art) - 1)
        print(hangman_art[art_index])

        # Deduplicate guessed letters for display
        unique_guessed_letters = sorted(set(game.state.guesses + game.state.incorrect_guesses))
        print(f"Guessed letters: {', '.join(unique_guessed_letters)}")

        valid_actions = game.get_list_action()
        if not valid_actions:
            break

        guess = input("Guess a letter: ").upper()
        action = next((a for a in valid_actions if a.letter == guess), None)

        if not action:
            print(f"Invalid guess '{guess}'. Please try again.")
            continue

        game.apply_action(action)

    # Game over
    if "_" not in game.display_word:
        print(f"\nCongratulations! You have guessed the word: {game.state.word_to_guess}")
    else:
        print("\n" + hangman_art[-1])  # Final hangman art
        print(f"\nGame Over! The word was: {game.state.word_to_guess}")


