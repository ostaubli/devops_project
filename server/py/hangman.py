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
        """ Important: Game initialization also requires a set_state call to set the 'word_to_guess' """
        word_to_guess = input("Gib ein Wort ein").lower()
        initial_state = HangmanGameState(word_to_guess, GamePhase.SETUP, [], [])
        self.set_state(initial_state)

    def set_state(self, state: HangmanGameState) -> None:
        """ Set the game to a given state """
        self.state = state

    def get_state(self) -> HangmanGameState:
        """ Set the game to a given state """
        return self.state

    def print_state(self) -> None:
        """ Print the current game state """
        print(self.state)

    def get_list_action(self) -> List[GuessLetterAction]:
        """ Get a list of possible actions for the active player """
        guessed_letters = self.state.guesses + self.state.incorrect_guesses
        available_letters = [letter for letter in "abcdefghijklmnopqrstuvwxyz" if letter not in guessed_letters]
        action = [GuessLetterAction(letter) for letter in available_letters]
        print(f"Du kannst aus folgenden Buchstaben raten: {available_letters}")
        print(f"Diese Buchstaben hast du bereits verbraucht: {guessed_letters}")
        print(f"Status des Spiels ist:{self.state.phase}")

    def apply_action(self, action: GuessLetterAction) -> None:
        if self.state.phase == GamePhase.RUNNING:
            letter = input("Gib einen Buchstaben ein").lower()

            if letter in self.state.guesses:
                print("Diesen Buchstaben hattest du bereits. Nimm einen anderen")

            elif letter in self.state.word_to_guess:
                self.state.guesses.append(letter)
                print(f"Richtig, der Buchstabe ist im {self.state.word_to_guess} enthalten")
            else:
                self.state.incorrect_guesses.append(letter)
                print(f"Falsch, der Buchstabe ist nicht im {self.state.word_to_guess} enthalten")


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
