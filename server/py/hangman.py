"""
Hangman game implementation.
"""

from typing import List, Optional
import string
import random
from enum import Enum
from server.py.game import Game, Player


class GuessLetterAction:
    # pylint: disable=too-few-public-methods
    """
    Represents a player's action where a letter is guessed.

    Attributes:
        letter (str): The guessed letter.
    """

    def __init__(self, letter: str) -> None:
        self.letter = letter.upper()


class GamePhase(str, Enum):
    # pylint: disable=too-few-public-methods
    """
    Enum class to represent the different phases of the Hangman game.

    Attributes:
        SETUP (str): Game setup phase before the game starts.
        RUNNING (str): Game is currently ongoing.
        FINISHED (str): Game is finished (either won or lost).
    """

    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'


class HangmanGameState:
    """
    Represents the current state of the Hangman game.

    Attributes:
        word_to_guess (str): The word being guessed in the game.
        phase (GamePhase): Current phase of the game.
        guesses (List[str]): A list of correct guesses made so far.
        incorrect_guesses (List[str]): A list of incorrect guesses made so far.
    """

    def __init__(
        self,
        word_to_guess: str,
        phase: GamePhase,
        guesses: List[str],
        incorrect_guesses: List[str]
    ) -> None:
        self.word_to_guess = word_to_guess.upper()  # Normalize to uppercase
        self.phase = phase
        self.guesses = guesses
        self.incorrect_guesses = incorrect_guesses


class Hangman(Game):
    """
    Manages the Hangman game logic and state.

    Attributes:
        state (Optional[HangmanGameState]): The current state of the game.
        max_attempts (int): The maximum number of incorrect guesses allowed.
    """

    def __init__(self) -> None:
        self.state: Optional[HangmanGameState] = None
        self.max_attempts = 8
        self.allow_empty_word_to_guess = False  # Allow empty word for testing purposes

    def get_state(self) -> Optional[HangmanGameState]:
        """
        Returns the current game state.

        Returns:
            Optional[HangmanGameState]: The current state of the game, or None if not initialized.
        """
        return self.state

    def set_state(self, state: HangmanGameState) -> None:
        """
        Sets the game's state. Initializes game progress and updates phases.

        Args:
            state (HangmanGameState): The initial state of the game.

        Raises:
            ValueError: If the word_to_guess is empty.
        """
        if not state.word_to_guess and not self.allow_empty_word_to_guess:
            print("The word to guess cannot be empty.")

        # Normalize and clean the guesses and incorrect guesses
        correct_guesses = [
            guess.upper() for guess in state.guesses
            if guess.upper() in state.word_to_guess
        ]
        incorrect_guesses = [
            guess.upper() for guess in state.guesses
            if guess.upper() not in state.word_to_guess
        ]

        state.guesses = correct_guesses
        state.incorrect_guesses.extend(incorrect_guesses)

        # Update game phase
        if all(letter in state.guesses for letter in state.word_to_guess):
            state.phase = GamePhase.FINISHED
        elif len(state.incorrect_guesses) >= self.max_attempts:
            state.phase = GamePhase.FINISHED
        else:
            state.phase = GamePhase.RUNNING

        self.state = state

    def print_state(self) -> None:
        """
        Prints the current game state, including guesses, masked word,
        remaining attempts, and the Hangman drawing.

        Raises:
            ValueError: If the game state is not initialized.
        """
        if not self.state:
            raise ValueError("Game state is not initialized.")

        # Check if the game has ended
        if self.state.phase == GamePhase.FINISHED:
            if set(self.state.word_to_guess) <= set(self.state.guesses):
                print("🎉 Congratulations! You've guessed the word:", self.state.word_to_guess)
            else:
                print("💀 Game Over! You've run out of attempts. The word was:", self.state.word_to_guess)
            return

        remaining_attempts = self.max_attempts - len(self.state.incorrect_guesses)
        masked_word = ''.join(
            letter if letter.upper() in self.state.guesses else '_'
            for letter in self.state.word_to_guess
        )
        print("\n === Hangman Game ===")
        print(f"Word to Guess: {masked_word}")
        print(f"Incorrect Guesses: {self.state.incorrect_guesses}")
        print(f"Remaining Attempts: {remaining_attempts}")
        print("=========================")
        self.print_hangman(len(self.state.incorrect_guesses))

    def print_hangman(self, incorrect_guess_count: int) -> None:
        """
        Prints the Hangman drawing corresponding to the number of incorrect guesses.

        Args:
            incorrect_guess_count (int): The number of incorrect guesses made so far.
        """
        hangman_stages = [
            """
               ------
               |    |
                    |
                    |
                    |
                    |
                    |
                    |
              ========
            """,
            """
               ------
               |    |
               |    |
                    |
                    |
                    |
                    |
                    |
              ========
            """,
            """
               ------
               |    |
               |    |
               O    |
                    |
                    |
                    |
              ========
            """,
            """
               ------
               |    |
               |    |
               O    |
               |    |
                    |
                    |
              ========
            """,
            """
               ------
               |    |
               |    |
               O    |
              /|    |
                    |
                    |
              ========
            """,
            """
               ------
               |    |
               |    |
               O    |
              /|\\   |
                    |
                    |
              ========
            """,
            """
               ------
               |    |
               |    |
               O    |
              /|\\   |
              /     |
                    |
              ========
            """,
            """
               ------
               |    |
               |    |
               O    |
              /|\\   |
              / \\   |
                    |
              ========
            """,
            """
               ------
               |    |
               |    |
               O    |
              /|\\   |
              / \\   |
              [GAME OVER]
              ========
            """
        ]
        # Cap the stage index to the maximum available in hangman_stages
        stage_index = min(incorrect_guess_count, len(hangman_stages) - 1)
        print(hangman_stages[stage_index])

    def get_list_action(self) -> List[GuessLetterAction]:
        """
        Returns a list of possible actions (letters that have not been guessed yet).

        Returns:
            List[GuessLetterAction]: A list of possible letter actions.

        Raises:
            ValueError: If the game state is not initialized.
        """
        if not self.state:
            raise ValueError("Game state is not initialized.")

        alphabet = set(string.ascii_uppercase)
        guessed_letters = {
            letter.upper()
            for letter in self.state.guesses + self.state.incorrect_guesses
        }
        available_letters = alphabet - guessed_letters
        return [GuessLetterAction(letter) for letter in sorted(available_letters)]

    def apply_action(self, action: GuessLetterAction) -> None:
        """
        Applies a player's action to the game state.

        Args:
            action (GuessLetterAction): The action to apply.

        Raises:
            ValueError: If the game state is not initialized or not running,
                        or if the letter has already been guessed.
        """
        if not self.state:
            raise ValueError("Game state is not initialized.")
        if self.state.phase != GamePhase.RUNNING:
            raise ValueError("Actions cannot be applied when the game is not in the RUNNING phase.")

        guessed_letter = action.letter

        if guessed_letter in self.state.guesses + self.state.incorrect_guesses:
            raise ValueError(f"The letter '{guessed_letter}' has already been guessed.")

        if guessed_letter in self.state.word_to_guess:
            print(f"Correct! The letter '{guessed_letter}' is in the word.")
            self.state.guesses.append(guessed_letter)
        else:
            print(f"Incorrect! The letter '{guessed_letter}' is not in the word.")
            self.state.incorrect_guesses.append(guessed_letter)

        if all(letter in self.state.guesses for letter in self.state.word_to_guess):
            self.state.phase = GamePhase.FINISHED
        elif len(self.state.incorrect_guesses) >= self.max_attempts:
            self.state.phase = GamePhase.FINISHED

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """
        Returns the game state from a player's perspective.

        Args:
            idx_player (int): The index of the player (not used in single-player Hangman).

        Returns:
            HangmanGameState: The player's view of the game state.

        Raises:
            ValueError: If the game state is not set.
        """
        if not self.state:
            raise ValueError("Game state is not set.")

        masked_word = ' '.join(
            letter if letter in self.state.guesses else '_'
            for letter in self.state.word_to_guess
        )
        return HangmanGameState(
            word_to_guess=masked_word,
            phase=self.state.phase,
            guesses=self.state.guesses,
            incorrect_guesses=self.state.incorrect_guesses
        )


