from typing import List, Optional
import random
from enum import Enum
from server.py.game import Game, Player
import string


class GuessLetterAction:

    def __init__(self, letter: str) -> None:
        self.letter = letter


class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class HangmanGameState:

    def __init__(self, word_to_guess: str, phase: GamePhase, guesses: List[str], incorrect_guesses: List[str]) -> None:
        self.word_to_guess = word_to_guess.lower()
        self.phase = phase
        self.guesses = guesses
        self.incorrect_guesses = incorrect_guesses


class Hangman(Game):

    def __init__(self) -> None:
        """ Important: Game initialization also requires a set_state call to set the 'word_to_guess' """
        self.state: HangmanGameState

        pass

    def get_state(self) -> HangmanGameState:
        """ Get the complete, unmasked game state """
        pass

    def set_state(self, state: HangmanGameState) -> None:
        """ Set the game to a given state """
        pass

    def print_state(self) -> None:
        """ Print the current game state """
        if self.state:
            print("Word:" , ''.join([char if char in self.guesses else '_' for char in self.word_to_guess]))
            print(f"Guesses: {', '.join(self.state.guesses)}")



    def get_list_action(self) -> List[GuessLetterAction]:
        """ Get a list of possible actions for the active player """

        # check if the game state is set or not - if not set return only an empty list
        if not self.state or not self.state.word_to_guess:
            return []
        
        # now get all letters from the alphabet to see all possible guesses
        all_letters = set(string.ascii_lowercase)

        # now get all guessed letters 
        guessed_letters = set(self.state.guesses)

        # now filter out all the guessed letters and get a sset with all letter that are remaining
        avlb_letters = all_letters - guessed_letters

        return [GuessLetterAction(letter) for letter in sorted(avlb_letters)]




    def apply_action(self, action: GuessLetterAction) -> None:
        """ Apply the given action to the game """
        
        # first check whether the game is running or not - again through the state
        if not self.state or self.state.phase != GamePhase.RUNNING:
            print("The game is currently not running - no actions can be applied.")
            return
        
        # define the letter already guessed - make sure lowercase
        guessed_letter = action.letter.lower()
        
        # check whether the letter was already guessed (whether there has been an attempt to guess this letter)
        if guessed_letter in self.state.guesses or guessed_letter in self.state.incorrect_guesses:
            print("The letter", guessed_letter, "has been already guessed.")
            return
        
        # add the letter to the list of guessed letters
        self.state.guesses.append(guessed_letter)

        # check if the guessed letter is in the word
        if guessed_letter in self.state.word_to_guess:
            print("Correct guess.")
        else:
            print("Incorrect guess")
            self.state.incorrect_guesses.append(guessed_letter)
        
        # check if the game is won - the word is guessed
        if all(char in self.state.guesses for char in self.state.word_to_guess):
            print("THe word has been guessed!")
            self.state.phase = GamePhase.FINISHED

        # set a maximum number of guessed in order to finish the game faster
        max_number_of_guesses = 5

        if len(self.state.incorrect_guesses) >= max_number_of_guesses:
            print("You have reached the maximum number of guesses. You therefore lose the game.")
            print(f"The word to guess was {self.state.word_to_guess}")


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
