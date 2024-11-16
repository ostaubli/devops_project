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
        """ Get the game state """
        if self.state is None:
            raise ValueError("Game state has not been initialized. Call `set_state` first.")
        return self.state

    def set_state(self, state: HangmanGameState) -> None:
        """
        Set the game's state.
        Args:
            state (HangmanGameState): The state to initialize or update the game with.
        """
        # Ensure the `state` parameter is explicitly passed and used
        if not state.word_to_guess:
            raise ValueError("The word to guess cannot be empty.")

        # Automatically initialize for SETUP phase
        if self.state is None:  # Check if this is the first time setting the state
            state.phase = GamePhase.SETUP
            state.guesses = []
            state.incorrect_guesses = []

        # Update the game state
        self.state = state

    def print_state(self) -> None:
        """ Print the current game state """
        pass

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

    game = Hangman()
    game_state = HangmanGameState(word_to_guess='DevOps', phase=GamePhase.SETUP, guesses=[], incorrect_guesses=[])
    game.set_state(game_state)
    print("Game initialized successfully!")
    print(f"Word to guess: {game.state.word_to_guess}")
    print(f"Game phase: {game.state.phase}")



