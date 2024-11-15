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
        self.state = None

    def get_state(self) -> HangmanGameState:
        """ Return the complete, unmasked game state """
        return self.state

    def set_state(self, state: HangmanGameState) -> None:
        """ Initialize the game state with the provided word and set phase to RUNNING """
        self.state = state
        self.state.phase = GamePhase.RUNNING

    def print_state(self) -> None:
        """ Print the current game state with masked word showing correctly guessed letters """
        # Mask word, showing only letters that have been correctly guessed
        masked_word = ''.join(
            [letter if letter.upper() in self.state.guesses else '_' for letter in self.state.word_to_guess]
        )
        print(f"Word: {masked_word}")
        print(f"Guesses: {', '.join(self.state.guesses)}")
        print(f"Incorrect Guesses: {', '.join(self.state.incorrect_guesses)}")

    def get_list_action(self) -> List[GuessLetterAction]:
        """ Generate a list of actions with all unused letters as possible guesses """
        all_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        return [
            GuessLetterAction(letter) for letter in all_letters
            if letter not in self.state.guesses and letter not in self.state.incorrect_guesses
        ]

    def apply_action(self, action: GuessLetterAction) -> None:
        """ Apply the guessed letter to the game state and update phase if the game is won or lost """
        letter = action.letter.upper()

        # Check if the letter is in the word
        if letter in self.state.word_to_guess.upper():
            if letter not in self.state.guesses:
                self.state.guesses.append(letter)
        else:
            if letter not in self.state.incorrect_guesses:
                self.state.incorrect_guesses.append(letter)

        # Check for win condition
        if all(letter.upper() in self.state.guesses for letter in self.state.word_to_guess):
            self.state.phase = GamePhase.FINISHED
            print("Congratulations, you've guessed the word!")
        elif len(self.state.incorrect_guesses) >= len(self.state.word_to_guess): # dynamic word length
            self.state.phase = GamePhase.FINISHED
            print("Game over! Too many incorrect guesses.")
            print(f"The correct word was: {self.state.word_to_guess}")

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """ Get the masked state for the player """
        return self.state


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

    while game.get_state().phase == GamePhase.RUNNING:
        game.print_state()
        actions = game.get_list_action()
        player = RandomPlayer()
        action = player.select_action(game.get_state(), actions)
        if action:
            game.apply_action(action)
        else:
            break
    game.print_state()