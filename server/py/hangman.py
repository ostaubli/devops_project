from typing import List, Optional
import random
from enum import Enum
from server.py.game import Game, Player


class GuessLetterAction:

    def __init__(self, letter: str) -> None:
        self.letter = letter

    def __str__(self):
        return str(self.letter)


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
        """ Important: Game initialization also requires a set_state call to set the 'word_to_guess' """
        self._state = None
        self._players = [RandomPlayer()]
        self._actions = [GuessLetterAction(chr(i)) for i in range(65, 91)]

    def get_state(self) -> HangmanGameState:
        """ Set the game to a given state """
        return self._state

    def set_state(self, state: HangmanGameState) -> None:
        """ Get the complete, unmasked game state """
        self._state = state

    def print_state(self) -> None:
        """ Print the current game state """

        # show the current correct guessed letters
        masked_word = ''.join(
            letter if letter.upper() in self._state.guesses else '_'
            for letter in self._state.word_to_guess
        )

        # print current status of the game
        print("=== Current Game State ===")
        print(f"Word to guess: {masked_word}")
        print(f"Guessed letters: {', '.join(self._state.guesses) if self._state.guesses else 'None'}")
        print(
            f"Incorrect guesses: {', '.join(self._state.incorrect_guesses) if self._state.incorrect_guesses else 'None'}")
        print(f"Game phase: {self._state.phase}")
        print("==========================")

    def get_list_action(self) -> List[GuessLetterAction]:
        """ Get a list of possible actions for the active player """
        return self._actions

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

    print(', '.join(map(str,game.get_list_action())))
    
