from typing import List, Optional
import random
import string
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
        self.word_to_guess = word_to_guess.upper()
        self.phase = phase
        self.guesses = [guess.upper() for guess in guesses]
        self.incorrect_guesses = [incorrect.upper() for incorrect in incorrect_guesses]


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
        for letter in state.guesses:
            if letter not in state.word_to_guess.upper():
                state.incorrect_guesses.append(letter.upper())

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
        return [a for a in self._actions if
                a.letter not in self._state.guesses and a.letter not in self._state.incorrect_guesses]

    def apply_action(self, action: GuessLetterAction) -> None:
        """ Apply the given action to the game """
        guessed_letter = action.letter.upper()  # Ensure the letter is in uppercase
        state = self._state

        # Check if letter is already guessed
        if guessed_letter in state.guesses or guessed_letter in state.incorrect_guesses:
            print(f"The letter '{guessed_letter}' has already been guessed.")
            return

        # Check if the letter is in the word and update the game state accordingly
        if guessed_letter in state.word_to_guess.upper():  # Case-insensitive check for the word
            state.guesses.append(guessed_letter)  # Add guessed letter to guesses (as uppercase)
            print(f"Correct! The letter '{guessed_letter}' is in the word.")
        else:
            state.incorrect_guesses.append(guessed_letter)  # Add to incorrect guesses (as uppercase)
            print(f"Incorrect! The letter '{guessed_letter}' is not in the word.")

        # Remove the guessed letter from the action list
        self._actions = [a for a in self._actions if a.letter != guessed_letter]

        # Check if game should be finished based on wrong guesses or revealed word
        if len(state.incorrect_guesses) >= 8:
            state.phase = GamePhase.FINISHED
            print("Game over! Too many incorrect guesses.")
        elif '_' not in (c if c.upper() in state.guesses else '_' for c in state.word_to_guess):
            state.phase = GamePhase.FINISHED
            print("Congratulations! You have finished the game.")

        # Ensure only unused capital letters remain in the action list
        self._actions = [a for a in self._actions if
                         a.letter not in state.guesses and a.letter not in state.incorrect_guesses]

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        masked_word = ''.join(
            letter if letter.upper() in self._state.guesses else '_'
            for letter in self._state.word_to_guess
        )

        return HangmanGameState(
            word_to_guess=masked_word,
            phase=self._state.phase,
            guesses=self._state.guesses,
            incorrect_guesses=self._state.incorrect_guesses
        )

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

    # Schleife für die Eingabe von Aktionen
    while game.get_state().phase != GamePhase.FINISHED:
        # Ausgabe der möglichen Aktionen
        actions = game.get_list_action()
        print("Mögliche Aktionen:", ', '.join(map(str, actions)))

        # Frage nach dem nächsten Buchstaben
        letter = input("Bitte gib einen Buchstaben ein (oder 'exit' zum Beenden): ").upper()

        # Beende das Spiel, wenn der Benutzer 'exit' eingibt
        if letter == 'EXIT':
            print("Spiel wird beendet.")
            break

        # Stelle sicher, dass der eingegebene Buchstabe gültig ist (A bis Z)
        if len(letter) == 1 and letter.isalpha() and letter in string.ascii_uppercase:
            action = GuessLetterAction(letter=letter)
            game.apply_action(action)  # Wende die Aktion an
            game.print_state()  # Nur nach einer gültigen Aktion den Status drucken
        else:
            print("Ungültige Eingabe. Bitte einen einzelnen Buchstaben (A-Z) eingeben.")

    # Zeige den finalen Zustand des Spiels
    if game.get_state().phase == GamePhase.FINISHED:
        game.print_state()
