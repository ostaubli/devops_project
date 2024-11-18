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
        self.max_attempts = 8 # Remaining attempts (e.g., max 6 incorrect guesses allowed)
        """ Important: Game initialization also requires a set_state call to set the 'word_to_guess' """

    def get_state(self) -> HangmanGameState:
        """ Get the complete, unmasked game state """
        return self.state 

    def set_state(self, state: HangmanGameState) -> None:
        # Update the game state
        """ Set the game to a given state """

        # Ensure the `state` parameter is explicitly passed and used
        if not state.word_to_guess:
            raise ValueError("The word to guess cannot be empty.")

        # Automatically initialize for SETUP phase
        if self.state is None:  # Check if this is the first time setting the state
            state.phase = GamePhase.SETUP
            state.guesses = []
            state.incorrect_guesses = []
        else:
        # Determine phase based on the current state
        if all(letter in state.guesses for letter in state.word_to_guess):
            state.phase = GamePhase.FINISHED  # All letters guessed correctly
        elif len(state.incorrect_guesses) >= self.max_attempts:
            state.phase = GamePhase.FINISHED  # Maximum incorrect guesses reached
        else:
            state.phase = GamePhase.RUNNING  # Game is in progress
        self.state 

    def print_state(self) -> None:
        """ Print the current game state. """
        if not self.state:
            print("Game state is not initialized.")
            return

        remaining_attempts = self.max_attempts - len(self.state.incorrect_guesses)

        # Print game state
        print("=== Hangman Game Test ===")
        print(f"Word to Guess: {[letter for letter in self.state.word_to_guess]}")
        print(f"Incorrect Guesses: {self.state.incorrect_guesses}")
        print(f"Remaining Attempts: {remaining_attempts}")
        print("=========================")

    def get_list_action(self) -> List[GuessLetterAction]:
        """ Get a list of possible actions for the active player """
        # Define the alphabet
        alphabet = set("abcdefghijklmnopqrstuvwxyz")

        # Find unguessed letters
        guessed_letters = set(self.state.guesses + self.state.incorrect_guesses)
        available_letters = alphabet - guessed_letters

        # Return available letters as GuessLetterAction objects
        return [GuessLetterAction(letter) for letter in sorted(available_letters)]

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
<<<<<<< HEAD
    game_state = HangmanGameState(word_to_guess='DevOps', phase=GamePhase.SETUP, guesses=[], incorrect_guesses=[])
    game.set_state(game_state)
    print("Game initialized successfully!")
    print(f"Word to guess: {game.state.word_to_guess}")
    print(f"Game phase: {game.state.phase}")



=======

    # Set up a new game state
    game_state = HangmanGameState(
        word_to_guess="DevOps".lower(),  # Word to guess
        phase=GamePhase.RUNNING,         # Phase set to RUNNING
        guesses=[],                      # No correct guesses yet
        incorrect_guesses=[]             # No incorrect guesses yet
    )
    game.set_state(game_state)  # Initialize the game state

    game.print_state()
    print(game.state)
    # Display available actions
    actions = game.get_list_action()
    print("\nAvailable actions:", [action.letter for action in actions])
>>>>>>> 819b563da575938209c4676382346b6ebf4a20a3
