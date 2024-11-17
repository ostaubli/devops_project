import string
from typing import List, Optional
import random
from enum import Enum
from server.py.game import Game, Player


class GuessLetterAction:
    """Class representing an action of guessing a letter in the Hangman game."""

    def __init__(self, letter: str) -> None:
        """
        Initialize a GuessLetterAction with the specified letter.
        """
        self.letter = letter

    def get_letter(self) -> str:
        """
        Retrieve the guessed letter.
        """
        return self.letter

    def is_valid_guess(self) -> bool:
        """
        Check if the guessed letter is valid (i.e., a single alphabetic character).
        """
        return len(self.letter) == 1 and self.letter.isalpha()


class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class HangmanGameState:
    """Class representing the state of a Hangman game."""

    def __init__(self, word_to_guess: str, phase: GamePhase,
                 guesses: List[str], incorrect_guesses: List[str]) -> None:
        """
        Initialize the Hangman game state.
        """
        self.word_to_guess = word_to_guess
        self.phase = phase
        self.guesses = guesses
        self.incorrect_guesses = incorrect_guesses

    def is_word_guessed(self) -> bool:
        """
        Determine if the word has been completely guessed.
        """
        return all(letter.upper() in (g.upper() for g in self.guesses) for letter in self.word_to_guess)

    def add_guess(self, letter: str) -> None:
        """
        Add a guessed letter to the list of guesses.
        """
        if letter not in self.guesses:
            self.guesses.append(letter)

class Hangman(Game):
    """ Hangman game implementation """

    HANGMAN_PICS = [r"""
    
                    """ ,
                    r"""
                    ____
                    |/    
                    |   
                    |    
                    |    
                    |    
                    |
                    |_____
                    """,
                    r"""
                      ____
                     |/    
                     |   (_)
                     |    
                     |    
                     |    
                     |
                     |_____
                     """,
                    r"""
                      ____
                     |/    
                     |   (_)
                     |    |
                     |    |    
                     |    
                     |
                     |_____
                     """,
                    r"""
                      ____
                     |/    
                     |   (_)
                     |   \|
                     |    |
                     |    
                     |
                     |_____
                     """,
                    r"""
                      ____
                     |/    
                     |   (_)
                     |   \|/
                     |    |
                     |    
                     |
                     |_____
                     """,
                    r"""
                      ____
                     |/    
                     |   (_)
                     |   \|/
                     |    |
                     |   / 
                     |
                     |_____
                     """,
                    r"""
                      ____
                     |/    
                     |   (_)
                     |   \|/
                     |    |
                     |   / \\
                     |
                     |_____
                     """,
                    r"""
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
        """Initialize the game with default values."""
        self.state = HangmanGameState(word_to_guess='', phase=GamePhase.SETUP, guesses=[], incorrect_guesses=[])

    def get_state(self) -> HangmanGameState:
        """Return the current game state."""
        return self.state

    def set_state(self, state: HangmanGameState) -> None:
        """Set the game to a given state."""
        self.state = state

    def print_state(self) -> None:
        """Print the current game state to the console."""
        display = [letter.upper() if letter.upper() in self.state.guesses
                   else '_' for letter in self.state.word_to_guess]
        print("Current word:", ' '.join(display))
        print("Incorrect guesses:", ', '.join(self.state.incorrect_guesses))
        print(self.HANGMAN_PICS[len(self.state.incorrect_guesses)])

    def get_list_action(self) -> List[GuessLetterAction]:
        """Get a list of possible actions for the active player."""
        return [GuessLetterAction(letter) for letter in string.ascii_uppercase
                if letter not in self.state.guesses]

    def apply_action(self, action: GuessLetterAction) -> None:
        """Apply the given action to the game."""
        letter = action.letter.upper()
        self.state.guesses.append(letter)
        if letter in self.state.word_to_guess.upper():
            print(f"Yes! {letter} is in the word.")
        else:
            print(f"No! {letter} is not in the word.")
            self.state.incorrect_guesses.append(letter)

        self.print_state()

        if all(l.upper() in (g.upper() for g in self.state.guesses) for l in self.state.word_to_guess):
            print("You've won!")
            self.state.phase = GamePhase.FINISHED
        elif len(self.state.incorrect_guesses) >= len(self.HANGMAN_PICS) - 1:
            print("Game over!")
            self.state.phase = GamePhase.FINISHED

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """Get the masked state for the active player."""
        word_to_guess_hidden = ''.join([letter if letter in self.state.guesses
                                        else '_' for letter in self.state.word_to_guess])
        return HangmanGameState(word_to_guess=word_to_guess_hidden,
                                phase=self.state.phase,
                                guesses=self.state.guesses,
                                incorrect_guesses=self.state.incorrect_guesses)


class RandomPlayer(Player):
    """ Random player that selects a random action from the list of possible actions """

    def select_action(self, state: HangmanGameState,
                      actions: List[GuessLetterAction]) -> Optional[GuessLetterAction]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None

    def get_available_actions(self, actions: List[GuessLetterAction]) -> List[str]:
        """
        Get the list of available actions as strings.
        """
        return [action.letter for action in actions]


if __name__ == "__main__":

    game = Hangman()
    game_state = HangmanGameState(word_to_guess='DevOps',
                                  phase=GamePhase.SETUP, guesses=[], incorrect_guesses=[])
    game.set_state(game_state)

    # # Example gameplay
    # game.state.phase = GamePhase.RUNNING
    # while game.get_state().phase == GamePhase.RUNNING:
    #     action = RandomPlayer().select_action(game.get_state(), game.get_list_action())
    #     if action:
    #         game.apply_action(action)
