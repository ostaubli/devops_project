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
        self.state = Optional[HangmanGameState] = None


    def get_state(self) -> HangmanGameState:
        """ Set the game to a given state """
        pass

    def set_state(self, state: HangmanGameState) -> None:
        """ Get the complete, unmasked game state """
        pass

    def print_state(self) -> None:
        """ Print the current game state """
        pass

    def get_list_action(self) -> List[GuessLetterAction]:
        """ Get a list of possible actions for the active player """
        if self.state and self.state.phase == GamePhase.RUNNING:
            guessed_letters = set(self.state.guesses)
            actions = []
            for i in range(ord('a'), ord('z') + 1):  # Loop through ASCII values of 'a' to 'z'
                letter = chr(i)  # Convert ASCII value to a character
                if letter not in guessed_letters:  # Check if the letter has not been guessed
                    actions.append(GuessLetterAction(letter))  # Add the action to the list
            return actions
        return []


    def apply_action(self, action: GuessLetterAction) -> None:
        if self.state and self.state.phase == GamePhase.RUNNING:
            letter = action.letter.lower()
            self.state.guesses.append(letter)
            if letter not in self.state.word_to_guess.lower():
                self.state.incorrect_guesses.append(letter)

            # Check if the game is finished
            word_set = set(self.state.word_to_guess.lower())
            guessed_set = set(self.state.guesses)
            if word_set.issubset(guessed_set):
                self.state.phase = GamePhase.FINISHED
                print("Congratulations! You've guessed the word.")
            elif len(self.state.incorrect_guesses) >= 6:  # Limit for incorrect guesses
                self.state.phase = GamePhase.FINISHED
                print(f"Game Over! The word was: {self.state.word_to_guess}")


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

    random_player = RandomPlayer()  # Create an instance of RandomPlayer

    # Main gameplay loop
    while game.state.phase == GamePhase.RUNNING:
        game.print_state()  # Print the current game state
        actions = game.get_list_action()  # Get all possible actions for the player

        # RandomPlayer selects an action
        action = random_player.select_action(game.get_state(), actions)
        if action:
            print(f"RandomPlayer guesses: {action.letter}")
            game.apply_action(action)  # Apply the chosen action to the game
        else:
            print("No more possible actions.")
            break