class RandomPlayer(Player):
    # pylint: disable=too-few-public-methods
    """
    A player that selects a random valid action.

    Methods:
        select_action: Selects a random action from the available actions.
    """

    def select_action(
        self,
        state: HangmanGameState,
        actions_list: List[GuessLetterAction]
    ) -> Optional[GuessLetterAction]:
        """
        Selects a random action from the list of available actions.

        Args:
            state (HangmanGameState): The current game state.
            actions_list (List[GuessLetterAction]): The list of possible actions.

        Returns:
            Optional[GuessLetterAction]: The selected action, or None if no actions are available.
        """
        if not actions_list:
            print("No available actions to select from.")
            return None
        selected_action = random.choice(actions_list)
        print(f"RandomPlayer selected action: {selected_action.letter}")
        return selected_action


if __name__ == "__main__":
    game = Hangman()
    game_state = HangmanGameState(
        word_to_guess="DeHop",
        phase=GamePhase.RUNNING,
        guesses=[],
        incorrect_guesses=[]
    )
    game.set_state(game_state)
    game.print_state()

    # Ensure the game state is not None
    state = game.get_state()
    if state is None:
        raise ValueError("Game state is not initialized.")

    while state.phase != GamePhase.FINISHED:
        action_list = game.get_list_action()
        print("\nAvailable actions:", [action.letter for action in action_list])
        guess = input("Enter your guess: ")
        selected_act = next(
            (action for action in action_list if action.letter == guess.upper()), None
        )
        if selected_act:
            game.apply_action(selected_act)
            game.print_state()
        else:
            print(f"Invalid guess '{guess}'. Try again.")
        # Update the state after each action
        state = game.get_state()
        if state is None:
            raise ValueError("Game state became None during the game.")
