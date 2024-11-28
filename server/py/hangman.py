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
        self.word_to_guess = word_to_guess.upper()
        self.phase = phase
        self.guesses = guesses
        self.incorrect_guesses = incorrect_guesses


class Hangman(Game):

    def __init__(self) -> None:
        """ Important: Game initialization also requires a set_state call to set the 'word_to_guess'. """
        self.max_incorrect_guesses = 8
        self.state: Optional[HangmanGameState] = None

    def get_state(self) -> HangmanGameState:
        """ Set the game to a given state """
        return HangmanGameState(
            word_to_guess=self.state.word_to_guess,
            phase=self.state.phase,
            guesses=self.state.guesses,
            incorrect_guesses=self.state.incorrect_guesses
        )

    def set_state(self, state: HangmanGameState) -> None:
        """ Get the complete, unmasked game state """
        self.state = state
        self.state.phase = GamePhase.RUNNING

    def print_state(self) -> None:
        """ Print the current game state """
        masked_word = ''.join([c if c in self.state.guesses else '_' for c in self.state.word_to_guess])
        print(f"Word to guess: {masked_word}")
        print(f"Guesses: {', '.join(self.state.guesses)}")
        print(f"Incorrect guesses ({len(self.state.incorrect_guesses)}): {', '.join(self.state.incorrect_guesses)}")
        print(f"Remaining attempts: {self.max_incorrect_guesses - len(self.state.incorrect_guesses)}")
        print(f"Phase: {self.state.phase}")

    def get_list_action(self) -> List[GuessLetterAction]:
        """ Get a list of possible actions for the active player """
        # all possibilities
        alphabet = set("abcdefghijklmnopqrstuvwxyz".upper()) 

        # possibilities left
        guessed_alphabets = set(self.state.guesses + self.state.incorrect_guesses)
        available_alphabets = alphabet - guessed_alphabets

        return [GuessLetterAction(letter) for letter in sorted(available_alphabets)]

    def apply_action(self, action: GuessLetterAction) -> None:
        """ Apply the given action to the game """
        guess_letter = action.letter.upper()

        # Valid guess
        if guess_letter in (self.state.guesses + self.state.incorrect_guesses):
            print(f"The letter {guess_letter} was already guessed!!!")
            return None
        
        # Check if guess is correct
        if guess_letter in self.state.word_to_guess:
            self.state.guesses.append(guess_letter)
            print(f"Correct guess: {guess_letter}")
        else:
            self.state.incorrect_guesses.append(guess_letter)
            print(f"Incorrect guess: {guess_letter}")
        
        # Game end cases
        if all(letter in self.state.guesses for letter in self.state.word_to_guess):
            print("Congratulations! You've guessed the word!")
            self.state.phase = GamePhase.FINISHED
        elif len(self.state.incorrect_guesses) >= self.max_incorrect_guesses:
            print("Game Over! You have run out of attempts and hangman is complete.")
            print(f"The word was: {self.state.word_to_guess}")
            self.state.phase = GamePhase.FINISHED

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """
        Get the masked state for the active player.
        The word to guess is masked with underscores for unrevealed letters.
        """
        # Mask the word with underscores for unguessed letters
        masked_word = ''.join([c if c in self.state.guesses else '_' for c in self.state.word_to_guess])

        # Create a masked game state to return to the player
        return HangmanGameState(
            word_to_guess=masked_word,  # Return the masked version of the word
            phase=self.state.phase,
            guesses=self.state.guesses,
            incorrect_guesses=self.state.incorrect_guesses
        )



class RandomPlayer(Player):

    def select_action(self, state: HangmanGameState, actions: List[GuessLetterAction]) -> Optional[GuessLetterAction]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == "__main__":

    game = Hangman()
    secret_word = input("Enter the word to guess word: ").strip()
    game_state = HangmanGameState(word_to_guess=secret_word, phase=GamePhase.SETUP, guesses=[], incorrect_guesses=[])
    game.set_state(game_state)

    # Start guessing process
    while game.get_state().phase == GamePhase.RUNNING:
        game.print_state()
        print('\n')
        # Get available actions and pick a letter
        actions = game.get_list_action()
        guess_letter = input("Guess a letter: ").strip().lower()

        if len(guess_letter) != 1 or not guess_letter.isalpha():
            print("Please enter a single alphabet letter.")
            continue

        action = GuessLetterAction(guess_letter)
        game.apply_action(action)

    # Final game state
    game.print_state()