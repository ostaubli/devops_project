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
    HANGMAN_PICS = [ """ 
____
|/   |
|   
|    
|    
|    
|
|_____
""",
"""
 ____
|/   |
|   (_)
|    
|    
|    
|
|_____
""",
"""
 ____
|/   |
|   (_)
|    |
|    |    
|    
|
|_____
""",
"""
 ____
|/   |
|   (_)
|   \|
|    |
|    
|
|_____
""",
"""
 ____
|/   |
|   (_)
|   \|/
|    |
|    
|
|_____
""",
"""
 ____
|/   |
|   (_)
|   \|/
|    |
|   / 
|
|_____
""",
"""
 ____
|/   |
|   (_)
|   \|/
|    |
|   / \\
|
|_____
""",
"""
 ____
|/   |
|   (_)
|   /|\\
|    |
|   | |
|
|_____
"""]
    def __init__(self) -> None:
        """ Important: Game initialization also requires a set_state call to set the 'word_to_guess' """
        initial_state = HangmanGameState(
            word_to_guess=random.choice(["PYTHON", "HANGMAN", "DEVELOPER", "CHALLENGE"]),
            phase=GamePhase.SETUP,
            guesses=[],
            incorrect_guesses=[]
        )
        self.set_state(initial_state)

    def get_state(self) -> HangmanGameState:
        """ Set the game to a given state """
        return self.state

    def set_state(self, state: HangmanGameState) -> None:
        """ Get the complete, unmasked game state """
        self.state = state
        if self.state.phase == GamePhase.SETUP:
            self.state.phase = GamePhase.RUNNING

    def print_state(self) -> None:
        """ Print the current game state """
        display = [letter if letter in self.state.guesses else '_' for letter in self.state.word_to_guess]
        print("Current word:", ' '.join(display))
        print("Incorrect guesses:", ', '.join(self.state.incorrect_guesses))
        print(self.HANGMAN_PICS[len(self.state.incorrect_guesses)])

    def get_list_action(self) -> List[GuessLetterAction]:
        """ Get a list of possible actions for the active player """
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        return [GuessLetterAction(letter) for letter in alphabet if letter not in self.state.guesses]

    def apply_action(self, action: GuessLetterAction) -> None:
        """ Apply the given action to the game """
        letter = action.letter.upper()
        self.state.guesses.append(letter)
        if letter in self.state.word_to_guess:
            print(f"Yes! {letter} is in the word.")
        else:
            print(f"No! {letter} is not in the word.")
            self.state.incorrect_guesses.append(letter)

        # Check game status
        if all(l in self.state.guesses for l in self.state.word_to_guess):
            self.state.phase = GamePhase.FINISHED
            print("You've won!")
            return
        # elif len(self.state.incorrect_guesses) >= len(self.HANGMAN_PICS) - 1:
        elif len(self.state.incorrect_guesses) >= 8:
        
            self.state.phase = GamePhase.FINISHED
            print("Game over!")
            return

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

    # Example gameplay
    while game.get_state().phase == GamePhase.RUNNING:
        action = RandomPlayer().select_action(game.get_state(), game.get_list_action())
        if action:
            game.apply_action(action)
            if game.get_state().phase == GamePhase.RUNNING:
                game.print_state()
            