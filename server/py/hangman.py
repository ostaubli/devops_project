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
    #add comment


class HangmanGameState:

    def __init__(self, word_to_guess: str, phase: GamePhase, guesses: List[str], incorrect_guesses: List[str]) -> None:
        self.word_to_guess = word_to_guess
        self.phase = phase
        self.guesses = guesses
        self.incorrect_guesses = incorrect_guesses


class Hangman(Game):

    def __init__(self) -> None:
        self.state: Optional[HangmanGameState] = None # Game state, initially None, set later via `set_state` as shown in `__main__`
        self.max_attempts = 8 # Remaining attempts (e.g., max 6 incorrect guesses allowed)

    def get_state(self) -> HangmanGameState:
        """ Get the complete, unmasked game state """
        return self.state 

    def set_state(self, state: HangmanGameState) -> None:
        # Update the game state
        """ Set the game to a given state """

        # Ensure the `state` parameter is explicitly passed and used
        if not state.word_to_guess:
            raise ValueError("The word to guess cannot be empty.")

        # Automatically initialize for SETUP phase
        if self.state is None:  # Check if this is the first time setting the state
            state.phase = GamePhase.SETUP
            state.guesses = []
            state.incorrect_guesses = []
        else:
            # Determine phase based on the current state
            if all(letter in state.guesses for letter in state.word_to_guess):
                state.phase = GamePhase.FINISHED  # All letters guessed correctly
            elif len(state.incorrect_guesses) >= self.max_attempts:
                state.phase = GamePhase.FINISHED  # Maximum incorrect guesses reached
            else:
                state.phase = GamePhase.RUNNING  # Game is in progress
        self.state = state

    def print_state(self) -> None:
        """ Print the current game state. """
        if not self.state:
            print("Game state is not initialized.")
            return

        remaining_attempts = self.max_attempts - len(self.state.incorrect_guesses)

        # Print game state
        print("=== Hangman Game Test ===")
        print(f"Word to Guess: {[letter for letter in self.state.word_to_guess]}")
        print(f"Incorrect Guesses: {self.state.incorrect_guesses}")
        print(f"Remaining Attempts: {remaining_attempts}")
        print("=========================")

             # Print the hangman drawing based on incorrect guesses
        self.print_hangman(len(self.state.incorrect_guesses))

    def print_hangman(self, incorrect_guess_count: int) -> None:
         """ Print the hangman drawing based on incorrect guesses """
         hangman_stages = [
             """
                ------
                |    |
                     |
                     |
                     |
                     |
                     |
                     |
               ========
             """,
             """
                ------
                |    |
                |    |
                     |
                     |
                     |
                     |
                     |
               ========
             """,
             """
                ------
                |    |
                |    |
                O    |
                     |
                     |
                     |
               ========
             """,
             """
                ------
                |    |
                |    |
                O    |
                |    |
                     |
                     |
               ========
             """,
             """
                ------
                |    |
                |    |
                O    |
               /|    |
                     |
                     |
               ========
             """,
             """
                ------
                |    |
                |    |
                O    |
               /|\\   |
                     |
                     |
               ========
             """,
             """
                ------
                |    |
                |    |
                O    |
               /|\\   |
               /     |
                     |
               ========
             """,
             """
                ------
                |    |
                |    |
                O    |
               /|\\   |
               / \\   |
                     |
               ========
             """,
             """
                ------
                |    |
                |    |
                O    |
               /|\\   |
               / \\   |
               [GAME OVER]
               ========
             """
         ]

         # Ensure we don't go out of bounds, use the last stage for incorrect guesses >= 8
         stage_index = min(incorrect_guess_count, len(hangman_stages) - 1)

         print(hangman_stages[stage_index])

    def get_list_action(self) -> List[GuessLetterAction]:
        """ Get a list of possible actions for the active player """
        # Define the alphabet
        alphabet = set("abcdefghijklmnopqrstuvwxyz")

        # Find unguessed letters
        guessed_letters = set(self.state.guesses + self.state.incorrect_guesses)
        available_letters = alphabet - guessed_letters

        # Return available letters as GuessLetterAction objects
        return [GuessLetterAction(letter) for letter in sorted(available_letters)]

    def apply_action(self, action: GuessLetterAction) -> None:
        """ Apply the given action to the game """

        if not self.state:
            print("Game state is not initialized.")
            return
        
        if self.state.phase != GamePhase.RUNNING:  # Ensure actions only occur in RUNNING phase
            print("Actions cannot be applied when the game is not in the RUNNING phase.")
            return

        guessed_letter = action.letter.lower()

         # Check if the guessed letter is valid
        if guessed_letter in self.state.guesses or guessed_letter in self.state.incorrect_guesses:
            print(f"The letter '{guessed_letter}' has already been guessed.")
            return
        
        # Check if the letter is in the word
        if guessed_letter in self.state.word_to_guess:
            print(f"Correct! The letter '{guessed_letter}' is in the word.")
            self.state.guesses.append(guessed_letter)
        else:
            print(f"Incorrect! The letter '{guessed_letter}' is not in the word.")
            self.state.incorrect_guesses.append(guessed_letter)
        
        # Check if the game has been won
        if all(letter in self.state.guesses for letter in self.state.word_to_guess):
            self.state.phase = GamePhase.FINISHED
            print("Congratulations! You've guessed the word:", self.state.word_to_guess)
        
        # Check if the game has been lost
        remaining_attempts = self.max_attempts - len(self.state.incorrect_guesses)
        if remaining_attempts <= 0:
            self.state.phase = GamePhase.FINISHED
            print("Game over! You've run out of attempts. The word was:", self.state.word_to_guess)


    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """ Get the masked state for the active player (player only sees the words which were guessed right)"""
        if not self.state:
            raise ValueError("Game state is not set.")
        # Create the masked word to hide unguessed letters
        masked_word = ' '.join(
            letter if letter.lower() in self.state.guesses else '_'
            for letter in self.state.word_to_guess
        )
        return HangmanGameState(
            word_to_guess=masked_word,
            phase=self.state.phase,
            guesses=self.state.guesses,
            incorrect_guesses=self.state.incorrect_guesses
        )


class RandomPlayer(Player):

    def select_action(self, state: HangmanGameState, actions: List[GuessLetterAction]) -> Optional[GuessLetterAction]:
        """ Given masked game state and possible actions, select the next action """
        if not actions:  # Check if the actions list is empty or None
            print("No available actions to select from.")
            return None

        # Randomly select an action from the list of available actions
        selected_action = random.choice(actions)
        print(f"RandomPlayer selected action: {selected_action.letter}")
        return selected_action



if __name__ == "__main__":

    # Initialize the Hangman game
    game = Hangman()

    # Set up a new game state
    game_state = HangmanGameState(
        word_to_guess="DevOps".lower(),  # Word to guess
        phase=GamePhase.RUNNING,         # Phase set to RUNNING
        guesses=[],                      # No correct guesses yet
        incorrect_guesses=[]             # No incorrect guesses yet
    )

    game.set_state(game_state)  # Initialize the game state

    game.print_state()
    # Start taking guesses in a loop until the game ends
    while game.get_state().phase != GamePhase.FINISHED:
        # Display available actions
        actions = game.get_list_action()
        print("\nAvailable actions:", [action.letter for action in actions])

        # Take input from the player
        guess = input("Enter your guess: ").lower()

        # Find the action matching the input
        selected_action = next((action for action in actions if action.letter == guess), None)

        if selected_action:
            game.apply_action(selected_action)
            game.print_state()  # Update and print game state after the guess
        else:
            print(f"Invalid guess '{guess}'. Try again.")

