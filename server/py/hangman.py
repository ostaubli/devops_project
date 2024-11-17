from typing import List, Optional
import random
from enum import Enum
from server.py.game import Game, Player


class GuessLetterAction:

    def __init__(self, letter: str) -> None:
        self.letter = letter


class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class HangmanGameState:

    def __init__(self, word_to_guess: str, phase: GamePhase, guesses: List[str], incorrect_guesses: List[str]) -> None:
        self.word_to_guess = word_to_guess
        self.phase = phase
        self.guesses = guesses
        self.incorrect_guesses = incorrect_guesses


class Hangman(Game):

    def __init__(self) -> None:
        self.state: Optional[HangmanGameState] = None # Game state, initially None, set later via `set_state` as shown in `__main__`
        """ Important: Game initialization also requires a set_state call to set the 'word_to_guess' """

    def get_state(self) -> HangmanGameState:
        """ Set the game to a given state """
        return self.state 

    def set_state(self, state: HangmanGameState) -> None:
        """ Get the complete, unmasked game state """
        self.state = state

    def print_state(self) -> None:
        """ Print the current game state. """
        if not self.state:
            print("Game state is not initialized.")
            return

        # Remaining attempts (e.g., max 6 incorrect guesses allowed)
        max_attempts = 6
        remaining_attempts = max_attempts - len(self.state.incorrect_guesses)

        # Print game state
        print("=== Hangman Game Test ===")
        print(f"Word to Guess: {[letter for letter in self.state.word_to_guess]}")
        print(f"Incorrect Guesses: {self.state.incorrect_guesses}")
        print(f"Remaining Attempts: {remaining_attempts}")
        print("=========================")

    def get_list_action(self) -> List[GuessLetterAction]:
        """ Get a list of possible actions for the active player """
        pass

    def apply_action(self, action: GuessLetterAction) -> None:
        """ Apply the given action to the game """
        pass

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        pass


class RandomPlayer(Player):

    def select_action(self, state: HangmanGameState, actions: List[GuessLetterAction]) -> Optional[GuessLetterAction]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == "__main__":

    # Initialize the Hangman game
    game = Hangman()

    # Set up a new game state
    game_state = HangmanGameState(
        word_to_guess="DevOps",
        phase=GamePhase.RUNNING,
        guesses=["D", "e", "p"],
        incorrect_guesses=["X", "Z"]
    )
    game.set_state(game_state)

    game.print_state()
