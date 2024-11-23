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
        self.state = None

    def get_state(self) -> HangmanGameState:
        """ Set the game to a given state """
        return self.state

    def set_state(self, state: HangmanGameState) -> None:
        """ Get the complete, unmasked game state """
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
    wrong_guesses = 8

    # Initialise Hangman game and state
    game = Hangman()
    game_state = HangmanGameState(word_to_guess='DevOps'.lower(), phase=GamePhase.SETUP, guesses=[], incorrect_guesses=[])
    game.set_state(game_state)

    # Create the display word
    display_word = ["_" for _ in game_state.word_to_guess]

    # Main game loop
    while len(game_state.incorrect_guesses) < wrong_guesses:
        print("Word: ", " ".join(display_word))
        print(f"Incorrect guesses left: {wrong_guesses - len(game_state.incorrect_guesses)}")
        print(f"Guessed letters: {', '.join(sorted(game_state.guesses + game_state.incorrect_guesses))}")
    
        # Get user input
        guess = input("Guess a letter: ").lower()

        # Check if the guess is valid
        if guess in game_state.guesses or guess in game_state.incorrect_guesses:
            print(f"You already guessed '{guess}'. Try a different letter.")
            continue

        # If the guess is right
        if guess in game_state.word_to_guess:
            for i, char in enumerate(game_state.word_to_guess):
                if char.lower() == guess:
                    display_word[i] = char
            game_state.guesses.append(guess)
        else:
            game_state.incorrect_guesses.append(guess)
            print(f"Wrong guess! You have {wrong_guesses - len(game_state.incorrect_guesses)} guesses left.")

        # Check if player has guessed the full word
        if "_" not in display_word:
            print(f"Congratulations! You have guessed the word: {game_state.word_to_guess}")
            break
    
        # Check if the player has reached maximum guesses  
        if len(game_state.incorrect_guesses) == wrong_guesses:
            print(f"You have lost the game! The word was: {game_state.word_to_guess}")