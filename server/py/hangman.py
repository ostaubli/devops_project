from typing import List, Optional, Type
import random
from enum import Enum
from pydantic import BaseModel
import string
from pydantic.v1 import validator
from server.py.game import Game, Player


class GuessLetterAction(BaseModel):
    letter: str

    @validator('letter')
    def validate_letter(cls, v):
        if v.upper() not in string.ascii_uppercase:
            raise ValueError("you have to insert a letter")
        return v

class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished

class HangmanGameState (BaseModel):
    word_to_guess: str
    phase: GamePhase
    guesses: List[str]
    incorrect_guesses: List[str]

    @validator("word_to_guess")
    def validate_word_to_guess(cls, v):
        if not v.isalpha():
            raise ValueError("The word go guess must contain only letters")
        return v

class Hangman(Game):
    def __init__(self) -> None:
        """ Important: Game initialization also requires a set_state call to set the 'word_to_guess' """
        self.state = None

    def set_state(self, state: HangmanGameState) -> None:
        """ Set the game to a given state """
        self.state = state

    def get_state(self) -> Type[HangmanGameState]:
        """ Set the game to a given state """
        return self.state

    def print_state(self) -> None:
        """ Print the current game state """
        print(f"Korrekt erratene Buchstaben {self.state.guesses}")
        print(f"Nicht korrekt erratene Buchstaben {self.state.incorrect_guesses}")
        print(f"Verfügbare Versuche {7 - len(self.state.incorrect_guesses)}")

# List[GuessLetterAction] ist deine Typisierung der Rückgabewerte der Methode. Das bedeutet, dass die Methode eine Liste
# von GuessLetterAction-Objekten zurückgibt.
    def get_list_action(self) -> List[GuessLetterAction]:
        """ Get a list of possible actions for the active player """
        all_letters = set(chr(i) for i in range(ord("a"), ord("z") + 1))
        remaining_letters = all_letters - set(self.state.guesses)
        actions = [GuessLetterAction(letter) for letter in sorted(remaining_letters)]
        return actions

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
