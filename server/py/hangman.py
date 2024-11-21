from typing import List, Optional
import random
from enum import Enum
from game import Game, Player

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
        self.masked_word = ["_"]*len(word_to_guess)

class Hangman(Game):
    def __init__(self) -> None:
        """ Important: Game initialization also requires a set_state call to set the 'word_to_guess' """
        word_to_guess = input("Gib das zu erratende Wort ein: ").lower()
        initial_state = HangmanGameState(word_to_guess, GamePhase.SETUP, [], [])
        self.set_state(initial_state)
        self.state.phase = GamePhase.RUNNING

    def set_state(self, state: HangmanGameState) -> None:
        """ Set the game to a given state """
        self.state = G

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
        print(f"Status des Spiels ist: {self.state.phase}")

    def apply_action(self, action: GuessLetterAction) -> None:
        """ Applies the action (i.e. guesses a letter) to the game and checks if it's correct or not. """
        while len(self.state.guesses) < len(self.state.word_to_guess) and len(self.state.incorrect_guesses) < 6:
            print(f"Das zu erratende Wort ist: {self.state.masked_word}")

            letter = input("Gib einen Buchstaben ein: ").lower().strip()

            if len(letter) != 1 or not letter.isalpha():
                print("Falsche Eingabe, bitte gib nur einen einzelnen Buchstaben ein.")
                continue

            elif letter in self.state.guesses or letter in self.state.incorrect_guesses:
                print("Diesen Buchstaben hattest du schon, nimm einen anderen: ")

            elif letter in self.state.word_to_guess:
                self.state.guesses.append(letter)
                print("Richtig, der Buchstabe ist im gesuchten Wort enthalten")

                for i, char in enumerate(self.state.word_to_guess):
                    if char == letter:
                        self.state.masked_word[i] = letter

                if all(c != "_" for c in self.state.masked_word):
                    self.state.phase = GamePhase.FINISHED
                    print(f"Herzlichen Glückwunsch, du hast das Wort {self.state.word_to_guess} richtig erraten")
                    break
            else:
                self.state.incorrect_guesses.append(letter)
                print(f"Der Buchstabe {letter} ist nicht im gesuchten Wort enthalten")

                if len(self.state.incorrect_guesses) >=6:
                    self.state.phase = GamePhase.FINISHED
                    print(f"Leider verloren. Du hast das gesuchte Wort {self.state.word_to_guess} nicht erraten")
                    break

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        if self.state.phase != GamePhase.RUNNING:
            print("Das Spiel läuft gegenwärtig nicht")

        masked_word = ''.join([letter if letter in self.state.guesses else '_' for letter in self.state.word_to_guess])
        print(f"Das zu erratende Wort ist {masked_word}")

class RandomPlayer(Player):

    def select_action(self, state: HangmanGameState, actions: List[GuessLetterAction]) -> Optional[GuessLetterAction]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None

if __name__ == "__main__":
    game = Hangman()
    letter = input("Gib einen Buchstaben ein: ").lower().strip()
    game.apply_action(GuessLetterAction(letter))

