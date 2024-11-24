from typing import List, Optional
import random
from enum import Enum
from server.py.game import Game, Player


class GuessLetterAction:
    """
    Represents a player's action where a letter is guessed.

    Attributes:
        letter (str): The guessed letter.
    """
    def __init__(self, letter: str) -> None:
        """
        Initializes the GuessLetterAction object.

        Args:
            letter (str): The guessed letter.
        """
        self.letter = letter


class GamePhase(str, Enum):
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
        """
        Initializes the HangmanGameState object.

        Args:
            word_to_guess (str): The word to be guessed by the player.
            phase (GamePhase): The current phase of the game.
            guesses (List[str]): Correct guesses made so far.
            incorrect_guesses (List[str]): Incorrect guesses made so far.
        """
        self.word_to_guess = word_to_guess
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
        """
        Initializes the Hangman game.
        """
        self.state: Optional[HangmanGameState] = None
        self.max_attempts = 8  # Default maximum incorrect guesses

    def get_state(self) -> HangmanGameState:
        """
        Returns the full unmasked Hangman game state.

        Returns:
            HangmanGameState: The current state of the game.
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
        if not state.word_to_guess:
            raise ValueError("The word to guess cannot be empty.")

        if self.state is None:  # First-time initialization
            state.phase = GamePhase.RUNNING
            state.guesses = []
            state.incorrect_guesses = []

        # Check game progress and update the game phase
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
        """
        if not self.state:
            print("Game state is not initialized.")
            return

        # Check if the game has ended
        if self.state.phase == GamePhase.FINISHED:
            if set(self.state.word_to_guess) <= set(self.state.guesses):
                print("🎉 Congratulations! You've guessed the word:", self.state.word_to_guess)
            else:
                print("💀 Game Over! You've run out of attempts. The word was:", self.state.word_to_guess)
            return

        # Display the game progress
        remaining_attempts = self.max_attempts - len(self.state.incorrect_guesses)
        masked_word = ''.join(
            letter if letter in self.state.guesses else '_'
            for letter in self.state.word_to_guess
        )
        print("=== Hangman Game ===")
        print(f"Word to Guess: {masked_word}")
        print(f"Incorrect Guesses: {self.state.incorrect_guesses}")
        print(f"Remaining Attempts: {remaining_attempts}")
        print("=========================")
        self.print_hangman(len(self.state.incorrect_guesses))

    def print_hangman(self, incorrect_guess_count: int) -> None:
        """
        Prints the Hangman ASCII art based on the number of incorrect guesses.

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
        # Cap the stage index to the number available in `hangman_stages`
        stage_index = min(incorrect_guess_count, len(hangman_stages) - 1)
        print(hangman_stages[stage_index])

    def get_list_action(self) -> List[GuessLetterAction]:
        """
        Returns a list of available actions (letters that have not been guessed).

        Returns:
            List[GuessLetterAction]: A list of unguessed letters wrapped in GuessLetterAction objects.
        """
        alphabet = set("abcdefghijklmnopqrstuvwxyz")
        guessed_letters = set(self.state.guesses + self.state.incorrect_guesses)
        available_letters = alphabet - guessed_letters
        return [GuessLetterAction(letter) for letter in sorted(available_letters)]

    def apply_action(self, action: GuessLetterAction) -> None:
        """
        Applies a player's guess to the game.

        Args:
            action (GuessLetterAction): The guessed letter provided by the player.
        """
        if not self.state:
            print("Game state is not initialized.")
            return

        if self.state.phase != GamePhase.RUNNING:
            print("Actions cannot be applied when the game is not in the RUNNING phase.")
            return

        guessed_letter = action.letter.lower()

        if guessed_letter in self.state.guesses + self.state.incorrect_guesses:
            print(f"The letter '{guessed_letter}' has already been guessed.")
            return

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
        Returns the masked game state for a player, showing only guessed letters in the word.

        Args:
            idx_player (int): The index of the player (for multiplayer support).

        Returns:
            HangmanGameState: The masked state of the game visible to the player.
        """
        if not self.state:
            raise ValueError("Game state is not set.")

        masked_word = ' '.join(
            letter if letter.lower() in self.state.guesses else '_'
            for letter in self.state.word_to_guess
        )
        return HangmanGameState(
            word_to_guess=masked_word,
            phase=self.state.phase,
            guesses=self.state.guesses,
            incorrect_guesses=self.state.incorrect_guesses
        )


class RandomPlayer(Player):
    """
    A player who guesses letters randomly.
    """
    def select_action(self, state: HangmanGameState, actions: List[GuessLetterAction]) -> Optional[GuessLetterAction]:
        """
        Randomly selects the next action (letter guess).

        Args:
            state (HangmanGameState): The current state of the Hangman game.
            actions (List[GuessLetterAction]): A list of possible actions (guesses).

        Returns:
            Optional[GuessLetterAction]: The randomly selected letter, or None if no actions are available.
        """
        if not actions:
            print("No available actions to select from.")
            return None
        selected_action = random.choice(actions)
        print(f"RandomPlayer selected action: {selected_action.letter}")
        return selected_action


if __name__ == "__main__":
    game = Hangman()
    game_state = HangmanGameState(
        word_to_guess="DevOpsp".lower(),
        phase=GamePhase.RUNNING,
        guesses=[],
        incorrect_guesses=[]
    )
    game.set_state(game_state)
    game.print_state()

    while game.get_state().phase != GamePhase.FINISHED:
        actions = game.get_list_action()
        print("\nAvailable actions:", [action.letter for action in actions])
        guess = input("Enter your guess: ").lower()
        selected_action = next((action for action in actions if action.letter == guess), None)
        if selected_action:
            game.apply_action(selected_action)
            game.print_state()
        else:
            print(f"Invalid guess '{guess}'. Try again.")