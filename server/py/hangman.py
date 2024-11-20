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

    def __init__(self, word_to_guess: str = "") -> None:
        """ Important: Game initialization also requires a set_state call to set the 'word_to_guess'. """
        self.word_to_guess = word_to_guess.lower()
        self.guesses = []
        self.incorrect_guesses = []
        self.phase = GamePhase.SETUP
        self.max_incorrect_guesses = 8

    def get_state(self) -> HangmanGameState:
        """ Set the game to a given state """
        return HangmanGameState(
            word_to_guess=self.word_to_guess,
            phase=self.phase,
            guesses=self.guesses,
            incorrect_guesses=self.incorrect_guesses
        )

    self.phase = GamePhase.SETUP if word_to_guess else GamePhase.FINISHED
    def set_state(self, state: HangmanGameState) -> None:
        """ Get the complete, unmasked game state """
        pass

    def print_state(self) -> None:
        """ Print the current game state """
        masked_word = ''.join([c if c in self.guesses else '_' for c in self.word_to_guess])
        print(f"Word to guess: {masked_word}")
        print(f"Guesses: {', '.join(self.guesses)}")
        print(f"Incorrect guesses ({len(self.incorrect_guesses)}): {', '.join(self.incorrect_guesses)}")
        print(f"Remaining attempts: {self.max_incorrect_guesses - len(self.incorrect_guesses)}")
        print(f"Phase: {self.phase}")

    def get_list_action(self) -> List[GuessLetterAction]:
        """ Get a list of possible actions for the active player """
        # all possibilities
        alphabet = set("abcdefghijklmnopqrstuvwxyz") 

        # possibilities left
        guessed_alphabets = set(self.guesses + self.incorrect_guesses)
        available_alphabets = alphabet - guessed_alphabets

        return [GuessLetterAction(letter) for letter in sorted(available_alphabets)]

    def apply_action(self, action: GuessLetterAction) -> None:
        """ Apply the given action to the game """
        guess_letter = action.letter

        # Valid guess
        if guess_letter in (self.guesses + self.incorrect_guesses):
            print(f"The letter {guess_letter} was already guessed!!!")
            return None
        
        # Check if guess is correct
        if guess_letter in self.word_to_guess:
            self.guesses.append(guess_letter)
            print(f"Correct guess: {guess_letter}")
        else:
            self.incorrect_guesses.append(guess_letter)
            print(f"Incorrect guess: {guess_letter}")
        
        # Game end cases
        if all(letter in self.guesses for letter in self.word_to_guess):
            print("Congratulations! You've guessed the word!")
            self.phase = GamePhase.FINISHED
        elif len(self.incorrect_guesses) >= self.max_incorrect_guesses:
            print("Game Over! You have run out of attempts and hangman is complete.")
            print(f"The word was: {self.word_to_guess}")
            self.phase = GamePhase.FINISHED

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """
        Get the masked state for the active player.
        The word to guess is masked with underscores for unrevealed letters.
        """
        # Mask the word with underscores for unguessed letters
        masked_word = ''.join([c if c in self.guesses else '_' for c in self.word_to_guess])

        # Create a masked game state to return to the player
        return HangmanGameState(
            word_to_guess=masked_word,  # Return the masked version of the word
            phase=self.phase,
            guesses=self.guesses,
            incorrect_guesses=self.incorrect_guesses
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
