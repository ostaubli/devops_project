from typing import List, Optional
import random
from enum import Enum
from server.py.game import Game, Player

# ASCII art for the hangman stages
HANGMAN_PICS = [
    '''
     +---+
     |    
     |    
     |    
    ===''', '''
     +---+
     |   O
     |    
     |    
    ===''', '''
     +---+
     |   O
     |   |
     |    
    ===''', '''
     +---+
     |   O
     |  /|
     |    
    ===''', '''
     +---+
     |   O
     |  /|\
     |    
    ===''', '''
     +---+
     |   O
     |  /|\
     |    \
    ===''', '''
     +---+
     |   O
     |  /|\
     |  / 
    ===''', '''
     +---+
     |   O
     |  /|\
     |  / \
    ==='''
]


class GuessLetterAction:

    def __init__(self, letter: str) -> None:
        if len(letter) != 1 or not letter.isalpha():
            raise ValueError("A guess must be a single alphabetic character.")
        self.letter = letter.lower()  # Ensure the letter is stored in lowercase

    def __repr__(self) -> str:
        return f"GuessLetterAction(letter='{self.letter}')"


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

    def display_state(self):
        """ Zeigt den aktuellen Spielzustand (Wort, falsche Buchstaben, Hangman-Bild) """
        # Das Wort wird angezeigt, wobei ungerratene Buchstaben durch "_" ersetzt werden
        word_display = ''.join([letter if letter in self.guesses else '_' for letter in self.word_to_guess])
        print(f"Word: {word_display}")  # Zeigt das Wort mit den erratenen Buchstaben
        print(f"Incorrect guesses: {', '.join(self.incorrect_guesses)}")  # Zeigt die falschen Buchstaben
        print(f"Hangman:\n{HANGMAN_PICS[len(self.incorrect_guesses)]}")  # Zeigt das entsprechende Hangman-Bild
        print()


class Hangman(Game):

    def __init__(self) -> None:
        """ Important: Game initialization also requires a set_state call to set the 'word_to_guess' """
        self.state: Optional[HangmanGameState] = None

    def get_state(self) -> HangmanGameState:
        """ Set the game to a given state """
        return self.state

    def set_state(self, state: HangmanGameState) -> None:
        """ Get the complete, unmasked game state """
        self.state = state

    def print_state(self) -> None:
        """ Print the current game state """
        if self.state:
            self.state.display_state()

    def get_list_action(self) -> List[GuessLetterAction]:
        """ Get a list of possible actions for the active player """
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        possible_guesses = [letter for letter in alphabet if letter not in self.state.guesses]
        return [GuessLetterAction(letter) for letter in possible_guesses]

    def apply_action(self, action: GuessLetterAction) -> None:
        """ Apply the given action to the game """
        if not self.state or self.state.phase == GamePhase.FINISHED:
            return
        if action.letter in self.state.word_to_guess:
            self.state.guesses.append(action.letter)
            if all(letter in self.state.guesses for letter in self.state.word_to_guess):
                self.state.phase = GamePhase.FINISHED
                print("\nCongratulations! You've guessed the word:", self.state.word_to_guess)
        else:
            self.state.incorrect_guesses.append(action.letter)
            if len(self.state.incorrect_guesses) == len(HANGMAN_PICS) - 1:
                self.state.phase = GamePhase.FINISHED
                print("\nGame Over! The word was:", self.state.word_to_guess)

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """ Get the masked state for the active player """
        word_display = ''.join([letter if letter in self.state.guesses else '_' for letter in self.state.word_to_guess])
        return HangmanGameState(
            word_to_guess=word_display,
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

    def setup_game():
        word_list = ['daniela', 'geraldine', 'liliana', 'laura']
        chosen_word = random.choice(word_list)
        game_state = HangmanGameState(word_to_guess=chosen_word, phase=GamePhase.SETUP, guesses=[], incorrect_guesses=[])
        game.set_state(game_state)
        game.state.phase = GamePhase.RUNNING


    # Setup the game
    setup_game()

    # Create a random player for the simulation
    player = RandomPlayer()

    # Start the game
    game.state.phase = GamePhase.RUNNING  # Transition to the running phase

    # Start the game loop
    while game.state.phase == GamePhase.RUNNING:
        game.print_state()  # Print the current state of the game
        actions = game.get_list_action()  # Get the list of possible actions
        action = player.select_action(game.state, actions)  # Select a random action

        if action:
            print(f"Player guesses: {action.letter}")  # Print the guessed letter
            game.apply_action(action)  # Apply the guessed letter

    # Once game is finished, print final message
    if game.state.phase == GamePhase.FINISHED:
        print(f"Game Over! The word was: {game.state.word_to_guess}")